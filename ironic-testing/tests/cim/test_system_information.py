#!/usr/bin/python
import os, re, json, sys
import string
from tests import base
import pprint

class TestSystemInformation(base.BaseTestCase):
    
    def setUp(self):
        super(TestSystemInformation, self).setUp()

    def build_identifying_dict(self, arr_identifying_descriptions, arr_identifying_info):
        pairs = {}
        for i in range(len(arr_identifying_descriptions)):
            pairs[arr_identifying_descriptions[i]] = arr_identifying_info[i]
        return pairs
    
    def get_system_chassis_instance(self, computer):
        chs = self.conn.Associators (computer.path, AssocClass='CIM_ComputerSystemPackage', ResultClass='IBM_Chassis', Role='Dependent', ResultRole='Antecedent')
        if (len(chs) == 0):
            raise Exception("No instances of System 'CIM_Chassis' found")

        if (len(chs) > 1):
            print ("Too many associated Chassis 'CIM_Chassis' found returning first");
                
        chassis = chs[0]
        
        return chassis
                 
    def get_chassis_uuid(self, computer):
        identifying_dict = self.build_identifying_dict(computer['IdentifyingDescriptions'], computer['OtherIdentifyingInfo'])
        uuid = identifying_dict['CIM:GUID']
        
        return uuid
              
    def test_get_system_information(self):
        sysinfo = {}

        # get computer system
        computers = self.conn.EnumerateInstances('IBM_ComputerSystem')
        if(len(computers) == 0):
            raise Exception("No instances of 'IBM_ComputerSystem' found")
        computer = computers[0]
        pprint.pprint(computer.items())
        
        # get chassis
        chs = self.get_system_chassis_instance(computer)
        pprint.pprint(chs.items())
        
        # mix up
        sysinfo['machine_name'] = 'tbd'
        sysinfo['machine_type_model'] = chs['Model']
        sysinfo['serial_number'] = chs['SerialNumber']
        sysinfo['uuid'] = self.get_chassis_uuid(computer)
        sysinfo['server_power'] = 'tbd'
        sysinfo['server_state'] = 'tbd'
        sysinfo['total_hours_powered_on'] = 'tbd'
        sysinfo['restart_count'] = computer['NumberOfReboots']
        sysinfo['ambient_temperature'] = 'tbd'
        sysinfo['enclosure_identify_led'] = 'tbd'
        sysinfo['check_log_led'] = 'tbd'
        
        pprint.pprint(sysinfo.items())
        
# This enables a test to be run from a command line
if __name__ == '__main__':
    base.main()

