#!/usr/bin/python
# -*- coding: utf-8 -*-
import httplib, urllib
from datetime import datetime
from lib import oauth, json

class SpringnoteClient:
    CONSUMER_TOKEN = "al8kiqVKqlpIwZBDBwI4WA"
    CONSUMER_TOKEN_SECRET = "SpdStIpIvw16A0R3KPuAaoUPceazM61h4nOjS8GM"

    SPRINGNOTE_PROTOCOL = 'http'
    SPRINGNOTE_SERVER = 'api.springnote.com'
    SPRINGNOTE_PORT = 80
       
    REQUEST_TOKEN_URL = 'https://api.springnote.com/oauth/request_token'
    ACCESS_TOKEN_URL = 'https://api.springnote.com/oauth/access_token'
    AUTHORIZATION_URL = 'https://api.springnote.com/oauth/authorize'

    DEFAULT_ROOT_TAG = u'springmemorootpage'
    DEFAULT_ROOT_TITLE = u'SpringMemo 최상위 페이지입니다'
 

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
            return None
        
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
        url = "%s://%s/%s" % (self.SPRINGNOTE_PROTOCOL, self.SPRINGNOTE_SERVER, path)
        
        #parameters = {}
        if params:
            query = '&'.join(['='.join(item) for item in params.items()])
            url += "?" + query

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

        # multi ?
        if type(result) == list:
            pages = []
            for r in result:
                pages.append(Page.from_json(r))
            return pages
        
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

        path = "pages.json"
        parameters = {'tags': tag}
        url = self.set_url("pages.json", parameters)

        oauth_request = self.create_oauth_request('GET', url, parameters)

        connection = self.create_connection(oauth_request)

        # response
        response = connection.getresponse()
        body = response.read()
        pages = self.handle_response(body)

        return pages


    def get_pages_with_parent_id(self,parent_id):
        path = "pages.json"
        parameters = {'parent_id': str(parent_id)}
        url = self.set_url("pages.json", parameters)


        oauth_request = self.create_oauth_request('GET', url, parameters)

        connection = self.create_connection(oauth_request)

        # response
        response = connection.getresponse()
        body = response.read()
        raw_pages = self.handle_response(body)
        pages = []
        if not raw_pages:
            return None
        for raw_page in raw_pages:
            pages.append(self.get_page(raw_page.identifier))

        return pages

        

    def create_page(self,title,source=None,domain=None,tags=None,rel=None):
        parameters = {}
        if domain:
            parameters.update({'domain': domain})
        url = self.set_url("pages.json", parameters)

        oauth_request = self.create_oauth_request('POST', url, parameters)

        body = Page.to_write_json(title=title, source=source, tags=tags, relation_is_part_of=rel)

        connection = self.create_connection(oauth_request, body, {'Content-Type':'application/json'})

        response = connection.getresponse()
        body = response.read()

        page = self.handle_response(body)
        return page

    # TODO: DRY!
    def update_page(self, page, domain=None):
        parameters = {}
        if domain:
            parameters.update({'domain': domain})
        url = self.set_url("pages/%d.json" % page.identifier, parameters)

        oauth_request = self.create_oauth_request('PUT', url, parameters)

        body = Page.to_write_json(**page.to_dict())
        connection = self.create_connection(oauth_request, body, {'Content-Type':'application/json'})

        response = connection.getresponse()
        body = response.read()
        
        page = self.handle_response(body)
        return page


    def delete_page(self,id,domain=None):
        parameters = {}
        if domain:
            parameters.update({'domain': domain})
        url = self.set_url("pages/%d.json" % id, parameters)

        oauth_request = self.create_oauth_request('DELETE', url, parameters)

        connection = self.create_connection(oauth_request)

        response = connection.getresponse()
        body = response.read()

        page = self.handle_response(body)
        return page


class SpringnoteError:
    class NotAuthorized(RuntimeError): pass
    class CannotCreatePage(RuntimeError): pass
    class HasAlreadyBeenTaken(RuntimeError): pass
    class InvalidOauthRequest(RuntimeError): pass
    class PageNotFound(RuntimeError): pass

def strptime(date_string, format):
    import time
    return datetime(*(time.strptime(date_string, format)[0:6]))

class Page:
    typeset = {
        'identifier': int,
        'relation_is_part_of': int,

        'date_created':  lambda x: strptime(x,"%Y/%m/%d %H:%M:%S +0000"),
        'date_modified': lambda x: strptime(x,"%Y/%m/%d %H:%M:%S +0000"),
        'tags': lambda x: x.split()
    }
    attrset = ["rights", "source", "creator", "date_created", "contributor_modified", "date_modified", "relation_is_part_of", "identifier", "tags", "title"]

    client = None

    def __init__(self):
        for attr_name in self.attrset:
            setattr(self, attr_name, None)

    @staticmethod
    def from_jsons(body):
        """ generate a Page instance from json string """
        data = json.loads(body)
        return Page.update_from_dict(data)

    @staticmethod
    def from_json(data):
        return Page.update_from_dict(data)

    @staticmethod
    def set_page_client(client):
        Page.client = client

    @staticmethod
    def create_new_page(title,rel=None,source=None,tags=None,domain=None):
        ''' 새 page 인스턴스를 생성한다  '''
        if title != None:
            page = Page.client.create_page(title=title,source=source,rel=rel)
        return page

    @staticmethod
    def get_root_page():
        page = Page.client.get_root_page()
        return page

    @staticmethod
    def get_all_pages(rootmemo):
        pages = Page.client.get_pages_with_parent_id(rootmemo.page.identifier)
        return pages

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

        json_ustr = json.dumps({'page':result},ensure_ascii=False)
        return json_ustr.encode('utf-8')

   
   
    def to_dict(self):
        result = {}
        for attr_name in Page.attrset:
            result[attr_name] = getattr(self,attr_name)
        return result


    @staticmethod
    def update_from_dict(data):
        """ update parsing json string """

        if type(data) == list:
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
        
    def save_page(self,title=None,source=None,tags=None,rel=None):
        ''' 주어진 소스를 이용해 현재 페이지에 저장, 업데이트 '''
        if source:
            self.source = source
        if title:
            self.title = title
        if tags:
            self.tags = tags
        if rel:
            self.relation_is_part_of = rel

        self.update_page()

    def delete_page(self):
        Page.client.delete_page(self.identifier)

    def update_page(self):
        ''' Page.client를 이용해 자신의 데이터를 저장한다. '''
        newpage = Page.client.update_page(self)
        self.update_self_with_page(newpage)

    def update_self_with_page(self, page):
        ''' page의 attr들로 자기자신의 데이터를 교체한다 '''
        for attr_name in Page.attrset:
            if hasattr(page, attr_name):
                setattr(self, attr_name, getattr(page, attr_name))



def run():
    print "run with springmemo.py"
    


if __name__ == "__main__":
    run()
