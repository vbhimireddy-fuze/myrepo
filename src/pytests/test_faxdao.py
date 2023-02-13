from unittest.mock import MagicMock, patch

from barcode_service.faxdao import FaxDao
from barcode_service.service_data import Barcode


def test_save():
    with patch("barcode_service.faxdao.pooling.MySQLConnectionPool") as pool:
        m_pool = MagicMock()
        pool.return_value = m_pool
        con = MagicMock()
        m_pool.get_connection.return_value.__enter__.return_value = con
        cur = MagicMock()
        con.cursor.return_value.__enter__.return_value = cur
        cur.__next__.return_value.data_type = "tinytext"

        conf = {"host": "localhost", "database":"db", "pool_size": 10}
        dao = FaxDao(conf)

        dao.save("f1", [])

        assert con.cursor.called
        assert con.commit.called


def test_serialize_barcodes():
    with patch("barcode_service.faxdao.pooling.MySQLConnectionPool") as pool:
        m_pool = MagicMock()
        pool.return_value = m_pool
        con = MagicMock()
        m_pool.get_connection.return_value.__enter__.return_value = con
        cur = MagicMock()
        con.cursor.return_value.__enter__.return_value = cur
        cur.__next__.return_value.barcodes_max_length = 0xFFFF

        conf = {"host": "localhost", "database":"db", "pool_size": 10}
        dao = FaxDao(conf)

        codes = [Barcode(1, "code128", "this is barcode")]
        fake_faxid = "12345"
        expected_serialization_value = "1¹code128¹this is barcode"
        saved_barcodes_text = ""
        saved_fax_id = ""

        def fake_execute(_, query_data_tuple):
            nonlocal saved_barcodes_text, saved_fax_id
            (saved_barcodes_text, saved_fax_id) = query_data_tuple


        cur = MagicMock()
        cur.execute = fake_execute
        con.cursor.return_value.__enter__.return_value = cur

        dao.save(fake_faxid, codes)
        assert saved_barcodes_text == expected_serialization_value
        assert saved_fax_id == fake_faxid
