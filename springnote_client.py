#!/usr/bin/python
#-*- coding:utf8 -*-
import oauth
import httplib,urllib
import xml.etree.ElementTree as ET
#import simplejson as json
#import lib.simplejson as json
import lib.json as json
from datetime import datetime

class SpringnoteClient:

    SPRINGNOTE_PROTOCOL = 'http'
    SPRINGNOTE_SERVER = 'api.springnote.com'
    SPRINGNOTE_PORT = 80
       
    REQUEST_TOKEN_URL = 'https://api.springnote.com/oauth/request_token'
    ACCESS_TOKEN_URL = 'https://api.springnote.com/oauth/access_token'
    AUTHORIZATION_URL = 'https://api.springnote.com/oauth/authorize'
    
    def __init__(self, consumer_token, consumer_token_secret):
        self.consumer = oauth.OAuthConsumer(consumer_token, consumer_token_secret)
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

        return Page.from_jsons(body)


    def authorize_url(self, token):
        return "%s?oauth_token=%s" % (self.AUTHORIZATION_URL, token.key)
        

    def create_page(self,title,source=None,domain=None):
        url = "%s://%s/pages.json" % (self.SPRINGNOTE_PROTOCOL, self.SPRINGNOTE_SERVER)
#        url = "%s://%s/pages.xml" % (self.SPRINGNOTE_PROTOCOL, self.SPRINGNOTE_SERVER)
        parameters = {}
        newpage = Page()
        newpage.title = title
        newpage.source = source

        if domain:
            parameters['domain'] = domain
            url += "?domain=%s" % domain


        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.access_token, http_method='POST', http_url=url, parameters=parameters)
        oauth_request.sign_request(self.signature_method, self.consumer, self.access_token)

        connection = httplib.HTTPConnection("%s:%d" % (self.SPRINGNOTE_SERVER, self.SPRINGNOTE_PORT))
        myheaders = oauth_request.to_header()

#        myheaders.update({'Content-Type':'application/xml'})
        myheaders.update({'Content-Type':'application/json'})
#        body = newpage.to_write_xml()
        body = newpage.to_write_json()

        connection.request(oauth_request.http_method, url, headers=myheaders,body=body)
        response = connection.getresponse()
        body = response.read()
        print "-----body-----"
        print body
        print "--------------"
        result = json.loads(body)
        print "type:::::::%s" % type(result)
        if type(result) == dict:
            print "TYPE::::::::::::::DICT"
            if result.has_key('errors'):
                for error in json.loads(body)['errors']:
                    if error['description'].startswith('has already been taken'):
                        raise SpringnoteError.CannotCreatePage
        elif type(result) == list:
            print "TYPE::::::::::::::LISt"
            for r in result:
#                if r.has_key('error') and r['error']['error_type'].startswith("InvalidOauthRequest"):
                if r.has_key('error') and r['error']['description'].startswith("signature_invalid"):
                    raise SpringnoteError.InvalidSignature

        return Page.from_jsons(body)

    def update_page(self,page,domain=None):
        url = "%s://%s/pages/%d.json" % (self.SPRINGNOTE_PROTOCOL, self.SPRINGNOTE_SERVER,page.identifier)
        parameters = {}

        print "update_page page type :: %s" % isinstance(page,Page)
        print "datetime :: %s" % page.date_created

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
        print "----body----"
        print body
        print "------------"

        return Page.from_jsons(body)




class SpringnoteError:
    class NotAuthorized(RuntimeError):
        pass
    class CannotCreatePage(RuntimeError):
        pass
    class InvalidOauthRequest(RuntimeError):
        pass
    class InvalidSignature(RuntimeError):
        pass

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

    def from_jsons(body):
        newPage = Page()
        newPage.parse_json(body)
        return newPage
    from_jsons = staticmethod(from_jsons)

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

#    def to_write_param(self):
#        result = {}
#        result['page[title]'] = self.title
#        result['page[source]'] = self.source
#        result['page[relation_is_part_of]'] = self.relation_is_part_of
#        result['page[tags]'] = self.tags
#        return result


    def to_write_json(self):
### type이 datetime일시에 맨 뒤에 +0000을 붙이던가, strptime으로 
#        page = {}
#        result = {}
#        page['title'] = self.title
#        page['source'] = self.source
#        page['relation_is_part_of'] = self.relation_is_part_of
#        page['tags'] = self.tags
#        result['page'] = page
#        return json.dumps({'page':page})
        return json.dumps({'page':self.__dict__})

    def to_write_xml(self):
        root = ET.Element("page")
        title = ET.SubElement(root,"title")
        title.text = self.title
        source = ET.SubElement(root,"source")
        source.text = self.source
        relation_is_part_of = ET.SubElement(root,"relation_is_part_of")
        relation_is_part_of.text = self.relation_is_part_of
        tags = ET.SubElement(root,"tags")
        tags.text = self.tags
        return ET.tostring(root,"utf-8")


    def parse_json(self,str):
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




def run():
    token = "wpRiJvvQy624FayfQ6Q"
    token_secret = "GHY2La7yR2moQUXO2ETiuuiAtqFCCa37bO6uAXC6Yw"
    id = 2759692
    access_key = "FHksYUxDz5sNpxXZ3Yq9Qg"
#    access_key = "FHksYUxDz5sNpxXZ3Yq9Qk"  #wrong access_key
    access_secret = "5ILhwSbmQCFBL4A8orCBna8zwLAbC2iIRPxRfRZgQls"

    client = SpringnoteClient(token,token_secret)
#    request_token = client.fetch_request_token()
    
#    print client.authorize_url(request_token)
#    raw_input("please Enter...")

#    access_token = client.fetch_access_token(request_token)
    access_token = client.set_access_token_directly(access_key,access_secret)
    print access_token.key, access_token.secret

#    page = client.get_page(id, domain='loocaworld')
    page = client.create_page(title="titleis this6",source="this is body",domain="loocaworld")
    print "----body----"
    print page.source
#    print result
    print "------------"


    


if(__name__=='__main__'):
    run()



