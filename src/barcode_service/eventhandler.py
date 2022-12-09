# coding=utf-8
import logging
from pathlib import Path
from typing import Callable, Tuple

from mysql.connector import DatabaseError, PoolError

from barcode_service.barcodereader import Barcode
from barcode_service.dao_exceptions import DaoException
from barcode_service.event_exceptions import InvalidMessageAttributeException
from barcode_service.processing_exceptions import ScanningFailureException

_log = logging.getLogger(__name__)


class EventHandler:

    def __init__(self, read_barcodes: Callable[[Path], Tuple[Barcode]], store_barcodes: Callable[[str, Tuple[Barcode]], None], producer_handler: Callable[[str, dict], None]) -> None:
        self.__read_barcodes = read_barcodes
        self.__store_barcodes = store_barcodes
        self.__producer_handler = producer_handler

    def handle(self, fax: dict) -> None:
        try:
            # Initialization to cover the event of an exception being raised
            fax["barCodes"] = []
            state = fax.get("state", None)
            direction = fax.get("direction", None)
            fax_id = fax["faxId"] # No validation is required for Fax ID because schema requires it to be present.

            if not all((direction, state)):
                raise InvalidMessageAttributeException(f"Invalid Fax Attributes Present: state: [{state}]; direction: [{direction}]")

            # Only scan incoming fax events marked as New
            if direction == "incoming" and state == "mark_new":
                file_name = fax.get("fileName", None)
                subscriber = fax.get("subscriberId", None)

                if not all((file_name, subscriber)):
                    raise InvalidMessageAttributeException(f"Invalid Fax Attributes Present. Cannot Process. fileName: [{file_name}]; subscriber: [{subscriber}]")

                file_name = Path(file_name)
                self.__process_fax(fax, Path(f"{subscriber}/in/{file_name.stem}.tif"))

            else:
                _log.warning(f"Skip barcode scanning because fax state and direction. Fax ID [{fax_id}] has direction [{direction}] and state [{state}]")

        except (DatabaseError, PoolError, DaoException, InvalidMessageAttributeException, ScanningFailureException) as ex:
            _log.error(str(ex))
        finally:
            self.__producer_handler(fax_id, fax)

    def __process_fax(self, fax: dict, file: Path) -> None:
        fax_id = fax["faxId"]
        _log.info(f"Analyzing file: {file}")
        codes = self.__read_barcodes(file)
        _log.info(f"Fax ID [{fax_id}]; Codes [{codes}]")
        fax["barCodes"] = list(
            ( {"pageNo": bar_code.page_no, "format": bar_code.format, "rawResult": bar_code.raw_result} for bar_code in codes )
        )
        if codes:
            self.__store_barcodes(fax_id, codes)
