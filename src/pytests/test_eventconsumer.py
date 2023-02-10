import threading
import time
from importlib.resources import open_text as open_resource_text
from unittest.mock import MagicMock, patch

from barcode_service.avroparser import AvroEnc
from barcode_service.eventconsumer import EventConsumer
from pytests.shared_data import KAFKA_FAX_DATA


def test_run():
    with patch("barcode_service.eventconsumer.Consumer") as consumer:
        m_con = MagicMock()
        consumer.return_value = m_con
        m_con.poll.return_value = MockMsg()

        with open_resource_text("barcode_service.resources", "reader.avsc") as resource_file:
            schema_txt = resource_file.read()

        conf = {
            "topics":["t1"],
            "bootstrap": {"servers":"localhost"},
            "group": {"id" : "barcode"},
            "auto": {"offset": {"reset": "earliest"}, },
            "timeout": 10,
            "is_confluent": True,
        }
        handler = MagicMock()
        con = EventConsumer(conf, schema_txt, handler)

        pro1 = threading.Thread(target=con.run)
        pro1.start()
        time.sleep(1)
        pro2 = threading.Thread(target=con.terminate)
        pro2.start()

        assert handler.called


class MockMsg():

    def error(self):
        return False

    def value(self):
        with open_resource_text("barcode_service.resources", "reader.avsc") as resource_file:
            schema_txt = resource_file.read()
        enc = AvroEnc(schema_txt)
        return enc.encode(KAFKA_FAX_DATA)

    def topic(self):
        return "t1"

    def partition(self):
        return "p1"

    def offset(self):
        return 123

    def key(self):
        return "k1"
