# coding=utf-8
import logging
from threading import Lock
from typing import Callable

from confluent_kafka import Consumer

from barcode_service.avroparser import AvroDec
from barcode_service.event_data import KafkaMessage

_log = logging.getLogger(__name__)


class EventConsumer:

    def __init__(self, conf: dict, schema: str, fax_handler_cb: Callable[[KafkaMessage], None]) -> None:
        _log.info(f"new EventConsumer. conf:{conf}")
        self.__config_lock = Lock()
        self.__terminated = False

        self.__timeout = conf["timeout"]
        self.__is_confluent = conf["is_confluent"]
        self.__fax_handler_cb = fax_handler_cb

        self.__dec = AvroDec(schema)

        self.__consumer = Consumer(
            **{
                'bootstrap.servers': conf['bootstrap']['servers'],
                'group.id': conf['group']['id'],
                'auto.offset.reset': conf['auto']['offset']['reset'],
                'enable.auto.commit': False,
                'isolation.level': 'read_committed',
            }
        )
        topics = conf['topics']
        self.__consumer.subscribe(
            topics,
            on_assign=(
                lambda _, partitions: _log.info(
                    f"Assigned partitions: [{tuple(p.partition for p in partitions)}]"
                )
            ),
            on_revoke=(
                lambda _, partitions: _log.info(
                    f"Revoked partitions: [{tuple(p.partition for p in partitions)}]"
                )
            ),
        )
        _log.info(f"Subscribed to topics [{topics}]")

    def run(self) -> None:
        try:
            while True:
                with self.__config_lock:
                    if self.__terminated:
                        _log.info("Kafka consumer was closed")
                        break

                    msg = self.__consumer.poll(timeout=self.__timeout)

                if msg is None:
                    continue

                if msg.error():
                    _log.error(f"Consumer error: {msg.error()}")
                    continue

                key = self.__decode(msg.key())
                fax = msg.value()
                if fax is None:
                    _log.error(f"Can not read event from [topic:{msg.topic()}, partition:{msg.partition()}, offset:{msg.offset() }, key:{key}]")
                    continue

                if self.__is_confluent:
                    fax = self.__dec.decode_confluent(fax)
                else:
                    fax = self.__dec.decode(fax)
                if fax is None:
                    _log.error(f"Can not decode event from [topic:{msg.topic()}, partition:{msg.partition()}, offset:{msg.offset() }, key:{key}]")
                    continue

                _log.info(f'Received [topic:{msg.topic()}, partition:{msg.partition()}, offset:{msg.offset() }, key:{key}], event:{fax}')
                event = KafkaMessage(
                    fax=fax,
                    consumer_position=self.__consumer.position(self.__consumer.assignment()),
                    consumer_group_metadata=self.__consumer.consumer_group_metadata(),
                )
                self.__fax_handler_cb(event)

        except RuntimeError as ex:
            _log.warning(f"Consumer was terminated due to reason: [{ex}]")

    def __decode(self, data) -> str:
        return data.decode("utf-8") if isinstance(data, bytes) else str(data)

    def terminate(self) -> None:
        with self.__config_lock:
            if self.__terminated:
                _log.warning("Consumer already terminated")
                return

            _log.info("Terminating Consumer")
            self.__consumer.close()
            self.__terminated = True
