#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from lib.pythonmock.mock import Mock
import os, sys

import springmemo

class SpringMemoCase(unittest.TestCase):
    def setUp(self):
        app = springmemo.wx.App()
        self.mainapp = springmemo.SpringMemo()
    def test_exist_springmemo_instance(self):
        self.assertTrue(isinstance(self.mainapp,springmemo.SpringMemo))
#        print self.mainapp



if __name__ == "__main__":
    loader = unittest.defaultTestLoader
    loader.testMethodPrefix = 'test'
    unittest.main(testLoader = loader)
