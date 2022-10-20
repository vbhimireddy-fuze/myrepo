import io
import logging
import os

import avro.io
import avro.schema

log = None


class AvroDec:

    def __init__(self, schema_txt):
        schema = avro.schema.parse(schema_txt)
        self.reader = avro.io.DatumReader(schema)
        
    def decode(self, raw_bytes):
        message_bytes = io.BytesIO(raw_bytes)
        decoder = avro.io.BinaryDecoder(message_bytes)
        value = self.reader.read(decoder)
        return value
    
    def decode_confluent(self, raw_bytes):
        message_bytes = io.BytesIO(raw_bytes)
        message_bytes.seek(5)
        decoder = avro.io.BinaryDecoder(message_bytes)
        value = self.reader.read(decoder)
        return value

    
class AvroEnc:

    def __init__(self, schema_txt):
        schema = avro.schema.parse(schema_txt)
        self.writer = avro.io.DatumWriter(schema)
        self.buf = io.BytesIO()
        self.encoder = avro.io.BinaryEncoder(self.buf)
        
    def encode(self, value):
        self.writer.write(value, self.encoder)
        values = self.buf.getvalue()
        self.buf.seek(0)
        self.buf.truncate(0)
        return values        


def init_log(): 
    global log
    log = logging.getLogger(__name__)    

def path_to_txt(path):
    init_log()    
    txt = open(path).read()
    if txt == None or len(txt) == 0:
        log.error(f"exit. can not read path:{path}")
        exit(0)
    return txt
    
