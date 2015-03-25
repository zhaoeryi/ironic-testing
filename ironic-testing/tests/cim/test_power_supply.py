#!/usr/bin/python
import os, re, json, sys
import string
from tests import base
import pprint

class TestPowerSupply(base.BaseTestCase):
    
    def setUp(self):
        super(TestPowerSupply, self).setUp()

    def test_get_all_powersupplies(self):
        # print 'Get Instance Name of ', str_svc_name, '...'
        powers = self.conn.EnumerateInstances('CIM_PowerSupply')
        for power in powers:
            pprint.pprint(power)
            physical_pkgs = self.conn.Associators(power.path, AssocClass='CIM_Realizes', ResultClass='CIM_PhysicalPackage', Role='Dependent', ResultRole='Antecedent')
            for pkg in physical_pkgs:
                pprint.pprint(pkg.items())
            
        
# This enables a test to be run from a command line
if __name__ == '__main__':
    base.main()

