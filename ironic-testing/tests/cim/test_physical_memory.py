#!/usr/bin/python
import os, re, json, sys
import string
from tests import base
import pprint

class TestPhysicalMemory(base.BaseTestCase):
    
    def setUp(self):
        super(TestPhysicalMemory, self).setUp()

    def test_get_all_memories(self):
        # print 'Get Instance Name of ', str_svc_name, '...'
        memories = self.conn.EnumerateInstances('CIM_PhysicalMemory')
        for mem in memories:
            pprint.pprint(mem)
            
        
# This enables a test to be run from a command line
if __name__ == '__main__':
    base.main()

