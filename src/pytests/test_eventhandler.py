from unittest.mock import MagicMock

from barcode_service.barcodereader import Barcode
from barcode_service.event_data import KafkaMessage
from barcode_service.eventhandler import EventHandler


def barcoder(path):
    print("read path:", path)
    return (Barcode(page_no=1, format='CODE128', raw_result='kelly.troy@aerocareusa.com'),)

def test_handle():
    dao = MagicMock()
    producer = MagicMock()
    handler = EventHandler(barcoder, dao, producer)
    fax = {
        "faxId":"f1",
        "subscriptionId":"sub1",
        "state":"mark_new",
        "direction":"incoming",
        "fileName":"f1",
        "subscriberId":"s1"
    }
    event = KafkaMessage(
        fax=fax,
        consumer_position= None,
        consumer_group_metadata= None,
    )
    handler.handle(event)

    assert dao.called
    assert producer.called
