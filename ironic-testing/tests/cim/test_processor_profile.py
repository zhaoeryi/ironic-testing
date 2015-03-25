#!/usr/bin/python
import os, re, json, sys
import string
from tests import base
import pprint

class TestCPUProfile(base.BaseTestCase):
    
    def setUp(self):
        super(TestCPUProfile, self).setUp()

    def test_get_all_processors(self):
        #print 'Get Instance Name of ', str_svc_name, '...'
        processors = self.conn.EnumerateInstances('CIM_Processor')
        for processor in processors:
            print processor
            numberic_sensors = self.conn.Associators(processor.path)
            pprint.pprint(numberic_sensors)
            
        
# This enables a test to be run from a command line
if __name__ == '__main__':
    base.main()

