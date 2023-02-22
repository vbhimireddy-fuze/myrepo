# coding=utf-8
import logging
import logging.config
import os
import sys
import threading
from copy import deepcopy
from importlib.resources import open_text as open_resource_text
from pathlib import Path
from signal import SIGINT, SIGTERM
from signal import signal as register_signal
from threading import ExceptHookArgs, Thread
from types import TracebackType
from typing import Type, Union

from barcode_service.barcodereader import BarcodeReader
from barcode_service.cli_parser import parse_arguments
from barcode_service.confutil import ConfUtil
from barcode_service.default_values import (CONSUMER_SCHEMA,
                                            DEFAULT_REST_API_HOST,
                                            DEFAULT_REST_API_PORT,
                                            DEFAULT_SCANNER_MAX_RETRIES,
                                            DEFAULT_SCANNER_MAX_WAIT_PERIOD,
                                            PRODUCER_SCHEMA, RESOURCES_MODULE)
from barcode_service.environment_variables import \
    get_environment_variable_configurations
from barcode_service.eventconsumer import EventConsumer
from barcode_service.eventhandler import EventHandler
from barcode_service.eventproducer import EventProducer
from barcode_service.faxdao import \
    FailedInitializationException as FaxDaoFailedInitializationException
from barcode_service.faxdao import FaxDao
from barcode_service.generic_scanner import (BarcodeScannerOptions,
                                             create_barcode_scanner)
from barcode_service.helpers import custom_logging_callback
from barcode_service.restapi import start_and_wait_for_rest_api
from barcode_service.spring_config import (
    SpringConfigException,
    get_configurations_from_cloud8_spring_config_service)
from barcode_service.synchronization import ShutDownSignal
from barcode_service.version import SERVICE_VERSION
from barcode_service.zbarreader import zbar_barcode_extractor

logging.basicConfig(
    format='[{asctime:^s}][{levelname:^8s}][{name:s}|{funcName:s}|{lineno:d}]: {message:s}',
    datefmt='%Y/%m/%d|%H:%M:%S (%Z)',
    style='{', level=logging.INFO
)

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


def _create_barcode_reader(faxes_location: Path, wait_period: float, max_retries: int) -> BarcodeReader:
    return BarcodeReader(
        BarcodeReader.BarcodeConfiguration(
            faxes_location=faxes_location
        ),
        create_barcode_scanner(
            zbar_barcode_extractor,
            BarcodeScannerOptions(wait_period, max_retries),
        ),
    )


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

        scanner_options = conf.get("scanner_options", {"wait_period": DEFAULT_SCANNER_MAX_WAIT_PERIOD, "max_retries": DEFAULT_SCANNER_MAX_RETRIES})
        barcode_reader = _create_barcode_reader(
            Path(conf["faxes_dir"]).absolute(),
            scanner_options.get("wait_period", DEFAULT_SCANNER_MAX_WAIT_PERIOD),
            scanner_options.get("max_retries", DEFAULT_SCANNER_MAX_RETRIES),
        )

        faxdao = FaxDao(conf["db"])
        producer = EventProducer(conf["producer"], producer_schema_txt)

        handler = EventHandler(
            (lambda file_path, br=barcode_reader: br.read_barcode(file_path)),
            (lambda fax_id, barcodes, fd=faxdao: fd.save(fax_id, barcodes)),
            (lambda kafka_event, p=producer: p.send(kafka_event))
        )

        enable_scan_barcode = conf["enable_scan_barcode"]
        _log.info(f"enable_scan_barcode: {enable_scan_barcode}")
        if enable_scan_barcode:
            consumer = EventConsumer(
                conf["consumer"],
                consumer_schema_txt,
                (lambda kafka_event, h=handler: h.handle(kafka_event))
            )
        else:
            consumer = EventConsumer(
                conf["consumer"],
                consumer_schema_txt,
                (lambda kafka_event, p=producer: p.send(kafka_event))
            )

        # The worker thread registers the consumer termination method, for orderly shutdown
        shutdown_signal.register_callback((lambda c=consumer: c.terminate()))

        consumer.run()
    except FaxDaoFailedInitializationException as ex:
        _log.critical(f"Failed to connect to the database: [{str(ex)}]")
    else:
        _log.info("Decoder Thread terminating.")


