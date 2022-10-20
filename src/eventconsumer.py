import logging
import os
import signal

from eventhandler import *

from confluent_kafka import Consumer
from avroparser import *


class ShutDown:
    need_to_kill = False
    
    def __init__(self):
        global log
        log = logging.getLogger(__name__)
        log.info("new shutdown")
        signal.signal(signal.SIGINT, self.killit)
        signal.signal(signal.SIGTERM, self.killit)
    
    def killit(self, *args):
        log.warn("killit")
        self.need_to_kill = True
        

class EventConsumer:
    
    def __init__(self, conf, handler, shutdown):
        global log
        log = logging.getLogger(__name__)
        log.info(f"new EventConsumer. conf:{conf}")
        self.shutdown = shutdown
        
        self.conf = conf
        
        self.timeout = conf["timeout"]
        
        self.handler = handler
        schema_path = conf['schema_path']
        
        log.info(f"schema_path:{schema_path}")
        schema_txt = path_to_txt(schema_path)
        self.dec = AvroDec(schema_txt)
        
        self._new_consumer()
    
    def _new_consumer(self):
        conf2 = dict(filter(lambda e: e[0] in 
            ['bootstrap.servers', 'group.id', 'auto.offset.reset', 'enable.auto.commit'],
            self.conf.items()))
        
        self.consumer = Consumer(**conf2)
        topics = self.conf['topics']
        log.info(f"subscribe topics:{topics}")
        self.consumer.subscribe(topics)
    
    def run(self):
        log.info("run start")
        i = 0    
        while True:
            if self.shutdown.need_to_kill:
                log.warn("need_to_kill is true and exit this thread/process now")
                break
                
            i += 1
            msg = self.consumer.poll(self.timeout)
        
            if msg is None:
                continue
            if msg.error():
                log.error(f"Consumer error: {msg.error()}")
                continue
            key = self.decode(msg.key())
            fax = msg.value()
            if fax == None:
                log.error(f"can not read event from [topic:{msg.topic()}, partition:{msg.partition()}, offset:{msg.offset() }, key:{key}]")
                continue
            
            fax = self.dec.decode_confluent(fax)
            if fax == None:
                log.error(f"can not decode event from [topic:{msg.topic()}, partition:{msg.partition()}, offset:{msg.offset() }, key:{key}]")
                continue
            
            log.info(f'Received [topic:{msg.topic()}, partition:{msg.partition()}, offset:{msg.offset() }, key:{key}], event:{fax}')
            self.handler.handle(fax)
                
        self.consumer.close()
        log.info("run end")

    def decode(self, data):
            return data.decode("utf-8") if isinstance(data, bytes) else str(data)
