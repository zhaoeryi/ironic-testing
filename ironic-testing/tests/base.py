from __future__ import print_function

import json
import os
import sys
import time
import unittest

from config import ConfigOpts
from pywbem import *


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        """Run before each test method to initialize test environment."""
        super(BaseTestCase, self).setUp()
        
        print("======================================================================")
        print("[Test Case] %s" % self._testMethodName)
        
        self.start = time.time()
         
        self.config = ConfigOpts()
        self.config.setup()
        
        self.conn = WBEMConnection(self.config.url, creds=(self.config.userid, self.config.password), default_namespace=self.config.namespace)

    def tearDown(self):
        super(BaseTestCase, self).tearDown()
        
        end = time.time()
        msg = ('[Test Case] end, taking %s seconds.' % ("%.1f" % (end - self.start)))
        print(msg)

def main():
    unittest.main()
