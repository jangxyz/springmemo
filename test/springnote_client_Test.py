#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from lib.pythonmock.mock import Mock
import os, sys

import springnote_client

class OAuthTestCase(unittest.TestCase):
    def setUp(self):
        self.client = springnote_client.SpringnoteClient()

    def test_oauth_consumer_token(self):
        ''' SpringnoteClient should have OAuthConsumer instance consumer,
            that have correct consumer token and consumer token secret '''
        self.assertEqual(self.client.consumer.key, springnote_client.SpringnoteClient.CONSUMER_TOKEN)
        self.assertEqual(self.client.consumer.secret, springnote_client.SpringnoteClient.CONSUMER_TOKEN_SECRET)

    def test_requesting_for_request_token_sends_proper_data(self):
        """ request token을 가져오기 위해 적당한 데이터가 입력되었는지 확인한다 """
        oauth_request = self.client.create_oauth_request_for_request_token()
        self.assertEqual(oauth_request.http_method, "POST")
        self.assertEqual(oauth_request.http_url,    'https://api.springnote.com/oauth/request_token')
        self.assertTrue('oauth_consumer_key' in oauth_request.parameters.keys())
        
    def test_fetching_request_token_receives_proper_data(self):
        springnote_client.httplib = Mock({
            'HTTPSConnection': Mock({
                'request': '123',
                'getresponse': Mock({'read': "oauth_token=cd&oauth_token_secret=ab&open_id=http%3A%2F%2Fchanju.myid.net%2F"})
            })
        })         
            
        data = self.client.fetch_request_token()
        self.assertEqual(type(data), springnote_client.oauth.OAuthToken)
        self.assertEqual(type(data.key), str)
        self.assertEqual(type(data.secret), str)
        
    def test_fetching_request_token_raises_not_authorized_exception_when_token_is_wrong(self):
        """ raise exception when unauthorized """
        springnote_client.httplib = Mock({
            'HTTPSConnection': Mock({
                'request': '123',
                'getresponse': Mock({'read': "Invalid OAuth Request (signature_invalid, base string: POST&https%3A%2F%2Fapi.springnote.com%2Foauth%2Frequest_token&oauth_consumer_key%3Dsome%252Bconsumer%252Btoken%252Bkey%26oauth_nonce%3D39982135%26oauth_signature_method%3DHMAC-SHA1%26oauth_timestamp%3D1234870498%26oauth_version%3D1.0)"})
            })
        })         
        
        self.assertRaises(springnote_client.SpringnoteError.NotAuthorized, self.client.fetch_request_token)


    def test_requesting_for_access_token_sends_proper_data(self):
        springnote_client.httplib = Mock({
            'HTTPSConnection': Mock({
                'request': '123',
                'getresponse': Mock({'read': "oauth_token=cd&oauth_token_secret=ab&open_id=http%3A%2F%2Fchanju.myid.net%2F"})
            })
        })
        data = self.client.fetch_request_token()
        oauth_request = self.client.create_oauth_request_for_access_token(data)
        self.assertEqual(oauth_request.http_method, "POST")
        self.assertEqual(oauth_request.http_url, 'https://api.springnote.com/oauth/access_token')
        self.assertTrue('oauth_consumer_key' in oauth_request.parameters.keys())
        self.assertTrue('oauth_token' in oauth_request.parameters.keys())
        
    def test_fetching_access_token_receives_proper_data(self):
        springnote_client.httplib = Mock({
            'HTTPSConnection': Mock({
                'request': '123',
                'getresponse': Mock({'read': "oauth_token=we&oauth_token_secret=fk&open_id=http%3A%2F%2Fchanju.myid.net%2F"})
            })
        })         
            
        request_token = self.client.fetch_request_token()
        data = self.client.fetch_access_token(request_token)
        self.assertEqual(type(data), springnote_client.oauth.OAuthToken)
        self.assertEqual(type(data.key), str)
        self.assertEqual(type(data.secret), str)
        
        
    def test_oauth_directly_set_access_token(self):
        """ should directly set access token """
        key    = "yzlqEHF22FmATMyh72TxsA"
        secret = "uFHI07nwCMD6XK5ilaR8WuHsJUx4jL9q6V9vgn240"
        access_token = self.client.set_access_token_directly(key,secret)

        self.assertEqual(type(access_token), springnote_client.oauth.OAuthToken)
        self.assertEqual(type(self.client.access_token), springnote_client.oauth.OAuthToken)
        self.assertEqual(access_token.key, self.client.access_token.key)
        self.assertEqual(access_token.secret, self.client.access_token.secret)



