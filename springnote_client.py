import oauth
import httplib

class SpringnoteClient:

    SPRINGNOTE_PROTOCOL = 'http'
    SPRINGNOTE_SERVER = 'api.springnote.com'
    SPRINGNOTE_PORT = 80
    
    REQUEST_TOKEN_URL = 'https://api.springnote.com/oauth/request_token'
    ACCESS_TOKEN_URL = 'https://api.springnote.com/oauth/access_token'
    AUTHORIZATION_URL = 'https://api.springnote.com/oauth/authorize'
    
    def __init__(self, consumer_token, consumer_token_secret):
        self.consumer = oauth.OAuthConsumer(consumer_token, consumer_token_secret)
        
    def create_oauth_request_for_request_token(self):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, http_url=self.REQUEST_TOKEN_URL)
        oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), self.consumer, None)
        return oauth_request
        
    def fetch_request_token(self):
        oauth_request = self.create_oauth_request_for_request_token()
                
        connection = httplib.HTTPSConnection("%s:%d" % ('api.springnote.com', 443))
        connection.request(oauth_request.http_method, self.REQUEST_TOKEN_URL, headers=oauth_request.to_header()) 
        response = connection.getresponse()
        body = response.read()
        if body.startswith('Invalid OAuth Request'):
            raise SpringnoteError.NotAuthorized
        return oauth.OAuthToken.from_string(body)
    
    def create_oauth_request_for_access_token(self, token):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=token, http_url=self.ACCESS_TOKEN_URL)
        oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), self.consumer, token)
        return oauth_request
        
    def fetch_access_token(self):
        oauth_request = self.create_oauth_request_for_request_token()
                
        connection = httplib.HTTPSConnection("%s:%d" % ('api.springnote.com', 443))
        connection.request(oauth_request.http_method, self.ACCESS_TOKEN_URL, headers=oauth_request.to_header()) 
        response = connection.getresponse()
        body = response.read()
        if body.startswith('Invalid OAuth Request'):
            raise SpringnoteError.NotAuthorized
        
        self.access_token = oauth.OAuthToken.from_string(body)
        return self.access_token
    
    # todo
    def get_page(self, id):
        url = "%s://%s/pages/%d.xml" % (SPRINGNOTE_PROTOCOL, SPRINGNOTE_SERVER, page_id)
        parameters = {}
        if domain:
            parameters['domain'] = domain
            url += "?domain=%s" % domain
        
        print url
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.access_token, http_method='GET', http_url=url, parameters=parameters)
        oauth_request.sign_request(self.signature_method, self.consumer, self.access_token)        

        connection = httplib.HTTPConnection("%s:%d" % (SPRINGNOTE_SERVER, SPRINGNOTE_PORT))
        connection.request('GET', url, headers=oauth_request.to_header())

class SpringnoteError:
    class NotAuthorized(RuntimeError):
        pass

class Page:
    def __init__(self, body):
        #self.identifier = None
        self.body = body
        
    def Page.from_xml(self, xml):
        return Page(xml)