# coding=utf-8
import logging
from abc import ABC, abstractmethod
from typing import Iterable

from mysql.connector import pooling, DatabaseError

from barcode_service.barcodereader import Barcode

_log = logging.getLogger(__name__)

# These characters should not be encoded in bar codes
_FIELDS_DELIMITER = '¹'
_BARCODE_DATA_DELIMITER = '²'

_UPDATE_QUERY = """
UPDATE t_fax
SET barcodes = %s
WHERE faxId = %s
"""

_BARCODES_FIELD_TYPE_QUERY = """SELECT data_type
FROM information_schema.columns
WHERE  table_name = 't_fax' AND column_name = 'barCodes'
LIMIT 1
"""

_MAXIMUM_TEXT_TYPES_LENGHT = {
    "tinytext": 256,
    "text": 65535,
    "mediumtext": 16777215,
    "longtext": 4294967295
}


class AbstractDao(ABC):
    @abstractmethod
    def save(self, fax_id: str, barcodes: Iterable[Barcode]) -> None:
        pass


class FaxDaoException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class FailedInitializationException(FaxDaoException):
    pass


class FaxDao(AbstractDao):
    def __init__(self, conf: dict) -> None:
        try:
            self.__pool = pooling.MySQLConnectionPool(pool_name="faxdb", **conf)
            with self.__pool.get_connection() as con:
                with con.cursor(named_tuple=True) as cur:
                    cur.execute(_BARCODES_FIELD_TYPE_QUERY)
                    if not cur.with_rows:
                        raise FailedInitializationException("Could not obtain barCodes field type from database")
                    field_type: str = next(cur).data_type
                    con.commit()
                    field_type = field_type.lower()
                    self.__max_column_size = _MAXIMUM_TEXT_TYPES_LENGHT.get(field_type, None)
                    if self.__max_column_size is None:
                        raise FailedInitializationException(f"Database barCodes field type is [{field_type}]. Accepted types are [{tuple(_MAXIMUM_TEXT_TYPES_LENGHT.keys())}]")

                    _log.info(f"Maximum barcode serialized data length is {self.__max_column_size}")
        except DatabaseError as ex:
            raise FailedInitializationException(str(ex)) from ex

    def save(self, fax_id: str, barcodes: Iterable[Barcode]) -> None:
        _log.debug(f"Updating fax [{fax_id}] with barcode data")

        barcodes_text, leftovers = self._serialize_barcodes(barcodes)
        if leftovers:
            _log.warning(f"Could not save the following barcodes for fax with ID [{fax_id}]: [{leftovers}]")

        _log.debug(f"barcodes_text: {barcodes_text}")

        with self.__pool.get_connection() as con:
            with con.cursor(prepared=True) as cur:
                cur.execute(_UPDATE_QUERY, (barcodes_text, fax_id))
                con.commit()

    def _serialize_barcodes(self, barcodes: Iterable[Barcode]) -> str:
        available_space = self.__max_column_size
        barcodes_prep = []
        leftovers = []
        for index, code in enumerate(barcodes):
            serialized_code = "{page_no:d}{delimiter:1s}{format:s}{delimiter:1s}{raw_result:s}".format(
                delimiter=_FIELDS_DELIMITER,
                page_no=code.page_no,
                format=code.format,
                raw_result=code.raw_result
            )
            serialized_code_len = len(serialized_code)
            if available_space < serialized_code_len:
                leftovers.extend(barcodes[index:])
                break
            available_space -= (serialized_code_len + (len(_BARCODE_DATA_DELIMITER) if index > 0 else 0))
            barcodes_prep.append(serialized_code)

        return (_BARCODE_DATA_DELIMITER.join(barcodes_prep), leftovers)
