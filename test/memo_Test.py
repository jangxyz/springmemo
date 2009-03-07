#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from lib.pythonmock.mock import Mock
import os, sys

import springmemo


class MemoCase(unittest.TestCase):
    def setUp(self):
        pass

    def test1_create_new_memo(self):
        ''' 새 메모가 생성돠고 그 안으 데이터가 올바르다 '''
        type = springmemo.MEMO_TYPE_NORMAL
        title = "imsi title"
        memo = springmemo.Memo(type,title)

    def test_get_root_memo_returns_root_page(self):
        ''' root page가 존재하면 해당 memo를 리턴한다 '''
        root_memo = springmemo.Memo.get_root_memo()
        self.assertTrue('springmemorootpage' in root_memo.page.tags)


if __name__ == "__main__":
    loader = unittest.defaultTestLoader
    loader.testMethodPrefix = 'test1'
    unittest.main(testLoader = loader)

