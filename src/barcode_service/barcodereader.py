# coding=utf-8
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Generator, Tuple

from barcode_service.service_data import Barcode

_log = logging.getLogger(__name__)


class BarcodeReader:
    @dataclass
    class BarcodeConfiguration:
        faxes_location: Path

    def __init__(self, config: BarcodeConfiguration, barcode_extractor: Generator[Tuple[int, str, str], None, None]) -> None:
        self.__barcode_extractor = barcode_extractor
        self.faxes_location: Path = config.faxes_location
        _log.info(f"new BarcodeReader. NFS faxes_dir:{self.faxes_location}")

    def read_barcode(self, file_location: Path) -> Tuple[Barcode]:
        full_file_path = (self.faxes_location / file_location).absolute()

        start_time = datetime.now()
        bar_codes = tuple(
            (Barcode(page_number, data_type, value) for (page_number, data_type, value) in self.__barcode_extractor(full_file_path))
        )
        end_time = datetime.now()
        duration = end_time - start_time
        _log.info(f"Barcode scan has ended. Duration [{duration}]")
        _log.info(f"Found [{len(bar_codes)}] barcodes at file [{full_file_path}]")

        return bar_codes
