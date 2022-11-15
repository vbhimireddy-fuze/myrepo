from avroparser import *
import logging
from confluent_kafka import Producer

from confutil import *


class EventProducer:
    
    def __init__(self, conf):
        global log
        log = logging.getLogger(__name__)
        log.info("new EventProducer")
        self.conf = conf
        schema_path = conf['schema_path']
        self.topic = conf['topic']
        log.info(f"schema_path:{schema_path}, topic:{self.topic}")
        
        schema_txt = path_to_txt(schema_path)
        self.enc = AvroEnc(schema_txt)
        self.__new_producer()
        
    def __new_producer(self):
        conf2 = dict(filter(lambda e: e[0] in 
            ['bootstrap.servers'],
            self.conf.items()))
        
        self.producer = Producer(**conf2)
        
    def send(self, faxid, fax):
        data = self.enc.encode(fax)
        size = len(data)
        log.info(f"sending faxid:{faxid}, fax:{fax}, size:{size}")
        
        callback = CallBack(faxid)
        self.producer.produce(self.topic, key=faxid, value=data, callback=callback.done)
        self.producer.flush()


class CallBack:
    
    def __init__(self, faxid):
        self.faxid = faxid
    
    def done(self, err, msg):
        if err:
            log.error(f"failed delivering faxid:{self.faxid}")
        else:
            log.info(f"delivered faxid:{self.faxid}. partition:{msg.partition()}, offset:{msg.offset()}")
            
