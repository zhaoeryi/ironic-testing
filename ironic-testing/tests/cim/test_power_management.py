#!/usr/bin/python
import os, re, json, sys
import string
from tests import base
 
class TestPowerManagement(base.BaseTestCase):
    
    def setUp(self):
        super(TestPowerManagement, self).setUp()

    def test_dm_get_chassis_list(self):
        str_svc_name = 'CIM_PowerManagementService'
        #print 'Get Instance Name of ', str_svc_name, '...'
        names = self.conn.EnumerateInstanceNames(str_svc_name)[0]
        print names

# This enables a test to be run from a command line
if __name__ == '__main__':
    base.main()

