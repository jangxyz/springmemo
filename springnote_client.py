#!/usr/bin/python
#-*- coding:utf8 -*-
import oauth
import httplib,urllib
import lib.json as json
from datetime import datetime

class SpringnoteClient:
    CONSUMER_TOKEN = "wpRiJvvQy624FayfQ6Q"
    CONSUMER_TOKEN_SECRET = "GHY2La7yR2moQUXO2ETiuuiAtqFCCa37bO6uAXC6Yw"

    SPRINGNOTE_PROTOCOL = 'http'
    SPRINGNOTE_SERVER = 'api.springnote.com'
    SPRINGNOTE_PORT = 80
       
    REQUEST_TOKEN_URL = 'https://api.springnote.com/oauth/request_token'
    ACCESS_TOKEN_URL = 'https://api.springnote.com/oauth/access_token'
    AUTHORIZATION_URL = 'https://api.springnote.com/oauth/authorize'
    
    def __init__(self):
        self.consumer = oauth.OAuthConsumer(self.CONSUMER_TOKEN, self.CONSUMER_TOKEN_SECRET)
        self.signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
        
    def create_oauth_request_for_request_token(self):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, http_url=self.REQUEST_TOKEN_URL)
        oauth_request.sign_request(self.signature_method, self.consumer, None)
        return oauth_request
        
    def fetch_request_token(self):
        oauth_request = self.create_oauth_request_for_request_token()
                
        connection = httplib.HTTPSConnection("%s:%d" % (self.SPRINGNOTE_SERVER, 443))
        connection.request(oauth_request.http_method, self.REQUEST_TOKEN_URL, headers=oauth_request.to_header())
        response = connection.getresponse()
        body = response.read()
        if body.startswith('Invalid OAuth Request'):
            raise SpringnoteError.NotAuthorized
        return oauth.OAuthToken.from_string(body)
    
    def create_oauth_request_for_access_token(self, token):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=token, http_url=self.ACCESS_TOKEN_URL)
        oauth_request.sign_request(self.signature_method, self.consumer, token)
        return oauth_request
        
    def fetch_access_token(self, token):
        oauth_request = self.create_oauth_request_for_access_token(token)
                
        connection = httplib.HTTPSConnection("%s:%d" % (self.SPRINGNOTE_SERVER, 443))
        connection.request(oauth_request.http_method, self.ACCESS_TOKEN_URL, headers=oauth_request.to_header()) 
        response = connection.getresponse()
        body = response.read()
        if body.startswith('Invalid OAuth Request'):
            raise SpringnoteError.NotAuthorized
        
        self.access_token = oauth.OAuthToken.from_string(body)
        return self.access_token
 
    def set_access_token_directly(self,key,secret):
        self.access_token = oauth.OAuthToken(key,secret)
        return self.access_token


    def get_root_page(self):
        '''tag 에 springmemorootpage 라고 써있는 글을 찾는다 '''
        '''없으면 새 페이지를 만들고 리턴 '''
        self.get_page_with_tag('springmemorootpage')
        pass


    # todo
    def get_page(self, id, domain=None):
        url = "%s://%s/pages/%d.json" % (self.SPRINGNOTE_PROTOCOL, self.SPRINGNOTE_SERVER, id)
        parameters = {}
        if domain:
            parameters['domain'] = domain
            url += "?domain=%s" % domain
        
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.access_token, http_method='GET', http_url=url, parameters=parameters)
        oauth_request.sign_request(self.signature_method, self.consumer, self.access_token)        

        connection = httplib.HTTPConnection("%s:%d" % (self.SPRINGNOTE_SERVER, self.SPRINGNOTE_PORT))
        connection.request('GET', url, headers=oauth_request.to_header())
        response = connection.getresponse()
        body = response.read()
    
        print "body::::::: %s" % body
        return Page.from_jsons(body)

    def get_page_with_tag(self,tag,domain=None):
#        url = "%s://%s/pages.json?tags=%s" % (self.SPRINGNOTE_PROTOCOL, self.SPRINGNOTE_SERVER, tag)
        url = "%s://%s/pages.json" % (self.SPRINGNOTE_PROTOCOL, self.SPRINGNOTE_SERVER)
        parameters = {}