class SpringnoteClientTestCase(unittest.TestCase):
    def setUp(self):
        connection_mock = Mock({
            'request': '123',
            'getresponse': Mock({'read': "oauth_token=we&oauth_token_secret=fk&open_id=http%3A%2F%2Fchanju.myid.net%2F"})
        })

        springnote_client.httplib = Mock({
            'HTTPSConnection': connection_mock,
            'HTTPConnection':  connection_mock
        })
        
        self.client = springnote_client.SpringnoteClient()

        request_token = self.client.fetch_request_token()
        data = self.client.fetch_access_token(request_token)
        self.access_token = data

        self.id = 2775538
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

        self.newjsons = '''
        {"page": {
                "rights": null,
                "source": "none sourceedited",
                "creator": "http://deepblue.myid.net/",
                "date_created": "2007/10/26 05:30:08 +0000",
                "contributor_modified": "http://deepblue.myid.net/",
                "date_modified": "2008/01/08 10:55:36 +0000",
                "relation_is_part_of": 1,
                "identifier": %d,
                "tags": "testedited",
                "title": "TestPageedited"
        }}''' % self.id

    def set_httplib_http_connection_mock_with_response_data(self, response_data):
        springnote_client.httplib = Mock({
            'HTTPConnection': Mock({
                'request': '123',
                'getresponse': Mock({'read': response_data})
            })
        })


    def test_get_page_with_id(self):
        self.set_httplib_http_connection_mock_with_response_data(self.jsons)

        page = self.client.get_page(self.id)
        self.assertTrue(isinstance(page, springnote_client.Page))
        self.assertEqual(page.identifier, self.id)


    def test_get_page_with_tag(self):
        tag = "sometag"
        page = self.client.get_page_with_tag(tag)
        self.assertTrue(isinstance(page,springnote_client.Page))
        self.assertTrue(tag in page.tags)

    def test_get_page_should_ask_for_correct_url(self):
        pass

    def test_create_page(self):
        self.set_httplib_http_connection_mock_with_response_data(self.jsons)

        title, body = 'TestPage', 'none source'
        page = self.client.create_page(title=title,source=body,domain="loocaworld")

        call = springnote_client.httplib.mockGetNamedCalls("HTTPConnection")[0]
        self.assertEqual(call.getName(), "HTTPConnection")
        self.assertEqual(call.getParam(0), "api.springnote.com:80")

        self.assertTrue( isinstance(page, springnote_client.Page ))
        self.assertNotEqual( page.identifier, None )
        self.assertEqual( page.title, title )
        self.assertEqual( page.source, body )


    def test_create_page_raises_cannot_create_page_exception_when_already_same_title(self):
        returnbody = '{"errors":[{"title": "name", "description": "has already been taken"}]}'
        self.set_httplib_http_connection_mock_with_response_data(returnbody)

        title, body = 'TestPage', 'none source'
        self.assertRaises(springnote_client.SpringnoteError.CannotCreatePage, \
                          self.client.create_page, title=title,source=body,domain="loocaworld")


    def test_create_page_raises_invalid_oauth_request_exception_when_init_with_wrong_access_token(self):
        returnbody = '''
            [{
                "error": {
                    "error_type": "InvalidOauthRequest", 
                    "description": "signature_invalid, base string: POST\u0026http%3A%2F%2Fapi.springnote.com%2Fpages.json\u0026domain%3Dloocaworld%26oauth_consumer_key%3Dwp%26oauth_nonce%3D63%26oauth_signature_method%3DHMAC-SHA1%26oauth_timestamp%3D1235461259%26oauth_token%3DFHk%26oauth_version%3D1.0"
                }
            }]
        '''
        self.set_httplib_http_connection_mock_with_response_data(returnbody)

        title, body = 'TestPage', 'none source'
        altclient = springnote_client.SpringnoteClient()
        altclient.set_access_token_directly("wrong key","wrong secret")

        self.assertRaises(springnote_client.SpringnoteError.InvalidOauthRequest, altclient.create_page,title=title,source=body,domain="loocaworld")


    def test_from_jsons(self):
        newpage = springnote_client.Page.from_jsons(self.newjsons)

        self.assertEqual(newpage.rights, None)
        self.assertEqual(newpage.source, "none sourceedited")
        self.assertEqual(newpage.creator, "http://deepblue.myid.net/")
        self.assertEqual(newpage.contributor_modified, "http://deepblue.myid.net/")
        self.assertEqual(newpage.date_created, springnote_client.datetime.strptime("2007/10/26 05:30:08 +0000","%Y/%m/%d %H:%M:%S +0000"))
        self.assertEqual(newpage.date_modified, springnote_client.datetime.strptime("2008/01/08 10:55:36 +0000","%Y/%m/%d %H:%M:%S +0000"))
        self.assertEqual(newpage.relation_is_part_of, 1)
        self.assertEqual(newpage.identifier, self.id)
        self.assertEqual(newpage.tags, ["testedited"])
        self.assertEqual(newpage.title, "TestPageedited")
    
