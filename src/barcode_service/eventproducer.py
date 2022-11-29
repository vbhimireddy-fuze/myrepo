# coding=utf-8
import logging

from confluent_kafka import Producer

from barcode_service.avroparser import AvroEnc

_log = logging.getLogger(__name__)


class EventProducer:

    def __init__(self, conf: dict, schema: str) -> None:
        self.conf = conf
        self.topic = conf['topic']
        self.enc = AvroEnc(schema)
        producer_config = dict(filter(lambda e: e[0] in ('bootstrap.servers',), self.conf.items()))
        self.producer = Producer(**producer_config)

    def send(self, fax_id: str, fax: dict) -> None:
        data = self.enc.encode(fax)
        size = len(data)
        _log.info(f"sending faxid:{fax_id}, fax:{fax}, size:{size}")
        self.producer.produce(self.topic, key=fax_id, value=data, callback=(lambda err, msg, fax_id=fax_id: self.__producer_cb(err, msg, fax_id)))
        self.producer.flush()

    def __producer_cb(self, err: int, msg: str, fax_id: str) -> None:
        if err:
            _log.error(f"failed delivering faxid:{fax_id}")
        else:
            _log.info(f"delivered faxid:{fax_id}. partition:{msg.partition()}, offset:{msg.offset()}")
