#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from lib.pythonmock.mock import Mock
import os, sys

import springmemo
import springnote_client


class SpringMemoCase(unittest.TestCase):
    def setUp(self):
        app = springmemo.wx.App()
        self.mainapp = springmemo.SpringMemo()
        self.mainapp.user_authorize()

        self.set_default_mock()

    def set_default_mock(self):
        connection_mock = Mock({
            'request': '123',
            'getresponse': Mock({'read': "oauth_token=we&oauth_token_secret=fk&open_id=http%3A%2F%2Fchanju.myid.net%2F"})
        })

        springnote_client.httplib = Mock({
            'HTTPSConnection': connection_mock,
            'HTTPConnection':  connection_mock
        })

        self.id = 2775538
        self.tag = "sometag"
        self.jsons = '''
            {"page": {
                "rights": null,
                "source": "none source",
                "creator": "http://deepblue.myid.net/",
                "date_created": "2007/10/26 05:30:08 +0000",
                "contributor_modified": "http://deepblue.myid.net/",
                "date_modified": "2008/01/08 10:55:36 +0000",
                "relation_is_part_of": 1,
                "identifier": %d,
                "tags": "test",
                "title": "TestPage"
            }}
        ''' % self.id




    def set_httplib_http_connection_mock_with_response_data(self,response_data):
        springnote_client.httplib = Mock({
            'HTTPConnection': Mock({
                'request': '123',
                'getresponse': Mock({'read': response_data})
            })
        })

    def test_exist_springmemo_instance(self):
        """ springmemo가 잘 만들어졌다 """
        self.assertTrue(isinstance(self.mainapp,springmemo.SpringMemo))
        self.assertEqual(type(self.mainapp.memos),type([]))
    
    def test1_creating_a_new_memo_instance(self):
        ''' 새 메모가 생성되고 springmemo.memos list에 push된다 '''
        ''' memo.page와 memo.view가 정상적이다 '''
        self.set_httplib_http_connection_mock_with_response_data(self.jsons)

        title = "TestPage"
        type = springmemo.MEMO_TYPE_NORMAL

        memo = self.mainapp.create_new_memo(type,title,rel=None)
        self.assertTrue(isinstance(memo, springmemo.Memo))
        self.assertEqual(self.mainapp.memos[0], memo)
        self.assertEqual(title, memo.page.title)
#        self.assertTrue(isinstance(memo.view,notegui.Note))

    def test_user_authorize_set_page_client(self):
        ''' 인증 초기에 Page.client이 적절히 들어온다 '''
        self.assertTrue(isinstance(springnote_client.Page.client,springnote_client.SpringnoteClient))


if __name__ == "__main__":
    loader = unittest.defaultTestLoader
    loader.testMethodPrefix = 'test1'
    unittest.main(testLoader = loader)

