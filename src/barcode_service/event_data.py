from dataclasses import dataclass
from typing import Any, List

from confluent_kafka import TopicPartition


__all__ = ["KafkaMessage"]

@dataclass
class KafkaMessage():
    fax: dict
    consumer_position: List[TopicPartition]
    consumer_group_metadata: Any
