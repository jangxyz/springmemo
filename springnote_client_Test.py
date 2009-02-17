#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import os, sys
from springnote_client import *

#class BasicAuthTestCase(unittest.TestCase):
#    def test_auth_info_header(self):
#        """ basic auth should be set in url """
#        """ http://username:userpassword@springnote.com/query?3=2 """
#        from urlparse import urlparse
#        user_id, user_key, app_key = 'some_user_id.myid.net', 'some_user_key', 'some_app_key'
#        auth = BasicAuth(user_id, user_key, app_key)
#        client = SpringnoteClient(auth)
#        parse_result = urlparse(client.url)
#        assertEqual(parse_result.username, user_id)
#        assertEqual(parse_result.password, "%s.%s" % (user_key,app_key))

class OAuthTestCase(unittest.TestCase):
    def setUp(self):
        self.consumer_token, self.consumer_token_secret = 'some consumer token key', 'some consumer secret'
        #auth = OAuth(consumer_token, consumer_token_secret)
        self.client = SpringnoteClient(self.consumer_token, self.consumer_token_secret)

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
        https_connection = Mock("httplib.HTTPSConnection")
        https_connection.mock_returns = Mock("connection")
        https_connection.mock_returns.getresponse.mock_returns = Mock("response")
        https_connection.mock_returns.getresponse.mock_returns.read.mock_returns = "oauth_token=cd&oauth_token_secret=ab&open_id=http%3A%2F%2Fchanju.myid.net%2F"
        data = self.client.fetch_request_token()
        self.assertEqual(type(data), oauth.OAuthToken)
        
        #pass

    #def test_oauth_access_token(self):
    #    """ should fetch the access token and make it a valid access token """
    #    self.client.access_token = None
    #    assertEqual(type(self.client.access_token), oauth.OAuthToken)

    #def test_oauth_directly_set_access_token(self):
    #    """ should directly set access token """
    #    self.client.access_token = oauth.OAuthToken(token, key)
    #    assertEqual(type(self.client.access_token), oauth.OAuthToken)


class SpringnoteClientTestCase(unittest.TestCase):
    def setup(self):
        # mock it out
        self.client = None

    #def test_get_page_with_id(self):
    #    id = 31752
    #    page = self.client.get_page(id)
    #    assertEqual( type(page), Page )
    #    assertEqual( page.identifier, id )

    #def test_create_page(self):
    #    title, body = 'some title', 'some body'
    #    page = self.client.create_page(title=title, source=body)
    #    assertEqual( type(page), Page )
    #    assertNotEqual( page.identifier, None )
    #    assertEqual( page.title, title )
    #    assertEqual( page.source, body )

class ExceptionTestCase(unittest.TestCase):
    pass
    #def test_not_found(self):
    #    """ requesting for resource that does not exist should raise NotFound error """
    #    some_function = lambda x: x
    #    self.assertRaises(SpringnoteError.NotFound, some_function)

if __name__ == '__main__':
    unittest.main()


