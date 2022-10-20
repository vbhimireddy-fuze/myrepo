import logging
import os

from barcodereader import *
from eventproducer import *
from faxdao import *

log = None


class EventHandler:
    
    def __init__(self,
        barcoder: BarcodeReader,
        dao: FaxDao,
        producer: EventProducer
    ):
        global log
        log = logging.getLogger(__name__)
        log.info("new EventHandler")
        self.barcoder = barcoder
        self.dao = dao
        self.producer = producer
    
    def handle(self, fax):
        subscriber = fax["subscriberId"]
        faxid = fax["faxId"]
        path = subscriber + faxid + ".tif"
        
        codes = []
        if faxid == "" or path == "":
            log.error("empty faxid or path and skip reading barcode")
        else: 
            log.info(f"target path:{path}")
            try:
                codes = self.barcoder.read_barcode(path)
            except Exception as e:
                log.error(f"failed to read_barcode:{e}")    
            
        log.info(f"faxid:{faxid}, codes:{codes}")    
        fax["barCodes"] = codes
  
        try:
            self.dao.save(faxid, codes)
        except Exception as e:
                log.error(f"failed save:{e}")
                    
        self.producer.send(faxid, fax)
