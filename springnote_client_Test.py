#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from mock import Mock
import os, sys
#from springnote_client import SpringnoteClient, httplib
import springnote_client
#import simplejson as json
#import lib.simplejson as json
import lib.json as json


from datetime import datetime
#import oauth

class OAuthTestCase(unittest.TestCase):
    def setUp(self):
        self.consumer_token, self.consumer_token_secret = 'some consumer token key', 'some consumer secret'
        #auth = OAuth(consumer_token, consumer_token_secret)
        self.client = springnote_client.SpringnoteClient(self.consumer_token, self.consumer_token_secret)

    def test_oauth_consumer_token(self):
        ''' SpringnoteClient should have OAuthConsumer instance consumer,
            that have correct consumer token and consumer token secret '''
        #self.assertEqual(self.client.consumer, oauth.OAuthConsumer(self.consumer_token, self.consumer_token_secret))
        self.assertEqual(self.client.consumer.key, self.consumer_token)
        self.assertEqual(self.client.consumer.secret, self.consumer_token_secret)
        #self.assertEqual(type(self.client.consumer), oauth.OAuthConsumer)

    def test_requesting_for_request_token_sends_proper_data(self):
        """ request token을 가져오기 위해 적당한 데이터가 입력되었는지 확인한다 """
        oauth_request = self.client.create_oauth_request_for_request_token()
        self.assertEqual(oauth_request.http_method, "POST")
        self.assertEqual(oauth_request.http_url,    'https://api.springnote.com/oauth/request_token')
        self.assertTrue('oauth_consumer_key' in oauth_request.parameters.keys())
        #self.assertEqual(oauth_request.parameters['oauth_consumer_key'], self.client.consumer.key)
        
    def test_fetching_request_token_receives_proper_data(self):
        """  """
        #https_connection = Mock("httplib.HTTPSConnection")
        #https_connection.mock_returns = Mock("connection")
        #https_connection.mock_returns.getresponse.mock_returns = Mock("response")
        #https_connection.mock_returns.getresponse.mock_returns.read.mock_returns = "oauth_token=cd&oauth_token_secret=ab&open_id=http%3A%2F%2Fchanju.myid.net%2F"

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


    #def test_authorize_url(self):
    #    url = self.client.authorize_url()



    # url test

    



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
        
        

    #def test_oauth_access_token(self):
    #    """ should fetch the access token and make it a valid access token """
    #    #self.client.access_token = None
    #    #self.assertEqual(type(self.client.access_token), springnote_client.oauth.OAuthToken)
        
    # todo
    def test_oauth_directly_set_access_token(self):
        """ should directly set access token """
        key = "yzlqEHF22FmATMyh72TxsA"
        secret = "uFHI07nwCMD6XK5ilaR8WuHsJUx4jL9q6V9vgn240"
#        self.client.access_token = springnote_client.oauth.OAuthToken(token, key)
        access_token = self.client.set_access_token_directly(key,secret)
        self.assertEqual(type(access_token), springnote_client.oauth.OAuthToken)
        self.assertEqual(type(self.client.access_token), springnote_client.oauth.OAuthToken)
        self.assertEqual(access_token.key, self.client.access_token.key)
        self.assertEqual(access_token.secret, self.client.access_token.secret)



class SpringnoteClientTestCase(unittest.TestCase):
    def setUp(self):
        xml = open("./test.xml").read()
        springnote_client.httplib = Mock({
            'HTTPSConnection': Mock({
                'request': '123',
                'getresponse': Mock({'read': "oauth_token=we&oauth_token_secret=fk&open_id=http%3A%2F%2Fchanju.myid.net%2F"})
            }),
            'HTTPConnection': Mock({
                'request': '123',
                'getresponse': Mock({'read': "oauth_token=we&oauth_token_secret=fk&open_id=http%3A%2F%2Fchanju.myid.net%2F"})
            })
        })
        
        self.consumer_token, self.consumer_token_secret = 'some consumer token key', 'some consumer secret'
        #auth = OAuth(consumer_token, consumer_token_secret)
        self.client = springnote_client.SpringnoteClient(self.consumer_token, self.consumer_token_secret)

        request_token = self.client.fetch_request_token()
        data = self.client.fetch_access_token(request_token)
        self.access_token = data

