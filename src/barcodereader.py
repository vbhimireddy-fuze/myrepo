import logging
import os
from os.path import exists

import cv2


class BarcodeReader:
    
    def __init__(self, conf, reader):
        global log
        global root_dir
        log = logging.getLogger(__name__)
        self.conf = conf
        self.reader = reader
        root_dir = conf["root_dir"]
        log.info(f"new BarcodeReader. root_dir:{root_dir}")
    
    def read_barcode(self, path):
        if path == "":
            log.error("path is empty. skip")
            return []
        
        full_path = root_dir + path
        log.info(f"read_barcode from full_path:{full_path}")
        
        if exists(full_path) == False:
            log.error(f"file does not exist:{full_path}. skip")
            return []
        
        return self._read_barcode(full_path)
        
    def _read_barcode(self, full_path):
        codes = []
        ret, imgs = cv2.imreadmulti(full_path, [], cv2.IMREAD_REDUCED_COLOR_2)
        if ret == False:
            log.error(f"can't open image:{full_path}")
            return codes
    
        no = 0
        size = len(imgs)
        log.info(f"found {size} images at {full_path}")
        for img in imgs:
            no += 1
            self.reader.add_codes(img, no, codes)
        
        return codes
        

class CommonReader:
    
    def add_codes(self, img, no: int, codes):
        pass
