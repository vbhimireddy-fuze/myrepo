# coding=utf-8
from io import BytesIO
from typing import Union

from avro.io import BinaryDecoder, BinaryEncoder, DatumReader, DatumWriter
from avro.schema import parse as schema_parse


class AvroDec:

    def __init__(self, schema_txt: str) -> None:
        schema = schema_parse(schema_txt)
        self.reader = DatumReader(schema)

    def decode(self, raw_bytes: bytes) -> Union[str, bytes]:
        message_bytes = BytesIO(raw_bytes)
        decoder = BinaryDecoder(message_bytes)
        value = self.reader.read(decoder)
        return value

    def decode_confluent(self, raw_bytes: bytes) -> Union[str, bytes]:
        message_bytes = BytesIO(raw_bytes)
        message_bytes.seek(5)
        decoder = BinaryDecoder(message_bytes)
        value = self.reader.read(decoder)
        return value

class AvroEnc:

    def __init__(self, schema_txt: str) -> None:
        schema = schema_parse(schema_txt)
        self.writer = DatumWriter(schema)
        self.buf = BytesIO()
        self.encoder = BinaryEncoder(self.buf)

    def encode(self, value: object) -> bytes:
        self.buf.seek(5)
        self.writer.write(value, self.encoder)
        values = self.buf.getvalue()
        self.buf.seek(0)
        self.buf.truncate(0)
        return values
