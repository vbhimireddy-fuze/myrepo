# coding=utf-8
import logging
from dataclasses import dataclass
from datetime import datetime
from json import dumps as json_dumps
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

    def read_barcode(self, file_location: Path) -> Tuple[Barcode]:
        full_file_path = (self.faxes_location / file_location).absolute()

        start_time = datetime.now()
        bar_codes = tuple(
            (Barcode(page_number, data_type, value, quality) for (page_number, data_type, value, quality) in self.__barcode_extractor(full_file_path))
        )
        end_time = datetime.now()

        format_occurrences: list[str] = list(b.format for b in bar_codes)
        statistic_data = json_dumps(
            {
                "ScanningDuration": (end_time - start_time).total_seconds(),
                "BarcodesCount": len(bar_codes),
                "FileFullPath": str(full_file_path),
                "BarcodeOccurrences": { fmt: format_occurrences.count(fmt) for fmt in format_occurrences },
            }
        )
        _log.info(f"Barcode scan has ended. Scanning statistics: [{statistic_data}].")
        return bar_codes