#        if domain:
#            parameters['domain'] = domain
#            url += "?domain=%s" % domain
        
        url += "?tags=%s" % tag
        print "url::%s"%url
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.access_token, http_method='GET', http_url=url, parameters=parameters)
        oauth_request.sign_request(self.signature_method, self.consumer, self.access_token)        

        connection = httplib.HTTPConnection("%s:%d" % (self.SPRINGNOTE_SERVER, self.SPRINGNOTE_PORT))

        connection.request('GET', url, headers=oauth_request.to_header())
        response = connection.getresponse()
        body = response.read()
        print "----------"
        print body
        print "----------"

        return Page.from_jsons(body)


    def authorize_url(self, token):
        return "%s?oauth_token=%s" % (self.AUTHORIZATION_URL, token.key)
        

    # TODO: DRY!
    def create_page(self,title,source=None,domain=None,tags=None):
        url = "%s://%s/pages.json" % (self.SPRINGNOTE_PROTOCOL, self.SPRINGNOTE_SERVER)
#        url = "%s://%s/pages.xml" % (self.SPRINGNOTE_PROTOCOL, self.SPRINGNOTE_SERVER)
        parameters = {}
        newpage = Page()
        newpage.title = title
        newpage.source = source
        if tags:
            newpage.tags.append(tags)

        if domain:
            parameters['domain'] = domain
            url += "?domain=%s&" % domain

        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.access_token, http_method='POST', http_url=url, parameters=parameters)
        oauth_request.sign_request(self.signature_method, self.consumer, self.access_token)

        connection = httplib.HTTPConnection("%s:%d" % (self.SPRINGNOTE_SERVER, self.SPRINGNOTE_PORT))
        myheaders = oauth_request.to_header()

        myheaders.update({'Content-Type':'application/json'})
        body = newpage.to_write_json()

        connection.request(oauth_request.http_method, url, body=body, headers=myheaders)
        response = connection.getresponse()
        body = response.read()
        #print "-----body-----"
        #print body
        #print "--------------"
        result = json.loads(body)
        if type(result) == dict:
            if result.has_key('errors'):
                for error in json.loads(body)['errors']:
                    if error['description'].startswith('has already been taken'):
                        raise SpringnoteError.CannotCreatePage
        elif type(result) == list:
            for r in result:
                if r.has_key('error') and r['error']['error_type'].startswith("InvalidOauthRequest"):
                    raise SpringnoteError.InvalidOauthRequest

        return Page.from_jsons(body)

    def update_page(self,page,domain=None):
        url = "%s://%s/pages/%d.json" % (self.SPRINGNOTE_PROTOCOL, self.SPRINGNOTE_SERVER,page.identifier)
        parameters = {}

        if domain:
            parameters['domain'] = domain
            url += "?domain=%s" % domain

        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.access_token, http_method='PUT', http_url=url, parameters=parameters)
        oauth_request.sign_request(self.signature_method, self.consumer, self.access_token)

        connection = httplib.HTTPConnection("%s:%d" % (self.SPRINGNOTE_SERVER, self.SPRINGNOTE_PORT))
        myheaders = oauth_request.to_header()

        myheaders.update({'Content-Type':'application/json'})
        body = page.to_write_json()

        connection.request(oauth_request.http_method, url, headers=myheaders,body=body)
        response = connection.getresponse()
        body = response.read()
        #print "----body----"
        #print body
        #print "------------"

        return Page.from_jsons(body)

    def delete_page(self,id,domain=None):
        url = "%s://%s/pages/%d.json" % (self.SPRINGNOTE_PROTOCOL, self.SPRINGNOTE_SERVER,id)
        parameters = {}

        if domain:
            parameters['domain'] = domain
            url += "?domain=%s" % domain

        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.access_token, http_method='DELETE', http_url=url, parameters=parameters)
        oauth_request.sign_request(self.signature_method, self.consumer, self.access_token)

        connection = httplib.HTTPConnection("%s:%d" % (self.SPRINGNOTE_SERVER, self.SPRINGNOTE_PORT))
        myheaders = oauth_request.to_header()

        connection.request(oauth_request.http_method, url, headers=myheaders)
        response = connection.getresponse()
        body = response.read()
        #print "----body----"
        #print body
        #print "------------"
        result = json.loads(body)
        if type(result) == dict:
            if result.has_key('errors'):
                for error in json.loads(body)['errors']:
                    if error['description'].startswith('has already been taken'):
                        raise SpringnoteError.CannotCreatePage
        elif type(result) == list:
            for r in result:
                if r.has_key('error') and r['error']['error_type'].startswith("NotFound"):
                    raise SpringnoteError.PageNotFound

        return Page.from_jsons(body)


