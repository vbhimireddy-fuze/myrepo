import threading
import time
from unittest.mock import patch, MagicMock
from barcode_service.eventconsumer import EventConsumer
from barcode_service.avroparser import AvroEnc


def test_run():
    with patch("barcode_service.eventconsumer.Consumer") as consumer:
        m_con = MagicMock()
        consumer.return_value = m_con
        m_con.poll.return_value = MockMsg()

        with open('../barcode_service/resources/reader.avsc', encoding="utf-8") as file:
            schema_txt = file.read()

        conf = {"topics":["t1"], "bootstrap.servers":"localhost", "timeout": 10,
            "is_confluent": True}
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
        with open('../barcode_service/resources/reader.avsc', encoding="utf-8") as file:
            schema_txt = file.read()
        enc = AvroEnc(schema_txt)
        msg = {
            "uuid":"579182d9-d827-435a-a91e-5ab6af28b5fb",
            "customerId":"0010r00000BF40SAAT",
            "userId":"KZGW7_R5TNmYGusP5y0Lvg",
            "faxId":"f2882f59916143f0bca1b4becdff602e",
            "subject":"",
            "fileName":"03aa178f6736421aad569fc4bedaba6f.pdf",
            "subscriberId":"Gg30YjCTQneGIJCWHFIwOA-INTERNET_FAX",
            "from":"14086278887",
            "to":"16014320257",
            "remotePartyId":"14086278887",
            "state":"completed",
            "cause":{
               "systemCode":"1001",
               "userString":"Normal.",
               "userCode":"2001"
            },
            "sentPage":"1/1",
            "receivedPage":"None",
            "retryCount":0,
            "startTimestamp":1669095140000,
            "updateTimestamp":1669066419457,
            "direction":"outgoing",
            "hqFax":"yes",
            "countryCode":"-US",
            "fromDid":"+14086278887",
            "toDid":"+16014320257",
            "subscriptionId":"06xGIVUxQ7OXorsZzt2WPw"
        }
        return enc.encode(msg)

    def topic(self):
        return "t1"

    def partition(self):
        return "p1"

    def offset(self):
        return 123

    def key(self):
        return "k1"
