#!/usr/bin/python
import os, re, json, sys
import string
from tests import base
import pprint

class TestFanProfile(base.BaseTestCase):
    
    def setUp(self):
        super(TestFanProfile, self).setUp()

    def test_get_all_fans(self):
        # print 'Get Instance Name of ', str_svc_name, '...'
        fans = self.conn.EnumerateInstances('CIM_Fan')
        for fan in fans:
            pprint.pprint(fan.items())
            fan_sensors = self.conn.Associators(fan.path, AssocClass='CIM_AssociatedSensor', ResultClass='CIM_NumericSensor', Role='Dependent', ResultRole='Antecedent')
            pprint.pprint(fan_sensors)
            
        
# This enables a test to be run from a command line
if __name__ == '__main__':
    base.main()

