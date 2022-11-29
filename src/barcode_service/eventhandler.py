# coding=utf-8
import logging
from pathlib import Path
from typing import Callable

from mysql.connector import PoolError, DatabaseError

from barcode_service.barcodereader import (BarcodeReader,
                                           FailedToProcessImageException)
from barcode_service.faxdao import AbstractDao, FaxDaoException

_log = logging.getLogger(__name__)


class EventHandler:

    def __init__(self, barcoder: BarcodeReader, dao: AbstractDao, producer_handler: Callable[[str, dict], None]) -> None:
        if any((a is None for a in (barcoder, dao, producer_handler))):
            raise ValueError()
        self.__barcoder = barcoder
        self.__dao = dao
        self.__producer_handler = producer_handler

    def handle(self, fax: dict) -> None:
        try:
            # Initialization to cover the event of an exception being raised
            fax["barCodes"] = []

            fax_id = fax["faxId"]
            fileName = fax["fileName"]
            subscriber = fax["subscriberId"]
            state = fax["state"]

            # Only scan fax events marked as New
            if state == "mark_new":
                path = f"{subscriber}/in/{fileName}"
                _log.info(f"Analyzing file: {path}")
                codes = self.__barcoder.read_barcode(Path(path))
                _log.info(f"Fax ID [{fax_id}]; Codes [{codes}]")
                fax["barCodes"] = list(
                    ( {"pageNo": bar_code.page_no, "format": bar_code.format, "rawResult": bar_code.raw_result} for bar_code in codes )
                )
                if len(codes):
                    self.__dao.save(fax_id, codes)
            else:
                _log.warning(f"Skip barcode scanning because fax state is not 'mark_new'. Fax ID [{fax_id}] has state [{state}]")
        except (FailedToProcessImageException, KeyError, ValueError, DatabaseError, PoolError, FaxDaoException, RuntimeError) as ex:
            _log.error(str(ex))
        finally:
            self.__producer_handler(fax_id, fax)
