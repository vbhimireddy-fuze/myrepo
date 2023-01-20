# coding=utf-8
import logging
from uuid import uuid4

from confluent_kafka import KafkaError, KafkaException, Producer

from barcode_service.avroparser import AvroEnc
from barcode_service.event_data import KafkaMessage

_log = logging.getLogger(__name__)


class EventProducer:

    def __init__(self, conf: dict, schema: str) -> None:
        self.conf = conf
        self.topic = conf['topic']
        self.enc = AvroEnc(schema)
        producer_config = dict(filter(lambda e: e[0] in ('bootstrap.servers',), self.conf.items()))
        producer_config['transactional.id'] = f"barcode-transfer-{uuid4()}" # Unique IDs per producers is required to avoid Transaction Fencing
        self.producer = Producer(**producer_config)
        self.producer.init_transactions()

    def send(self, event: KafkaMessage) -> None:
        try:
            fax = event.fax
            fax_id = fax["faxId"]
            data = self.enc.encode(fax)
            size = len(data)
            _log.info(f"sending faxid:{fax_id}, fax:{fax}, size:{size}")
            self.producer.begin_transaction()
            self.producer.produce(self.topic, key=fax_id, value=data, callback=(lambda err, msg, fax_id=fax_id: self.__producer_cb(err, msg, fax_id)))
            self.producer.send_offsets_to_transaction(
                event.consumer_position,
                event.consumer_group_metadata
            )
            self.producer.commit_transaction()
        except (KafkaError, KafkaException) as ex:
            _log.error(f"Production of Kafka event failed: [{ex}]")
            self.producer.abort_transaction()

    def __producer_cb(self, err: int, msg: str, fax_id: str) -> None:
        if err:
            _log.error(f"failed delivering faxid:{fax_id}")
        else:
            _log.info(f"delivered faxid:{fax_id}. partition:{msg.partition()}, offset:{msg.offset()}")