def main():
    """
        This is the service entry point
    """
    try:
        sys.excepthook = __log_stracktrace # Main thread exception hook
        threading.excepthook = __log_thread_stacktrace # threads exception hook

        shutdown_signal = ShutDownSignal() # Shared with all workers for orderly shutdown

        # Setting Signals for orderly shutdown
        # This will call the ShutDownSignal object and propagate the shutdown signal to all registered threads
        # These signal registrations are only valid if REST API is not executed. If so, the uvicorn webserver will take over the signal management
        for sig in (SIGTERM, SIGINT):
            register_signal(sig, (lambda signum, frame, shutdown_signal=shutdown_signal: __signal_cb(signum, frame, shutdown_signal)))

        arguments_parser = parse_arguments()
        program_arguments = arguments_parser.parse_args()
        environment_configurations = get_environment_variable_configurations()

        if program_arguments.config_files:
            service_configuration = program_arguments.service_config_location
            logger_configuration = program_arguments.log_config_location
        elif program_arguments.spring_config:
            spring_configurations = get_configurations_from_cloud8_spring_config_service(
                environment_configurations.spring_config_host, environment_configurations.spring_config_label
            )
            service_configuration = spring_configurations.barcode_service_configuration
            logger_configuration = spring_configurations.barcode_logger_configuration
        else:
            critical_error = f"Something is wrong with (config_files, spring_config) CLI parsed values: [{program_arguments.__dict__}]."
            _log.critical(critical_error)
            sys.exit(critical_error)

        conf = ConfUtil(
            conf_path = service_configuration,
            log_path = logger_configuration
        )

        service_configurations = conf.conf
        logging_configurations = conf.log_conf
        logging.config.dictConfig(logging_configurations)
        temp_config = deepcopy(service_configurations)
        del temp_config["db"]["password"] # Prevent logging the password
        _log.info(f'Environment Configurations: "{environment_configurations}"')
        _log.info(f'Service Configuration Options: "{temp_config}"')
        _log.info(f'Logging Configuration Options: "{logging_configurations}"')
        _log.info(f'Barcode Decoder Service: Version [{SERVICE_VERSION}]')
        del temp_config

        # Check if faxes directory exists and is available.
        faxes_location = Path(service_configurations["faxes_dir"]).absolute()
        if not faxes_location.exists() or not faxes_location.is_dir():
            raise NotADirectoryError(f"Invalid Fax Directory Location: [{str(faxes_location)}]")

        if not os.access(str(faxes_location), os.R_OK):
            raise PermissionError(f"No read rights to location [{faxes_location}]")

        # Kafka thread - Will consume kafka events, decode barcodes and add them to the database.
        kafka_thread = Thread(name="Kafka Decoder", target=_thread_main, args=(service_configurations, shutdown_signal))
        kafka_thread.start()
        _log.info(f"Thread [{kafka_thread.name}] with id [{kafka_thread.native_id}] has started")

        # REST API service (asyncio based) - Will listen to barcode decoding requests
        if "restapi" in service_configurations:
            _log.info(f'Rest API will be served at [{service_configurations["restapi"].get("host", DEFAULT_REST_API_HOST)}] on port [{service_configurations["restapi"].get("port", DEFAULT_REST_API_PORT)}]')
            scanner_options = service_configurations.get("scanner_options", {"wait_period": DEFAULT_SCANNER_MAX_WAIT_PERIOD, "max_retries": DEFAULT_SCANNER_MAX_RETRIES})
            barcode_reader = _create_barcode_reader(
                faxes_location,
                scanner_options.get("wait_period", DEFAULT_SCANNER_MAX_WAIT_PERIOD),
                scanner_options.get("max_retries", DEFAULT_SCANNER_MAX_RETRIES),
            )
            # Main thread will block here given that its the main thread that will run the asyncio REST API
            # asyncio loop will terminate upon receiving a SIGINT or SIGTERM signals from exterior.
            # shutdown_signal object is passed so that uvicorn can signal the application termination, if requested.
            start_and_wait_for_rest_api(service_configurations, conf.log_conf, shutdown_signal, faxes_location, barcode_reader)
        else:
            _log.warning("REST API configuration not Present. REST API will not be available.")

        if kafka_thread.is_alive():
            _log.info(f"Waiting for thread [{kafka_thread.name}] with ID [{kafka_thread.native_id}] to terminate.")
            kafka_thread.join()

        _log.info("Barcode Service is terminating. Goodbye.")
    except (SpringConfigException, NotADirectoryError, PermissionError) as ex:
        _log.error(ex)
        sys.exit(str(ex))