#        self.id = 4
        self.id = 2775538
        self.jsons = '''{"page": {
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

    def test_get_page_with_id(self):

        springnote_client.httplib = Mock({
            'HTTPConnection': Mock({
                'request': '123',
                'getresponse': Mock({'read': self.jsons
                })
            })
        })

        page = self.client.get_page(self.id)
        self.assertTrue( isinstance(page, springnote_client.Page ))
        self.assertEqual(page.identifier, self.id)
#        self.assertEqual( type(), str)

    def test_create_page(self):

        springnote_client.httplib = Mock({
            'HTTPConnection': Mock({
                'request': '123',
                'getresponse': Mock({'read': self.jsons
                })
            })
        })

        title, body = 'TestPage', 'none source'
        page = self.client.create_page(title=title,source=body,domain="loocaworld")

        call = springnote_client.httplib.mockGetNamedCalls("HTTPConnection")[0]
        self.assertEqual(call.getName(),"HTTPConnection")
        self.assertEqual(call.getParam(0),"api.springnote.com:80")
        self.assertTrue( isinstance(page, springnote_client.Page ))
        self.assertNotEqual( page.identifier, None )
        self.assertEqual( page.title, title )
        self.assertEqual( page.source, body )

    def test_create_page_raises_cannot_create_page_exception_when_already_same_title(self):
        returnbody = '{"errors":[{"title": "name", "description": "has already been taken"}]}'

        springnote_client.httplib = Mock({
            'HTTPConnection': Mock({
                'request': '123',
                'getresponse': Mock({'read': returnbody})
            })
        })
        title, body = 'TestPage', 'none source'

        self.assertRaises(springnote_client.SpringnoteError.CannotCreatePage, self.client.create_page,title=title,source=body,domain="loocaworld")
    def test_create_page_raises_invalid_oauth_request_exception_when_init_with_wrong_access_token(self):
        returnbody = '''
            [{"error": {"error_type": "InvalidOauthRequest", "description": "signature_invalid, base string: POST\u0026http%3A%2F%2Fapi.springnote.com%2Fpages.json\u0026domain%3Dloocaworld%26oauth_consumer_key%3DwpRiJvvQy624FayfQ6Q%26oauth_nonce%3D63475398%26oauth_signature_method%3DHMAC-SHA1%26oauth_timestamp%3D1235461259%26oauth_token%3DFHksYUxDz5sNpxXZ3Yq9Qk%26oauth_version%3D1.0"}}]
        '''

        springnote_client.httplib = Mock({
            'HTTPConnection': Mock({
                'request': '123',
                'getresponse': Mock({'read': returnbody})
            })
        })
        title, body = 'TestPage', 'none source'
        altclient = springnote_client.SpringnoteClient(self.consumer_token, self.consumer_token_secret)
        altclient.set_access_token_directly("wrong key","wrong secret")
        self.assertRaises(springnote_client.SpringnoteError.InvalidSignature, altclient.create_page,title=title,source=body,domain="loocaworld")


    def test_from_jsons(self):
        newjsons = '''{"page": {
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
}}
        ''' % self.id

        newpage = springnote_client.Page.from_jsons(newjsons)
        self.assertEqual(newpage.rights, None)
        self.assertEqual(newpage.source, "none sourceedited")
        self.assertEqual(newpage.creator, "http://deepblue.myid.net/")
        self.assertEqual(newpage.contributor_modified, "http://deepblue.myid.net/")
        self.assertEqual(newpage.date_created, datetime.strptime("2007/10/26 05:30:08 +0000","%Y/%m/%d %H:%M:%S +0000"))
        self.assertEqual(newpage.date_modified, datetime.strptime("2008/01/08 10:55:36 +0000","%Y/%m/%d %H:%M:%S +0000"))
        self.assertEqual(newpage.relation_is_part_of, 1)
        self.assertEqual(newpage.identifier, self.id)
        self.assertEqual(newpage.tags, ["testedited"])
        self.assertEqual(newpage.title, "TestPageedited")
    
#### getpage 쪽도 에러 처리 해줘야 할 듯


    def test_update_page_with_id(self):
        
        newjsons = '''{"page": {
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
}}
        ''' % self.id

        newpage = springnote_client.Page.from_jsons(newjsons)

        springnote_client.httplib = Mock({
            'HTTPConnection': Mock({
                'request': '123',
                'getresponse': Mock({'read': newjsons
                })
            })
        })

        title, body = 'TestPage', 'none source'
        page = self.client.update_page(page=newpage,domain="loocaworld")

        call = springnote_client.httplib.mockGetNamedCalls("HTTPConnection")[0]
        self.assertEqual(call.getName(),"HTTPConnection")
        self.assertEqual(call.getParam(0),"api.springnote.com:80")
        self.assertTrue( isinstance(page, springnote_client.Page ))
        self.assertNotEqual( page.identifier, None )
        self.assertEqual( page.title, newpage.title )
        self.assertEqual( page.source, newpage.body )




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
}}
        '''
        self.attrset = ["rights", "source", "creator", "date_created", "contributor_modified", "date_modified", "relation_is_part_of", "identifier", "tags", "title"]
    def test_create_page_without_parameters_has_attributes(self):
        p = springnote_client.Page()
        for attr_name in self.attrset:
            self.assertTrue(attr_name in self.attrset)
        

    def test_parse_json_as_dictionary(self):
        p = springnote_client.Page()
        result = p.parse_json(self.json)
        page = springnote_client.Page.from_jsons(self.json)
        for attr_name in ["rights", "source", "creator", "date_created", "contributor_modified", "date_modified", "relation_is_part_of", "identifier", "tags", "title"]:
            self.assertTrue(hasattr(p,attr_name))


    def test_create_page_with_from_jsons_method(self):
        p = springnote_client.Page.from_jsons(self.json)
        self.assertTrue(isinstance(p,springnote_client.Page))
        self.assertEqual(p.identifier,4)
        self.assertEqual(p.source,"none source")
        self.assertEqual(type(p.date_created),datetime)
        self.assertEqual(type(p.date_modified),datetime)
        self.assertEqual(type(p.identifier),int)
        self.assertEqual(type(p.relation_is_part_of),int)


    def test_parse_json_and_saves_key_as_attributes(self):
        p = springnote_client.Page()
        p.parse_json(self.json)

        self.assertEqual(p.identifier,4)
        self.assertEqual(p.source,"none source")
        self.assertEqual(type(p.date_created),datetime)
        self.assertEqual(type(p.date_modified),datetime)
        self.assertEqual(type(p.identifier),int)
        self.assertEqual(type(p.relation_is_part_of),int)