class SpringnoteError:
    class NotAuthorized(RuntimeError): pass
    class CannotCreatePage(RuntimeError): pass
    class InvalidOauthRequest(RuntimeError): pass
    class PageNotFound(RuntimeError): pass


class Page:
    typeset = {
        'identifier': int,
        'relation_is_part_of': int,

        'date_created': lambda x: datetime.strptime(x,"%Y/%m/%d %H:%M:%S +0000"),
        'date_modified': lambda x: datetime.strptime(x,"%Y/%m/%d %H:%M:%S +0000"),
        'tags': lambda x: x.split()
    }
    attrset = ["rights", "source", "creator", "date_created", "contributor_modified", "date_modified", "relation_is_part_of", "identifier", "tags", "title"]

    def __init__(self):
        for attr_name in self.attrset:
            setattr(self, attr_name, None)
        setattr(self,'window',None)             #UI에 대한 핸들 

    @staticmethod
    def from_jsons(body):
        """ generate a Page instance from json string """
        newPage = Page()
        newPage.update_from_jsons(body)
        return newPage

#    def to_param(self):
#        result = {}
#        for attr_name,attr_value in self.__dict__.iteritems():
#            result['page[%s]' % attr_name] = attr_value
#        return result

#    def to_json(self):
#        result = {}
#        for key,value in self.__dict__.iteritems():
#            if value != None:
#                result[key] = value
#        return json.dumps(result)

    def to_write_param(self):
        result = {}
        result['page[title]'] = self.title
        result['page[source]'] = self.source
        return result


    def to_write_json(self):
        result = {}
        for attr_name in self.attrset:
            result[attr_name] = getattr(self,attr_name)
        return json.dumps({'page':result})


    def update_from_jsons(self,str):
        """ update parsing json string """
        data = json.loads(str)
        data = data["page"]
        for attr_name, attr_type in self.typeset.iteritems():
            data[attr_name] = attr_type( data[attr_name] )

        for key,value in data.iteritems():
            setattr(self, key, value)
        return data
        

    def to_s(self):
        return "%s %s %s %s %s %s" % (self.identifier,self.date_created,
                self.date_modified, self.rights,
                self.creator, self.contributor_modified)



class Model:
    def __init__(self,memo):
        self.page = None
        self.memo = memo
        self.client = memo.controller.client

    @staticmethod
    def create_new_model(memo,type,title):
        model = Model(memo)
        model.page = model.client.create_page(title)
        return model

    @staticmethod
    def get_root_model(memo):
        model = Model(memo)
        model.page = model.client.get_root_page()








def run():
    token = "wpRiJvvQy624FayfQ6Q"
    token_secret = "GHY2La7yR2moQUXO2ETiuuiAtqFCCa37bO6uAXC6Yw"
    id = 2827114
    access_key = "FHksYUxDz5sNpxXZ3Yq9Qg"
    access_secret = "5ILhwSbmQCFBL4A8orCBna8zwLAbC2iIRPxRfRZgQls"

    client = SpringnoteClient()
#    request_token = client.fetch_request_token()
    
#    print client.authorize_url(request_token)
#    raw_input("please Enter...")

#    access_token = client.fetch_access_token(request_token)
    access_token = client.set_access_token_directly(access_key,access_secret)
    print access_token.key, access_token.secret

#    page = client.get_page(id, domain='loocaworld')
    page = client.get_page_with_tag("aaa",domain='loocaworld')
#    page = client.create_page(title="titleis this7",source="this is body",domain="loocaworld")

    print "----body----"
    print page.source
#    print result
    print "------------"

#    page.title = "EDITED TITLE!!!"
#    page.source = "This page is hacked"
#    newpage = client.update_page(page,domain='loocaworld')


#    result = client.delete_page(page.identifier,domain='loocaworld')
    


if __name__ == "__main__":
    run()
