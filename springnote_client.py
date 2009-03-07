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

    DEFAULT_ROOT_TAG = 'springmemorootpage'
    DEFAULT_ROOT_TITLE = 'SpringMemo 최상위 페이지입니다'
   
    def print_client(self):
        print "::::::::: print client ::::::::"
        print " consumer :: %s" % self.consumer
        print " consumer key :: %s" % self.consumer.secret
        print " consumer secret :: %s" % self.consumer.key
        print " access :: %s" % self.access_token
        print " access key :: %s" % self.access_token.key
        print " access secret :: %s" % self.access_token.secret
        print " signature_method :: %s" % self.signature_method
        print "::::::::: print client finished ::::::::"


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
        page = self.get_page_with_tag('springmemorootpage')
        if page == None:
            page = self.create_page(self.DEFAULT_ROOT_TITLE,source=None,domain=None,tags=self.DEFAULT_ROOT_TAG,rel=None)
        elif isinstance(page, list):
            page = page[0]

        return page


    def authorize_url(self, token):
        return "%s?oauth_token=%s" % (self.AUTHORIZATION_URL, token.key)


    def set_url(self, path, params={}):
        #url = "%s://%s/pages/%d.json" % (self.SPRINGNOTE_PROTOCOL, self.SPRINGNOTE_SERVER, id)
        url = "%s://%s/%s" % (self.SPRINGNOTE_PROTOCOL, self.SPRINGNOTE_SERVER, path)
        
        #parameters = {}
        if params:
            query = '&'.join(['='.join(item) for item in params.items()])
            url += "?" + query
        #if domain:
        #    parameters['domain'] = domain
        #    url += "?domain=%s" % domain

        return url

    def create_oauth_request(self, http_method, http_url, parameters):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.access_token, http_method=http_method, http_url=http_url, parameters=parameters)
        oauth_request.sign_request(self.signature_method, self.consumer, self.access_token)        
        return oauth_request


    def create_connection(self, oauth_request, body=None, headers={}):
        connection = httplib.HTTPConnection("%s:%d" % (self.SPRINGNOTE_SERVER, self.SPRINGNOTE_PORT))
        merged_headers = oauth_request.to_header()

        merged_headers.update(headers)
        connection.request(oauth_request.http_method, oauth_request.http_url, headers=merged_headers, body=body)
        return connection

    def handle_response(self, response_body):
        result = json.loads(response_body)
#        print "----------"
#        print result
#        print "----------"


        # errors?
        if type(result) == dict:
            if result.has_key('errors'):
                for error in json.loads(response_body)['errors']:
                    if error['description'].startswith('has already been taken'):
                        raise SpringnoteError.HasAlreadyBeenTaken
        elif type(result) == list:
            if len(result) == 0:    #찾을 수 없음
                return None
            for r in result:
                if r.has_key('error') and r['error']['error_type'].startswith("InvalidOauthRequest"):
                    raise SpringnoteError.InvalidOauthRequest
                elif r.has_key('error') and r['error']['error_type'].startswith("NotFound"):
                    raise SpringnoteError.PageNotFound
        
        # generate Page instance from json
        return Page.from_jsons(response_body)

    # todo
    def get_page(self, id, domain=None):
        path = "pages/%d.json" % id
        parameters = {}
        if domain:
            parameters.update({'domain': domain})
        url = self.set_url(path, parameters)

        oauth_request = self.create_oauth_request('GET', url, parameters)
        connection = self.create_connection(oauth_request)

        # response
        response = connection.getresponse()
        body = response.read()
        page = self.handle_response(body)

        return page

    def get_page_with_tag(self, tag):
        #url = "%s://%s/pages.json" % (self.SPRINGNOTE_PROTOCOL, self.SPRINGNOTE_SERVER)
        #parameters = {}
        #if tag:
        #    parameters['tags'] = tag
        #    url += "?tags=%s" % tag

        path = "pages.json"
        parameters = {'tags': tag}
        url = self.set_url("pages.json", parameters)

        #oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.access_token, http_method='GET', http_url=url, parameters=parameters)
        #oauth_request.sign_request(self.signature_method, self.consumer, self.access_token)        
        oauth_request = self.create_oauth_request('GET', url, parameters)

        #connection = httplib.HTTPConnection("%s:%d" % (self.SPRINGNOTE_SERVER, self.SPRINGNOTE_PORT))

        #connection.request('GET', url, headers=oauth_request.to_header())
        connection = self.create_connection(oauth_request)

        response = connection.getresponse()
        body = response.read()

        #result = json.loads(body)

        #if type(result) == dict:
        #    if result.has_key('errors'):
        #        for error in json.loads(body)['errors']:
        #            if error['description'].startswith('has already been taken'):
        #                raise SpringnoteError.HasAlreadyBeenTaken
        #elif type(result) == list:
        #    if len(result) == 0:    # 찾을 수 없음
        #        return None
        #    for r in result:
        #        if r.has_key('error') and r['error']['error_type'].startswith("InvalidOauthRequest"):
        #            raise SpringnoteError.InvalidOauthRequest

        #return Page.from_jsons(body)
        # response
        response = connection.getresponse()
        body = response.read()
        pages = self.handle_response(body)

        return pages

        

    def create_page(self,title,source=None,domain=None,tags=None,rel=None):
        #url = "%s://%s/pages.json" % (self.SPRINGNOTE_PROTOCOL, self.SPRINGNOTE_SERVER)
        #parameters = {}
        #if domain:
        #    parameters['domain'] = domain
        #    url += "?domain=%s&" % domain
        parameters = {}
        if domain:
            parameters.update({'domain': domain})
