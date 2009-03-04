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
        self.assertEqual(type(self.mainapp.memos),type([]))
#        print self.mainapp
    
    def test_create_new_memo(self):
        ''' 새 메모가 생성되고 springmemo.memos list에 push된다 '''
        title = "imsi title"
        type = springmemo.MEMO_TYPE_NORMAL

        memo = self.mainapp.create_new_memo(type,title)

class MemoCase(unittest.TestCase):
    def setUp(self):
        pass

    def test_create_new_memo(self):
        ''' 새 메모가 생성돠고 그 안으 데이터가 올바르다 '''
        type = springmemo.MEMO_TYPE_NORMAL
        title = "imsi title"
        memo = springmemo.Memo(type,title)



if __name__ == "__main__":
    loader = unittest.defaultTestLoader
    loader.testMethodPrefix = 'test'
    unittest.main(testLoader = loader)
