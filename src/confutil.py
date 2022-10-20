import yaml

import logging
import logging.config
import os


class ConfUtil:
    
    def __init__(self, conf_path, log_path):
        self.conf = None
        self.done = False
        
        self.init_conf(conf_path)
        if self.conf == None:
            return
        
        self.done = self.init_log(log_path)
   
    def is_good(self):
        return self.done
    
    def get_conf(self):
        return self.conf    
        
    def init_conf(self, path):
        print('read conf_path', path)
        try:
            self.conf = yaml.safe_load(self.__load_file(path))
        except Exception as e:
            print(e)
    
    def __load_file(self, path):
        if not path:
            print('exit. empty path')
            return
        try:
            with open(path, 'rt') as f:
                return f.read()
        except FileNotFoundError as e:
            print(e)   
            
    def init_log(self, path):
        print('read log_path', path)
        try:
            config = yaml.safe_load(self.__load_file(path))
            logging.config.dictConfig(config)
        except Exception as e:
            print(e)
            return False
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
    
