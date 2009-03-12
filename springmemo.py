#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import springnote_client
import notegui
import wx
import re

MEMO_TYPE_NORMAL = 1
MEMO_TYPE_TODO = 2


DEFAULT_FILE_NAME = "access_file.txt"

class SpringMemo:
    def __init__(self):
        self.notegui = notegui.NoteTaskBar(self)
        self.memos = []
        self.rootmemo = None

    def find_access_file(self):
        if os.path.exists(DEFAULT_FILE_NAME):
            access_file = file(DEFAULT_FILE_NAME,'r')
            str = access_file.read()
            str = str[0:len(str)-1]  # EOF 삭제
            arr = str.split(' ')
            return arr
        return None


    def user_authorize(self):
        ''' authorize 파일이 있는지 확인하고 있으면 client바로 설정,
            없으면 client를 이용해 url을 만들고 인증하여 설정 '''
        client = springnote_client.SpringnoteClient()
        #file check
        access_arr = self.find_access_file()
        #if ok,
        if access_arr:
            client.set_access_token_directly(access_arr[0],access_arr[1])
        else:
        #if not,
            request_token = client.fetch_request_token()
            self.notegui.show_authorize(authorize_url(request_token))
            #여기서 대기, dialog을 띄우고 ShowModal로 인증을 기다린다
            access_token = client.fetch_access_token(request_token)
            #여기서 인증 에러 나면, 앞 위치로 돌아가 "다시한번" alert창

        springnote_client.Page.set_page_client(client)

    def create_new_memo(self, type, title, rel=None, sub=False):
        ''' Memo 생성, self.memos에 append '''
        ''' sub : rootpage의 sub로 생성한다 '''
        if sub == True:
            memo = Memo(type,title,rel=self.rootmemo.page.identifier)
        else:
            memo = Memo(type,title,rel)
        self.memos.append(memo)
        return memo

    def init_all_memos(self):
        ''' Root페이지와 하부 모든 페이지를 가져온다 '''
        pages = springnote_client.Page.get_all_pages(self.rootmemo)

        for page in pages:
            memo = Memo.from_page(page)
#            if memo != None:
#                self.memos.append(memo)
            self.memos.append(memo)


class Memo:
    def __init__(self, view=None, page=None, header=None):
        self.view = view
        self.page = page
#        self.type = type       ?? 필요한가 ??
        self.header = header

    @staticmethod
    def create(type=None,title=None,rel=None,tags=None):
        ''' 완전히 새로 만드는 부분 '''
        memo = Memo()

        memo.view = memo.get_view(type=type,title=title)
        memo.header = PageHeader(type=type)
        default_source = memo.get_save_source()

        memo.page = springnote_client.Page.create_new_page(title,rel=rel,source=default_source,tags=tags) #domain?? skip!

    def save_memo(self):
        ''' 현재 memo를 저장한다 
            self.get_save_source()를 이용해 데이터를 받아서 Page객체를 설정,
            (page.source에 저장,)
            Page에서 저장하는 방식.. 
        '''
        source = self.get_save_source()
        print "source :: %s" % source

        self.page.save_page(source=source)

    def close_memo(self):
        self.header.is_open = False
        self.save_memo()


    def get_save_source(self,view=None,header=None):
        ''' self.view의 데이터를 시리얼라이즈 하여(self.view.serialize?)
            self.header.make_source_from_header() 와 합쳐서 업로드
            page와 header가 있으면 그걸로, 없으면 self.으로..
        '''
        if view == None:
            view = self.view
        if header == None:
            header = self.header
        source = view.SerializeBody()
        source += header.make_source_from_header()
        return source

    @staticmethod
    def from_page(page):
        ''' page정보로 Memo 생성
         page의 header로, On상태일때 view를 Show해줌
        '''
        header = PageHeader.parse_header_from_source(page.source)
        memo = Memo(page=page,header=header)
        if header.is_open == True:
            print "open open"
            memo.view = memo.get_view(header.type,page.title)
        return memo


    def get_view(self,type,title,is_open=True,parent=None,id=-1):
        if type == MEMO_TYPE_NORMAL:
            view = notegui.NormalNote(parent,id,title,self)
        return view


    @staticmethod
    def get_root_memo():
        memo = Memo()
        memo.page = springnote_client.Page.get_root_page()
        return memo



class PageHeader:
    re_find_header = re.compile("<div[^>]*?id=\"page_header\"[^>]*?>(.*?)</div>",re.M|re.I|re.U|re.S)
    re_get_all_attrs = re.compile("<p[^>]*?id=\"(.*?)\"[^>]*?>(.*?)</p>",re.M|re.I|re.U|re.S)
    typeset = {
            'is_open': lambda x: (x == "False" and False)\
                    or (x == "True" and True),
            'type': int
            }
    attrset = ['is_open','type']

    def __init__(self,type=None,is_open=True):
#        self.is_open = None
#        for attr_name in PageHeader.attrset:
#            setattr(self, attr_name, None)
        if type:
            self.type = type
        if is_open:
            self.is_open = True

    def make_source_from_header(self):
        source = ""
        for attr_name in PageHeader.attrset:
            source += "<p id=\"%s\">%s</p>"% (attr_name,getattr(self,attr_name))

        source = "<div id=\"page_header\" style=\"display:none;\">%s</div>" % source

        return source




    @staticmethod
    def parse_header_from_source(source):
        ph = PageHeader()
        header_text = PageHeader.re_find_header.findall(source)
        attrs = PageHeader.re_get_all_attrs.findall(header_text[0])
        print attrs

        for attrset in attrs:
            setattr(ph,attrset[0],PageHeader.typeset[attrset[0]](attrset[1]))

        return ph


#### Run() Method ####


def run():
    app = notegui.wx.App()
    springmemo = SpringMemo()
    springmemo.user_authorize()
    print "now getroot"
    springmemo.rootmemo = Memo.get_root_memo()
    print "root :: %s" % springmemo.rootmemo.page
    springmemo.init_all_memos()

    app.MainLoop()

def run2():
    is_open = True
    source = '''
<div id="body">
this is real body.<br />
and this is a text.<br />
</div>
Here is a HIDDEN header for 
<div id="page_header"><p id="is_open">%s</p><p id="type">1</p></div>
SpringMemo! Don't delete this line PLEASE :)
        ''' % (str(is_open))

    header = PageHeader.parse_header_from_source(source)




#### for Main ####

if __name__=="__main__":
    run()
#    run2()



