import logging
import os

from barcodereader import *
from eventproducer import *
from faxdao import *

class EventHandler:
    
    def __init__(self, conf, barcoder, dao, producer):
        global log
        log = logging.getLogger(__name__)
        log.info("new EventHandler")
        self.conf = conf
        self.start_time = conf['start_time']
        log.info(f"start_time:{self.start_time}")
        self.barcoder = barcoder
        self.dao = dao
        self.producer = producer
    
    
    def handle(self, fax):
        faxid = fax["faxId"]
        
        subscriber = fax["subscriberId"]
        state = fax["state"]
        # right now we only scan new i/b faxes but 
        # later it may be changed by user (system) requirement
        if state == "mark_new": 
            path = f"{subscriber}/in/{faxid}.tif"
            codes = []
            log.info(f"target path:{path}")
            try:
                codes = self.barcoder.read_barcode(path)
            except Exception as e:
                log.exception(f"failed to read_barcode:{e}")    
            
            log.info(f"faxid:{faxid}, codes:{codes}")    
            fax["barCodes"] = codes
      
            self.dao.save(faxid, codes)
            
        else:
            log.info(f"skip barcode scanning because it is not 'mark_new'. faxid:{faxid}")
                        
        self.producer.send(faxid, fax)