#### getpage 쪽도 에러 처리 해줘야 할 듯


    def test_update_page_with_id(self):
        self.set_httplib_http_connection_mock_with_response_data(self.newjsons)
        newpage = springnote_client.Page.from_jsons(self.newjsons)
        title, body = 'TestPage', 'none source'

        # update page
        page = self.client.update_page(page=newpage, domain="loocaworld")

        # should call httplib.HTTPConnection
        call = springnote_client.httplib.mockGetNamedCalls("HTTPConnection")[0]
        self.assertEqual(call.getName(),"HTTPConnection")
        self.assertEqual(call.getParam(0),"api.springnote.com:80")
        self.assertTrue( isinstance(page, springnote_client.Page ))

        # XXX: should ???
        self.assertNotEqual( page.identifier, None )
        self.assertEqual( page.title,  newpage.title )
        self.assertEqual( page.source, newpage.source )

    def test_delete_page_with_id(self):
        '''
        self.id로 delete_page 하면 그 return값은 self.id의 page와 동일해야 함
        '''
        self.set_httplib_http_connection_mock_with_response_data(self.newjsons)
        newpage = springnote_client.Page.from_jsons(self.newjsons)

        # delete page
        page = self.client.delete_page(id=self.id, domain="loocaworld")

        # should call HTTPConnection
        call = springnote_client.httplib.mockGetNamedCalls("HTTPConnection")[0]
        self.assertEqual(call.getName(),"HTTPConnection")
        self.assertEqual(call.getParam(0),"api.springnote.com:80")
        self.assertTrue( isinstance(page, springnote_client.Page ))

        # XXX: should ???
        self.assertNotEqual( page.identifier, None )
        self.assertEqual( page.title, newpage.title )
        self.assertEqual( page.source, newpage.source )

    def test_delete_page_raises_page_not_found_exception_when_calls_twice(self):
        '''
        self.id로 delete_page 한 뒤에 get_page 하면 에러를 뿜어내야 함
        '''
        self.set_httplib_http_connection_mock_with_response_data(self.newjsons)
        newpage = springnote_client.Page.from_jsons(self.newjsons)
        page = self.client.delete_page(id=self.id,domain="loocaworld")

        errorjsons = '''
            [{"error": {"error_type": "NotFound", "description": "NotFound"}}]
        '''
        self.set_httplib_http_connection_mock_with_response_data(errorjsons)

        # deleting page twice should rais error
        self.assertRaises(springnote_client.SpringnoteError.PageNotFound, self.client.delete_page,id=self.id,domain="loocaworld")


class SpringnotePageClassTestCase(unittest.TestCase):
    def setUp(self):
        self.json = '''{"page": {
            "rights": null,
            "source": "none source",
            "creator": "http://deepblue.myid.net/",
            "date_created": "2007/10/26 05:30:08 +0000",
            "contributor_modified": "http://deepblue.myid.net/",
            "date_modified": "2008/01/08 10:55:36 +0000",
            "relation_is_part_of": 1,
            "identifier": 4,
            "tags": "test",
            "title": "TestPage"
        }}'''


    def test_create_page_without_parameters_has_attributes(self):
        p = springnote_client.Page()
        attrset = ["rights", "source", "creator", "date_created", "contributor_modified", "date_modified", "relation_is_part_of", "identifier", "tags", "title"]
        for attr_name in attrset:
            self.assertTrue(hasattr(p, attr_name))        


    def test_create_page_with_from_jsons_method(self):
        p = springnote_client.Page.from_jsons(self.json)

        self.assertTrue(isinstance(p, springnote_client.Page))
        self.assertEqual(p.identifier, 4)
        self.assertEqual(p.source, "none source")
        self.assertTrue(isinstance(p.date_created,        springnote_client.datetime))
        self.assertTrue(isinstance(p.date_modified,       springnote_client.datetime))
        self.assertTrue(isinstance(p.identifier,          int))
        self.assertTrue(isinstance(p.relation_is_part_of, int))


    def test_parse_json_and_saves_key_as_attributes(self):
        p = springnote_client.Page()
        p.update_from_jsons(self.json)

        self.assertEqual(p.identifier,4)
        self.assertEqual(p.source,"none source")
        self.assertEqual(type(p.date_created), springnote_client.datetime)
        self.assertEqual(type(p.date_modified),springnote_client.datetime)
        self.assertEqual(type(p.identifier),int)
        self.assertEqual(type(p.relation_is_part_of),int)



class JsonImportExportTestCase(unittest.TestCase):
    def setUp(self):
        self.o = [1, 2, 3, None, False, {"a": "def"}]
        self.s = '''[1, 2, 3, null, false, {"a": "def"}]'''


    def test_parse_json_string_into_object(self):
        self.assertEqual( springnote_client.json.loads(self.s), self.o )


    def test_parse_object_into_json_string(self):
        self.assertEqual( springnote_client.json.dumps(self.o), self.s)


    def test_parse_datetime_to_json(self):
        now = springnote_client.datetime.strptime("2007/10/26 05:30:08 +0000","%Y/%m/%d %H:%M:%S +0000")
        self.assertEqual(springnote_client.json.dumps(now), '"2007/10/26 05:30:08 +0000"')
        self.assertEqual(springnote_client.json.dumps([1,2,True]), '[1, 2, true]')


class ExceptionTestCase(unittest.TestCase):
    pass
    #def test_not_found(self):
    #    """ requesting for resource that does not exist should raise NotFound error """
    #    some_function = lambda x: x
    #    self.assertRaises(SpringnoteError.NotFound, some_function)


if __name__ == '__main__':
    #unittest.main(defaultTest=suite())
    loader = unittest.defaultTestLoader
    loader.testMethodPrefix = 'test'
    unittest.main(testLoader = loader)