#        else:
#            parameters.update({'domain': 'loocaworld'})
        url = self.set_url("pages.json", parameters)

        #oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.access_token, http_method='POST', http_url=url, parameters=parameters)
        #oauth_request.sign_request(self.signature_method, self.consumer, self.access_token)
        oauth_request = self.create_oauth_request('POST', url, parameters)

        #newpage = Page()
        #newpage.title = title
        #newpage.source = source
        #newpage.tags = tags
#        body = Page.to_write_json(title=title, source=source, tags=tags)
        body = Page.to_write_json(title=title, source="", tags=tags, relation_is_part_of=rel)

        #connection = httplib.HTTPConnection("%s:%d" % (self.SPRINGNOTE_SERVER, self.SPRINGNOTE_PORT))
        #myheaders = oauth_request.to_header()
        #myheaders.update({'Content-Type':'application/json'})
        #connection.request(oauth_request.http_method, url, body=body, headers=myheaders)
        connection = self.create_connection(oauth_request, body, {'Content-Type':'application/json'})

        response = connection.getresponse()
        body = response.read()

        ##print "-----body-----"
        ##print body
        ##print "--------------"
        #result = json.loads(body)
        #if type(result) == dict:
        #    if result.has_key('errors'):
        #        for error in json.loads(body)['errors']:
        #            if error['description'].startswith('has already been taken'):
        #                raise SpringnoteError.HasAlreadyBeenTaken
        #elif type(result) == list:
        #    for r in result:
        #        if r.has_key('error') and r['error']['error_type'].startswith("InvalidOauthRequest"):
        #            raise SpringnoteError.InvalidOauthRequest

        #return Page.from_jsons(body)
        page = self.handle_response(body)
        return page

    # TODO: DRY!
    def update_page(self, page, domain=None):
        #url = "%s://%s/pages/%d.json" % (self.SPRINGNOTE_PROTOCOL, self.SPRINGNOTE_SERVER,page.identifier)
        #parameters = {}

        #if domain:
        #    parameters['domain'] = domain
        #    url += "?domain=%s" % domain
        parameters = {}
        if domain:
            parameters.update({'domain': domain})
        url = self.set_url("pages/%d.json" % page.identifier, parameters)

        #oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.access_token, http_method='PUT', http_url=url, parameters=parameters)
        #oauth_request.sign_request(self.signature_method, self.consumer, self.access_token)
        oauth_request = self.create_oauth_request('PUT', url, parameters)

        #connection = httplib.HTTPConnection("%s:%d" % (self.SPRINGNOTE_SERVER, self.SPRINGNOTE_PORT))
        #myheaders = oauth_request.to_header()

        #myheaders.update({'Content-Type':'application/json'})
        #body = Page.to_write_json(**page.to_dict())
        #connection.request(oauth_request.http_method, url, headers=myheaders,body=body)
        body = Page.to_write_json(**page.to_dict())
        connection = self.create_connection(oauth_request, body, {'Content-Type':'application/json'})

        response = connection.getresponse()
        body = response.read()
        
        #print "----body----"
        #print body
        #print "------------"
        #return Page.from_jsons(body)
        page = self.handle_response(body)
        return page


    def delete_page(self,id,domain=None):
        #url = "%s://%s/pages/%d.json" % (self.SPRINGNOTE_PROTOCOL, self.SPRINGNOTE_SERVER,id)
        #parameters = {}

        #if domain:
        #    parameters['domain'] = domain
        #    url += "?domain=%s" % domain
        parameters = {}
        if domain:
            parameters.update({'domain': domain})
        url = self.set_url("pages/%d.json" % id, parameters)

        #oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.access_token, http_method='DELETE', http_url=url, parameters=parameters)
        #oauth_request.sign_request(self.signature_method, self.consumer, self.access_token)
        oauth_request = self.create_oauth_request('DELETE', url, parameters)

        #connection = httplib.HTTPConnection("%s:%d" % (self.SPRINGNOTE_SERVER, self.SPRINGNOTE_PORT))
        #myheaders = oauth_request.to_header()

        #connection.request(oauth_request.http_method, url, headers=myheaders)
        connection = self.create_connection(oauth_request)

        response = connection.getresponse()
        body = response.read()
        ##print "----body----"
        ##print body
        ##print "------------"
        #result = json.loads(body)
        #if type(result) == dict:
        #    if result.has_key('errors'):
        #        for error in json.loads(body)['errors']:
        #            if error['description'].startswith('has already been taken'):
        #                raise SpringnoteError.HasAlreadyBeenTaken
        #elif type(result) == list:
        #    for r in result:
        #        if r.has_key('error') and r['error']['error_type'].startswith("NotFound"):
        #            raise SpringnoteError.PageNotFound
        #return Page.from_jsons(body)
        page = self.handle_response(body)
        return page


