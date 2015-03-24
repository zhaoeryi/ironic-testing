import os
import ConfigParser
import sys

class ConfigOpts(object):
    def __init__(self):
        pass
    
    def setup(self):
        base_dir =  os.path.dirname(os.path.abspath(__file__))
        conf_file = os.path.join(base_dir, "systest.conf")
            
        cp = ConfigParser.RawConfigParser()
        cp.read(conf_file)
            
        self.url = cp.get("CIM", "url")
        self.userid = cp.get("CIM", "userid")
        self.password = cp.get("CIM", "password")       
        self.namespace = cp.get("CIM", "namespace")      

