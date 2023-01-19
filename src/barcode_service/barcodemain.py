# coding=utf-8
import logging
import logging.config
import os
import sys
import threading
from importlib.resources import open_text as open_resource_text
from pathlib import Path
from signal import SIGINT, SIGTERM
from signal import signal as register_signal
from threading import ExceptHookArgs, Thread
from types import TracebackType
from typing import List, Type, Union

from barcode_service import \
    __version__ as SERVICE_VERSION  # pylint: disable=cyclic-import
from barcode_service.barcodereader import BarcodeReader
from barcode_service.cli_parser import parse_arguments
from barcode_service.confutil import ConfUtil
from barcode_service.eventconsumer import EventConsumer
from barcode_service.eventhandler import EventHandler
from barcode_service.eventproducer import EventProducer
from barcode_service.faxdao import \
    FailedInitializationException as FaxDaoFailedInitializationException
from barcode_service.faxdao import FaxDao
from barcode_service.generic_scanner import (BarcodeScannerOptions,
                                             create_barcode_scanner)
from barcode_service.helpers import custom_logging_callback
from barcode_service.synchronization import ShutDownSignal
from barcode_service.zbarreader import zbar_barcode_extractor

RESOURCES_MODULE = "barcode_service.resources"
PRODUCER_SCHEMA = "producer.avsc"
CONSUMER_SCHEMA = "reader.avsc"

DEFAULT_SCANNER_MAX_WAIT_PERIOD = 1.0 # Default Scanner Waiting Time
DEFAULT_SCANNER_MAX_RETRIES = 5 # Default Scanner Maximum Number of Retries

_log = logging.getLogger(__name__)

def __log_stracktrace(tp: BaseException, val: Union[BaseException, None], tb: Type[TracebackType]) -> None:
    """
        Exception hook used to log unhandled exceptions stacktrace
    """
    custom_logging_callback(_log, logging.CRITICAL, tp, val, tb)


def __log_thread_stacktrace(args: ExceptHookArgs) -> None:
    """
        Adapted Exception hook used to log unhandled exceptions stacktrace from threads
    """
    _log.critical(f"Exception from thread [{args.thread.getName()}] with ID [{args.thread.ident}]")
    __log_stracktrace(args.exc_type, args.exc_value, args.exc_traceback)


def __signal_cb(signum, _, shutdown_signal: ShutDownSignal) -> None:
    _log.warning(f"Signal handler called with signal {signum}")
    shutdown_signal.send_signal()


def _thread_main(conf, shutdown_signal: ShutDownSignal) -> None:
    """
        Decoder Worker thread body
    """
    try:
        # Loading Producer Schema
        with open_resource_text(RESOURCES_MODULE, PRODUCER_SCHEMA) as resource_file:
            producer_schema_txt = resource_file.read()

        # Loading Consumer Schema
        with open_resource_text(RESOURCES_MODULE, CONSUMER_SCHEMA) as resource_file:
            consumer_schema_txt = resource_file.read()

        # Check if faxes directory exists and is available.
        faxes_location = Path(conf["faxes_dir"]).absolute()
        if not faxes_location.exists() or not faxes_location.is_dir():
            raise NotADirectoryError(f"Invalid Fax Directory Location: [{str(faxes_location)}]")

        if not os.access(str(faxes_location), os.R_OK):
            raise PermissionError(f"No read rights to location [{faxes_location}]")

        scanner_options = conf.get("scanner_options", {"wait_period": DEFAULT_SCANNER_MAX_WAIT_PERIOD, "max_retries": DEFAULT_SCANNER_MAX_RETRIES})

        barcode_reader = BarcodeReader(
            BarcodeReader.BarcodeConfiguration(
                faxes_location=faxes_location
            ),
            create_barcode_scanner(
                zbar_barcode_extractor,
                BarcodeScannerOptions(
                    scanner_options.get("wait_period", DEFAULT_SCANNER_MAX_WAIT_PERIOD),
                    scanner_options.get("max_retries", DEFAULT_SCANNER_MAX_RETRIES),
                ),
            ),
        )

        faxdao = FaxDao(conf["db"])
        producer = EventProducer(conf["producer"], producer_schema_txt)
        handler = EventHandler(
            (lambda file_path, br=barcode_reader: br.read_barcode(file_path)),
            (lambda fax_id, barcodes, fd=faxdao: fd.save(fax_id, barcodes)),
            (lambda fax_id, fax, p=producer: p.send(fax_id, fax))
        )

        enable_scan_barcode = conf["enable_scan_barcode"]
        _log.info(f"enable_scan_barcode: {enable_scan_barcode}")
        if enable_scan_barcode:
            consumer = EventConsumer(
                conf["consumer"],
                consumer_schema_txt,
                (lambda fax, h=handler: h.handle(fax))
            )
        else:
            consumer = EventConsumer(
                conf["consumer"],
                consumer_schema_txt,
                (lambda fax, p=producer: p.send(fax["faxId"], fax))
            )

        # The worker thread registers the consumer termination method, for orderly shutdown
        shutdown_signal.register_callback((lambda c=consumer: c.terminate()))

        consumer.run()
    except FaxDaoFailedInitializationException as ex:
        _log.critical(f"Failed to connect to the database: [{str(ex)}]")
    except (NotADirectoryError, PermissionError) as ex:
        _log.critical(f"Invalid location configuration: [{str(ex)}]")
    else:
        _log.info("Decoder Thread terminating.")


def main():
    """
        This is the service entry point
    """
    sys.excepthook = __log_stracktrace # Main thread exception hook
    threading.excepthook = __log_thread_stacktrace # threads exception hook

    shutdown_signal = ShutDownSignal() # Shared with all workers for orderly shutdown

    # Setting Signals for orderly shutdown
    # This will call the ShutDownSignal object and propagate the shutdown signal to all registered threads
    for sig in (SIGTERM, SIGINT):
        register_signal(sig, (lambda signum, frame, shutdown_signal=shutdown_signal: __signal_cb(signum, frame, shutdown_signal)))

    arguments_parser = parse_arguments()
    program_arguments = arguments_parser.parse_args()

    conf = ConfUtil(
        conf_path = program_arguments.service_config_location,
        log_path = program_arguments.log_config_location
    )

    logging.config.dictConfig(conf.log_conf)

    _log.info(f'Service Configuration Options: "{conf.conf}"')
    _log.info(f'Logging Configuration Options: "{conf.log_conf}"')
    _log.info(f'Barcode Decoder Service: Version [{SERVICE_VERSION}]')


    thread_cnt = conf.conf["thread_cnt"]
    _log.info(f"Total thread count: {thread_cnt}")
    ps: List[Thread] = []
    for i in range(thread_cnt):
        p = Thread(name=f"Decoder {i}", target=_thread_main, args=(conf.conf, shutdown_signal))
        ps.append(p)
        p.start()
        _log.info(f"Thread [{p.name}] with id [{p.native_id}] has started")

    for p in ps:
        _log.info(f"Waiting for thread [{p.name}] with ID [{p.native_id}] to terminate.")
        p.join()
    _log.info("Barcode Service is terminating. Goodbye.")
