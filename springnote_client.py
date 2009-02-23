#!/usr/bin/python
#-*- coding:utf8 -*-
import oauth
import httplib,urllib
import xml.etree.ElementTree as ET
import simplejson as json
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
        oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), self.consumer, None)
        return oauth_request
        
    def fetch_request_token(self):
        oauth_request = self.create_oauth_request_for_request_token()
                
#        connection = httplib.HTTPSConnection("%s:%d" % (self.SPRINGNOTE_SERVER, self.SPRINGNOTE_PORT))
        connection = httplib.HTTPSConnection("%s:%d" % (self.SPRINGNOTE_SERVER, 443))
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
        
    def fetch_access_token(self, token):
        oauth_request = self.create_oauth_request_for_access_token(token)
                
#        connection = httplib.HTTPSConnection("%s:%d" % (self.SPRINGNOTE_SERVER, self.SPRINGNOTE_PORT))
        connection = httplib.HTTPSConnection("%s:%d" % (self.SPRINGNOTE_SERVER, 443))
        connection.request(oauth_request.http_method, self.ACCESS_TOKEN_URL, headers=oauth_request.to_header()) 
        response = connection.getresponse()
        body = response.read()
#        print oauth_request, dir(oauth_request), oauth_request.http_method, self.ACCESS_TOKEN_URL, oauth_request.to_header(), body
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
        
#        print url
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.access_token, http_method='GET', http_url=url, parameters=parameters)
        oauth_request.sign_request(self.signature_method, self.consumer, self.access_token)        

        connection = httplib.HTTPConnection("%s:%d" % (self.SPRINGNOTE_SERVER, self.SPRINGNOTE_PORT))
        connection.request('GET', url, headers=oauth_request.to_header())
        response = connection.getresponse()
        body = response.read()

        return Page.from_json(body)


    def authorize_url(self, token):
        return "%s?oauth_token=%s" % (self.AUTHORIZATION_URL, token.key)
        

    def create_page(self,title,source=None,domain=None):
#        url = "%s://%s/pages.json" % (self.SPRINGNOTE_PROTOCOL, self.SPRINGNOTE_SERVER)
        url = "%s://%s/pages.xml" % (self.SPRINGNOTE_PROTOCOL, self.SPRINGNOTE_SERVER)
        parameters = {}
        newpage = Page()
        newpage.title = title
        newpage.source = source


#        print "url:: %s" % url

        if domain:
            parameters['domain'] = domain
            url += "?domain=%s" % domain
        else:
            url += "?"

### URL에 해보자
#        for key,value in newpage.to_write_param().iteritems():
#            url += "&%s=%s" % (urllib.quote(key), urllib.quote(value))
#            url += "&%s=%s" % (key, urllib.quote(value))
        
        print "url:: %s" % url
####

        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.access_token, http_method='POST', http_url=url, parameters=parameters)
        oauth_request.sign_request(self.signature_method, self.consumer, self.access_token)

#        connection = httplib.HTTPConnection("%s:%d" % (self.SPRINGNOTE_SERVER, self.SPRINGNOTE_PORT))
        connection = httplib.HTTPSConnection("%s:%d" % (self.SPRINGNOTE_SERVER, 443))
#        connection = httplib.HTTPSConnection("%s" % self.SPRINGNOTE_SERVER)
        myheaders = oauth_request.to_header()


### headers에 해보자
#        headers.update(json = newpage.to_write_json())
#        headers.update(xml = urllib.quote(newpage.to_write_xml()))
        myheaders.update(newpage.to_write_param())

        connection.request(oauth_request.http_method, url, headers=myheaders)
        print "headers ::::::: %s" % myheaders
#        connection.request(oauth_request.http_method, url, headers=oauth_request.to_header(),body=body)
        response = connection.getresponse()
        body = response.read()
        print body



class SpringnoteError:
    class NotAuthorized(RuntimeError):
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

    def from_json(body):
        newPage = Page()
        newPage.parse_json(body)
        return newPage
    from_json = staticmethod(from_json)

    def to_param(self):
        result = {}
        for attr_name,attr_value in self.__dict__.iteritems():
#            if(attr_value != None) and (attr_value != False):
#                result['page[%s]' % attr_name] = attr_value
            result['page[%s]' % attr_name] = attr_value
        return result

    def to_json(self):
#        return json.dumps(self.__dict__)
        result = {}
        for key,value in self.__dict__.iteritems():
            if value != None:
                result[key] = value
        print "\nreulst:::\n%s" % result
        return json.dumps(result)

    def to_write_param(self):
        result = {}
        result['page[title]'] = self.title
        result['page[source]'] = self.source
#        result['page[relation_is_part_of]'] = self.relation_is_part_of
#        result['page[tags]'] = self.tags
        return result


    def to_write_json(self):
        result = {}
        result['title'] = self.title
        result['source'] = self.source
        result['relation_is_part_of'] = self.relation_is_part_of
        result['tags'] = self.tags
        return json.dumps(result)

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
    token = "KUo2OdVplBeXmG4oSiWfA"
    token_secret = "KSHdHxWfoP9o158RYiQ05SEtVYCHRBy5VFSwbiRB5Y"
    id = 2759692
    access_key = "yzlqEHF22FmATMyh72TxsA"
    access_secret = "uFHI07nwCMD6XK5ilaR8WuHsJUx4jL9q6V9vgn240"

    client = SpringnoteClient(token,token_secret)
#    request_token = client.fetch_request_token()
    
#    print client.authorize_url(request_token)
#    raw_input("please Enter...")

#    access_token = client.fetch_access_token(request_token)
    access_token = client.set_access_token_directly(access_key,access_secret)
    print access_token.key, access_token.secret

#    page = client.get_page(id, domain='loocaworld')
    result = client.create_page(title="titleis this",source="this is body",domain="loocaworld")
    print "----body----"
#    print page.source
    print result
    print "------------"


    


if(__name__=='__main__'):
    run()



