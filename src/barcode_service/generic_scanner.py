# coding=utf-8
import logging
from pathlib import Path
from time import sleep
from typing import Generator, Tuple
from dataclasses import dataclass
from copy import deepcopy

from barcode_service.processing_exceptions import ScanningFailureException

_log = logging.getLogger(__name__)


@dataclass
class BarcodeScannerOptions:
    retry_delay: float
    max_retry_count: int

def create_barcode_scanner(generic_extractor: Generator[Tuple[int, str, str], None, None], options: BarcodeScannerOptions):
    def extractor(image_location: Path):
        scanner_options = deepcopy(options)
        attempt = 1
        while attempt <= scanner_options.max_retry_count:
            try:
                for result in generic_extractor(image_location):
                    yield result
                return
            except ScanningFailureException as ex:
                _log.error(f"Attempt [{attempt} failed due to: [{ex}]")
            attempt += 1
            sleep(scanner_options.retry_delay)
        raise ScanningFailureException(f"Cannot process image at location [{image_location.absolute()}]. Failed all attempts.")

    return extractor