class SpringnoteError:
    class NotAuthorized(RuntimeError): pass
    class CannotCreatePage(RuntimeError): pass
    class HasAlreadyBeenTaken(RuntimeError): pass
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

    client = None

    def __init__(self):
        for attr_name in self.attrset:
            setattr(self, attr_name, None)
        setattr(self,'view',None)             #UI에 대한 핸들 

    @staticmethod
    def from_jsons(body):
        """ generate a Page instance from json string """
        #newPage = Page()
        #newPage.update_from_jsons(body)
        #return newPage
        data = json.loads(body)
        return Page.update_from_dict(data)

    @staticmethod
    def set_page_client(client):
        Page.client = client

    @staticmethod
    def create_new_page(type,title,rel):
        ''' 새 page 인스턴스를 생성한다  '''
        if title != None:
            page = Page.client.create_page(title=title,source="",rel=rel)
        return page

    @staticmethod
    def get_root_page():
        page = Page.client.get_root_page()
        return page

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

    @staticmethod
    def to_write_json(**page_dict):
        result = {}
        for attr_name in Page.attrset:
            if attr_name in page_dict:
                result[attr_name] = page_dict[attr_name]

        return json.dumps({'page':result})

    def to_dict(self):
        result = {}
        for attr_name in Page.attrset:
            result[attr_name] = getattr(self,attr_name)
        return result

    #def to_write_json(self):
    #    result = {}
    #    for attr_name in self.attrset:
#   #         if(getattr(self,attr_name)!=None):
#   #             print getattr(self,attr_name)
#   #             result[attr_name] = getattr(self,attr_name).decode('euc-kr').encode('euc-kr')
#   #         else:
#   #             result[attr_name] = getattr(self,attr_name)
    #        result[attr_name] = getattr(self,attr_name)
    #    return json.dumps({'page':result})

    @staticmethod
    def update_from_dict(data):
        """ update parsing json string """

        if type(data) == list:
            #data = data[0]
            return [Page.update_from_dict(each_data) for each_data in data]

        data = data["page"]

        # type conversion
        for attr_name, attr_type in Page.typeset.iteritems():
            if data.has_key(attr_name):
                data[attr_name] = attr_type( data[attr_name] )

        new_page = Page()
        for key,value in data.iteritems():
            setattr(new_page, key, value)
        return new_page

    def update_from_jsons(self,str):
        """ update parsing json string """
        data = json.loads(str)
        if type(data) == list:
            data = data[0]
        data = data["page"]
        # type conversion
        for attr_name, attr_type in self.typeset.iteritems():
            if data.has_key(attr_name):
                data[attr_name] = attr_type( data[attr_name] )

        for key,value in data.iteritems():
            setattr(self, key, value)
        return data
        

    def to_s(self):
        return "%s %s %s %s %s %s" % (self.identifier,self.date_created,
                self.date_modified, self.rights,
                self.creator, self.contributor_modified)












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
#    page = client.get_page_with_tag(client.DEFAULT_ROOT_TAG)
#    page = client.get_root_page()
#    page = client.create_page(title="titleis this7",source="this is body",domain="loocaworld")
    client.print_client()
    page = client.create_page(title="titleis this9",source="",rel=None)

    print "----body----"
    print page.source
#    print result
    print "------------"
    print "id::%d"%page.identifier

#    page.title = "EDITED TITLE!!!"
#    page.source = "This page is hacked"
#    newpage = client.update_page(page,domain='loocaworld')


#    result = client.delete_page(page.identifier,domain='loocaworld')
    


if __name__ == "__main__":
    run()
