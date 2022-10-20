import logging
import os
import mysql.connector.pooling as pooling    

# those should not be used in barcode
deli = '¹'
deli2 = '²'

_save_query = "update t_fax set barcodes = %s where faxId = %s"


class FaxDao:
    
    def __init__(self, conf):
        global log
        log = logging.getLogger(__name__)
        self.conf = conf
        log.info(f"new FaxDao, host:{conf['host']}, db:{conf['database']}")
        self.max_column_size = conf.pop("max_column_size")
        pool_size = conf["pool_size"]
        log.info(f"pool_size:{pool_size}")
        self.pool = pooling.MySQLConnectionPool(pool_name="faxdb",
                                                      **conf)
        
    def save(self, faxid, barcodes):
        log.info(f"save faxid:{faxid}")
        codetxt = deli2
        try:
            codetxt = self.codes2txt(barcodes)
        except Exception as e:
                log.error(f"failed codes2txt:{e}")    
        
        size = len(codetxt)
        if size > self.max_column_size:
            log.warning(f"data exceed. size:{size}")
            codetxt = codetxt[:size]
            
        log.info(f"codetxt:{codetxt}")

        con = None
        cur = None 
        try:
            con = self.pool.get_connection()
            cur = con.cursor(prepared=True)
            params = (codetxt, faxid)
            cur.execute(_save_query, params)
            con.commit()
        except Exception as e: 
            log.error(f"failed query, e:{e}")
            
        finally:
            self._close(cur) 
            self._close(con)            
            
    def _close(self, obj):
        try:
            obj.close()
        except:
            log.info(f"closing failed:{obj}")
            None        
    
    def codes2txt(self, codes):
        if not codes:
            return deli2
        
        txt = ""
        for code in codes:
            txt = txt + self.code2txt(code) + deli2
        return txt
        
    def code2txt(self, code):
        no = str(code.get("pageNo"))          
        fm = str(code.get("format"))
        result = str(code.get("rawResult"))
        txt = no + deli + fm + deli + result
        return txt
