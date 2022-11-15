import yaml

import logging
import logging.config
import threading
import getpass

import os
import sys
from faxdao import *
from barcodereader import *
from eventhandler import *
from eventconsumer import *

from confutil import *

from zbarreader import ZbarReader

    
def main():
    print("main starts.")
    print(f"pwd:{os.getcwd()}")
    
    global log
    env = ""  # default
    if len(sys.argv) > 1:
        env = sys.argv[1]
        print(f"given env is {env}")
    else:
        print("use default env")    
        
    conf = single_confutil(env).conf
    
    user_id = conf['user_id']
    if not check_user(user_id):
        print(f'Please try with id:{user_id}')
        sys.exit(1)
    
    log = logging.getLogger(__name__)
    log.info("log is ready and started")
    
    dao = FaxDao(conf["db"])
    shutdown = ShutDown()
    
    thread_cnt = conf["thread_cnt"]
    log.info(f"total thread_cnt:{thread_cnt}")
    ps = []
    for i in range(thread_cnt):
        log.info(f"new {i + 1}th process starts")
        p = threading.Thread(target=new_task, args=(conf, dao, shutdown))
        ps.append(p)
        p.start()
        
    for p in ps:
        p.join()
    log.info("End Barcode Application. Good Bye")        

    
def check_user(idNeed):
    myid = getpass.getuser()
    if idNeed != myid:
        print(f'your id should be :{idNeed} but it is {myid}')
        return False
    return True

         
def new_task(conf, dao, shutdown):
    barcoder_conf = conf["barcoder"]
    barcoder = BarcodeReader(barcoder_conf, new_reader(conf))
    
    producer_conf = conf["producer"]
    producer = EventProducer(producer_conf)
    
    handler_conf = conf["handler"]
    hanlder = EventHandler(handler_conf, barcoder, dao, producer)
    consumer_conf = conf["consumer"]
    consumer = EventConsumer(consumer_conf, hanlder, shutdown);
    
    consumer.run()
    

def new_reader(conf):
    # later we may change reader with other (better) one
    # but this time we starts with Zbar
    log.info("creating ZbarReader")
    return ZbarReader(conf["zbar"])


if __name__ == '__main__':
    main()
