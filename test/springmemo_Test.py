#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from lib.pythonmock.mock import Mock
import os, sys

import springmemo
import springnote_client
import notegui


class SpringMemoCase(unittest.TestCase):
    def setUp(self):
        self.app = springmemo.wx.App()
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


        self.jsons_root_page = '''
            {"page": {
                "rights": null,
                "source": "none source",
                "creator": "http://deepblue.myid.net/",
                "date_created": "2007/10/26 05:30:08 +0000",
                "contributor_modified": "http://deepblue.myid.net/",
                "date_modified": "2008/01/08 10:55:36 +0000",
                "relation_is_part_of": 1,
                "identifier": %d,
                "tags": %s,
                "title": %s
            }}
        ''' % (self.id,springnote_client.SpringnoteClient.DEFAULT_ROOT_TAG,springnote_client.SpringnoteClient.DEFAULT_ROOT_TITLE)




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
    
    def test_creating_a_new_memo_instance(self):
        ''' 새 메모가 생성되고 springmemo.memos list에 push된다 '''
        ''' memo.page와 memo.view가 정상적이다 '''
        self.set_httplib_http_connection_mock_with_response_data(self.jsons)

        title = "TestPage"
        type = springmemo.MEMO_TYPE_NORMAL

        memo = self.mainapp.create_new_memo(type,title,rel=None)
        self.assertTrue(isinstance(memo, springmemo.Memo))
        self.assertEqual(self.mainapp.memos[0], memo)
        self.assertEqual(title, memo.page.title)
        self.assertTrue(isinstance(memo.view,notegui.NormalNote))

    def test_user_authorize_set_page_client(self):
        ''' 인증 초기에 Page.client이 적절히 들어온다 '''
        self.assertTrue(isinstance(springnote_client.Page.client,springnote_client.SpringnoteClient))

#    def test_initializing_all_memos(self):
#        self.mainapp.init_all_memos()
#        self.assertTrue(isinstance(self.mainapp.rootmemo,springmemo.Memo))

    def test_get_root_memo_parses_jsons_correctly(self):
        pass


### Memo ###

class MemoCase(unittest.TestCase):
    def setUp(self):
        self.app = springmemo.wx.App()
        self.mainapp = springmemo.SpringMemo()
        self.mainapp.user_authorize()

#        self.set_default_mock()

    def test_get_root_memo_returns_correct_root_memo(self):
        rootmemo = springmemo.Memo.get_root_memo()
        print "title:%s" % rootmemo.page.title
        print "tags:%s" % rootmemo.page.tags
        self.assertTrue(isinstance(rootmemo,springmemo.Memo))
        self.assertTrue(isinstance(rootmemo.page,springnote_client.Page))
#        self.assertEqual(rootmemo.page.tags,springnote_client.SpringnoteClient.DEFAULT_ROOT_TAG)
#        self.assertEqual(rootmemo.page.title,springnote_client.SpringnoteClient.DEFAULT_ROOT_TITLE)
        self.assertEqual(unicode(rootmemo.page.title,'utf-8'),unicode(springnote_client.SpringnoteClient.DEFAULT_ROOT_TITLE,'utf-8'))


class PageHeader(unittest.TestCase):
    def setUp(self):
        self.is_open = True
        self.type = springmemo.MEMO_TYPE_NORMAL
        self.source = '''
<div id="body">
this is real body.<br />
and this is a text.<br />
</div>
Here is a HIDDEN header for 
<div id="page_header"><p id="is_open">%s</p><p id="type">%d</p></div>
SpringMemo! Don't delete this line PLEASE :)
        ''' % (str(self.is_open),self.type)

    def test_parsing_header_from_source(self):
        header = springmemo.PageHeader.parse_header_from_source(self.source)

        self.assertEqual(header.is_open,self.is_open)
        self.assertEqual(header.type,self.type)
        self.assertTrue(isinstance(header.type,int))

    def test1_making_source_from_header(self):
        header = springmemo.PageHeader()
        header.is_open = True
        header.type = 1
        header_str = "<div id=\"page_header\" style=\"display:none;\"><p id=\"is_open\">%s</p><p id=\"type\">%s</p></div>" % (header.is_open, header.type)

        result_str = header.make_source_from_header()
        header2 = springmemo.PageHeader.parse_header_from_source(result_str)

        self.assertEqual(header_str,result_str)
        self.assertEqual(header2.is_open,header.is_open)
        self.assertEqual(header2.type,header.type)


### Run ###

if __name__ == "__main__":
    loader = unittest.defaultTestLoader
    loader.testMethodPrefix = 'test1'
    unittest.main(testLoader = loader)

