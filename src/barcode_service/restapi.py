import asyncio
import logging
import pathlib

import uvicorn
from fastapi import FastAPI, HTTPException, Path
from fastapi.responses import RedirectResponse

from barcode_service.barcodereader import BarcodeReader
from barcode_service.default_values import (
    DEFAULT_REST_API_HOST, DEFAULT_REST_API_MAX_CONCURRENT_REQUESTS,
    DEFAULT_REST_API_PORT)
from barcode_service.processing_exceptions import ScanningFailureException
from barcode_service.service_data import Barcode
from barcode_service.synchronization import ShutDownSignal
from barcode_service.version import SERVICE_VERSION

_log = logging.getLogger(__name__)


def start_and_wait_for_rest_api(conf, log_config, shutdown_signal: ShutDownSignal, faxes_location: pathlib.Path, barcode_reader: BarcodeReader):
    async def run_server(app, host, port):
        config = uvicorn.Config(host=host, port=port, app=app, lifespan="on", loop="asyncio", http="auto", limit_concurrency=DEFAULT_REST_API_MAX_CONCURRENT_REQUESTS, log_config=log_config)
        server = uvicorn.Server(config)
        await server.serve()

    host = conf["restapi"].get("host", DEFAULT_REST_API_HOST)
    port = conf["restapi"].get("port", DEFAULT_REST_API_PORT)
    app = FastAPI(title='Barcode Service API', description=f"This is the Barcode Service Rest API v{SERVICE_VERSION}")

    @app.get("/v1/barcodes/{subscriber_id}/{direction}/{fax_id}")
    async def get_barcodes(
        subscriber_id: str = Path(regex=r"\w+", min_length=1, example="06xGIVUxQ7OXorsZzt2WPw"),
        direction: str = Path(regex=r"(^in$)|(^out$)", min_length=2, max_length=3, example="in"),
        fax_id: str = Path(regex=r"[\da-fA-F]{32}", min_length=32, max_length=32, example="00112233445566778899aabbccddeeff")
    ) -> list[Barcode]:
        file_location = faxes_location / subscriber_id / direction / f"{fax_id}.tif"
        if not file_location.exists():
            raise HTTPException(status_code=404, detail=f"Resource [{subscriber_id}/{direction}/{fax_id}] does not exist")
        try:
            return list(barcode for barcode in barcode_reader.read_barcode(file_location))
        except ScanningFailureException as ex:
            raise HTTPException(status_code=503, detail=str(ex)) from ex
        except Exception as ex:
            raise HTTPException(status_code=500, detail=str(ex)) from ex

    @app.get("/", include_in_schema=False)
    async def docs_redirect():
        return RedirectResponse(url='/docs')

    @app.on_event("shutdown")
    def shutdown_event():
        shutdown_signal.send_signal()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_server(app, host, port))
    finally:
        loop.close()
    _log.info("REST API Terminated")