class JsonImportExportTestCase(unittest.TestCase):
    def setUp(self):
        self.o = [1, 2, 3, None, False, {"a": "def"}]
        self.s = '''[1, 2, 3, null, false, {"a": "def"}]'''

    def test_parse_json_string_into_object(self):
        self.assertEqual( json.loads(self.s), self.o )

    def test_parse_object_into_json_string(self):
        self.assertEqual( json.dumps(self.o), self.s)

    def test_parse_datetime_to_json(self):
        now = datetime.strptime("2007/10/26 05:30:08 +0000","%Y/%m/%d %H:%M:%S +0000")
        def encode_datetime(obj):
            if isinstance(obj, datetime):
                return obj.strftime("%Y/%m/%d %H:%M:%S +0000")
            raise TypeError(repr(obj) + " is not JSON serializable")

        #self.assertEqual(json.dumps(now, default=encode_datetime), '"2007/10/26 05:30:08 +0000"')
        self.assertEqual(json.dumps(now), '"2007/10/26 05:30:08 +0000"')
        self.assertEqual(json.dumps([1,2,True], default=encode_datetime), '[1, 2, true]')


class ExceptionTestCase(unittest.TestCase):
    pass
    #def test_not_found(self):
    #    """ requesting for resource that does not exist should raise NotFound error """
    #    some_function = lambda x: x
    #    self.assertRaises(SpringnoteError.NotFound, some_function)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(JsonImportExportTestCase('test1_parse_datetime_to_json'))
    return suite

if __name__ == '__main__':
    #unittest.main(defaultTest=suite())
    loader = unittest.defaultTestLoader
    loader.testMethodPrefix = 'test'
    unittest.main(testLoader = loader)


