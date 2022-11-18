import logging
import os
from datetime import datetime

from barcode_service.barcodereader import CommonReader
import pyzbar.pyzbar as pyzbar


class ZbarReader(CommonReader):
    
    def __init__(self, conf):
        global log
        log = logging.getLogger(__name__)
        log.info("new ZbarReader")
        self.conf = conf
    
    def add_codes(self, img, no: int, codes):
        log.info("barcode scan started")
        started = datetime.now()
        results = pyzbar.decode(img)
        log.info(f"{len(results)} codes were found at page:{no}")
        for result in results:
            ty = result.type
            val = str(result.data)
            data = result.data
            val = data.decode("utf-8") if isinstance(data, bytes) else str(data)
            
            code = {"pageNo": no, "format": ty, "rawResult": val}
            log.info(code)
            codes.append(code)
        
        ended = datetime.now()
        duration = ended - started
        log.info(f"barcode scan ended. Duration:{duration}")
