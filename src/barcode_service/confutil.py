import yaml

import logging
import logging.config
import os
import sys


class ConfUtil:
    
    def __init__(self, conf_path, log_path):
        self.conf = None
        self.done = False
        
        self.init_conf(conf_path)
        self.done = self.init_log(log_path)
   
    def is_good(self):
        return self.done
    
    def get_conf(self):
        return self.conf    
        
    def init_conf(self, path):
        print(f'read config from:{path}')
        self.conf = yaml.safe_load(self.__load_file(path))
        
    
    def __load_file(self, path):
        if not path:
            print('exit because path is empty')
            sys.exit(1)
        
        with open(path, 'rt') as f:
            return f.read()
            
    def init_log(self, path):
        print(f'read log config from:{path}')
        config = yaml.safe_load(self.__load_file(path))
        logging.config.dictConfig(config)
        return True
    

confutil = None


def single_conf(env):
    return single_confutil(env).conf


def single_confutil(env):
    global confutil
    if confutil != None:
        return confutil
    
    if env:
        env = "-" + env
    else:
        env = ""

    print(f"env:{env}")        
    conf_path = f"conf{env}.yaml"
    log_path = f"log{env}.yaml"
    
    print(f"single_confutil. new ConfUtil. conf_path:{conf_path}, log_path:{log_path}")
    temp = ConfUtil(conf_path, log_path)
    
    if temp.is_good() == False:
        print("ERROR. failed ConfUtil and it exits now")
        exit()
    
    print("finished single_confutil")
    confutil = temp
    return confutil
    
