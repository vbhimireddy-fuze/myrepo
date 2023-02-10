from importlib.resources import open_text as open_resource_text
from unittest.mock import MagicMock, patch

from pytests.shared_data import KAFKA_FAX_DATA

from barcode_service.event_data import KafkaMessage
from barcode_service.eventproducer import EventProducer


def test_send():
    with patch("barcode_service.eventproducer.Producer") as producer:

        m_pro = MagicMock()
        producer.return_value = m_pro

        with open_resource_text("barcode_service.resources", "producer.avsc") as resource_file:
            schema_txt = resource_file.read()

        conf = {
            "topic":"t1",
            "bootstrap": { "servers": "localhost"},
        }
        pro = EventProducer(conf, schema_txt)

        event = KafkaMessage(
            fax=KAFKA_FAX_DATA,
            consumer_position= None,
            consumer_group_metadata= None,
        )
        pro.send(event)

        assert m_pro.produce.called
