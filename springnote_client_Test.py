#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from mock import Mock
import os, sys
#from springnote_client import SpringnoteClient, httplib
import springnote_client
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
            
        data = self.client.fetch_access_token()
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
        #self.client.access_token = springnote_client.oauth.OAuthToken(token, key)
        #self.assertEqual(type(self.client.access_token), springnote_client.oauth.OAuthToken)


class SpringnoteClientTestCase(unittest.TestCase):
    def setUp(self):
        # mock it out
        #self.client = None
        springnote_client.httplib = Mock({
            'HTTPSConnection': Mock({
                'request': '123',
                'getresponse': Mock({'read': "oauth_token=we&oauth_token_secret=fk&open_id=http%3A%2F%2Fchanju.myid.net%2F"})
            })
        })         
            

        
        self.consumer_token, self.consumer_token_secret = 'some consumer token key', 'some consumer secret'
        #auth = OAuth(consumer_token, consumer_token_secret)
        self.client = springnote_client.SpringnoteClient(self.consumer_token, self.consumer_token_secret)
        data = self.client.fetch_access_token()
        self.access_token = data

    def test_get_page_with_id(self):
        id = 31752
        page = self.client.get_page(id)
        #self.assertEqual( type(page), Page )
        #self.assertEqual( page.identifier, id )
        self.assertEqual( type(), str)

    #def test_create_page(self):
    #    title, body = 'some title', 'some body'
    #    page = self.client.create_page(title=title, source=body)
    #    assertEqual( type(page), Page )
    #    assertNotEqual( page.identifier, None )
    #    assertEqual( page.title, title )
    #    assertEqual( page.source, body )

    #def test_update_page(self):
    #    self.fail("Implement me")

class ExceptionTestCase(unittest.TestCase):
    pass
    #def test_not_found(self):
    #    """ requesting for resource that does not exist should raise NotFound error """
    #    some_function = lambda x: x
    #    self.assertRaises(SpringnoteError.NotFound, some_function)

if __name__ == '__main__':
    unittest.main()


