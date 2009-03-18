#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import springnote_client
import notegui
import wx
import re

MEMO_TYPE_NORMAL = 1
MEMO_TYPE_TODO = 2


#DEFAULT_FILE_NAME = "access_file.txt"
DEFAULT_FILE_NAME = "user_file.txt"

class SpringMemo:
    def __init__(self):
        self.notegui = notegui.NoteTaskBar(self)
        self.memos = []
        self.rootmemo = None
        self.authdialog = None
        self.is_auth_save = False       #access_token을 저장 하는 가
        self.access_token = None
        self.access_token_secret = None

        self.init_app()

    def init_app(self):
        self.user_authorize()
        self.rootmemo = Memo.get_root_memo()
        self.init_all_memos()


#    def find_access_file(self):
#        if os.path.exists(DEFAULT_FILE_NAME):
#            access_file = file(DEFAULT_FILE_NAME,'r')
#            str = access_file.read()
#            str = str[0:len(str)-1]  # EOF 삭제
#            arr = str.split(' ')
#            return arr
#        return None

    def get_user_file(self):
        ''' 사용자의 컴퓨터에 저장될 파일을 연다
            access_token, access_token_secret, is_auth_save
        '''
        if os.path.exists(DEFAULT_FILE_NAME):
            user_file = file(DEFAULT_FILE_NAME,'r')
            data_arr = user_file.read().split('\n')
            self.access_token = data_arr[0]
            self.access_token_secret = data_arr[1]
#            self.is_auth_save = bool(data_arr[2])
            self.is_auth_save = True #이미 저장되어있으므로 지금도 True
            user_file.close()
            return True
        return False

    def save_user_file(self,key,secret):
        user_file = file(DEFAULT_FILE_NAME,'w')
        user_file.write(key + '\n')
        user_file.write(secret + '\n')
        user_file.close()

    def delete_user_file(self):
        os.remove(DEFAULT_FILE_NAME)

    def check_auth_save(self,):
        if self.is_auth_save:
            self.save_user_file(self.access_token,self.access_token_secret)
        else:
            self.delete_user_file()


    def user_authorize(self):
        ''' authorize 파일이 있는지 확인하고 있으면 client바로 설정,
            없으면 client를 이용해 url을 만들고 인증하여 설정 '''
        client = springnote_client.SpringnoteClient()
        confirmed = False
#        access_arr = self.find_access_file()
#        if access_arr:
        if self.get_user_file():
            client.set_access_token_directly(self.access_token,self.access_token_secret)
        else:
            request_token = client.fetch_request_token()
#            self.notegui.show_authorize(authorize_url(request_token))

            while confirmed == False:
                self.authdialog = notegui.AuthDialog(auth_url=client.authorize_url(request_token))
                rval = self.authdialog.ShowModal()
                #여기서 대기, dialog을 띄우고 ShowModal로 인증을 기다린다
                if rval == wx.ID_OK:
                    #여기서 인증 에러 나면, 앞 위치로 돌아가 "다시한번" alert창
                    #(SpringnoteError.NotAuthorized 익셉션 발생하면)
                    try:
                        access_token = client.fetch_access_token(request_token)
                    except springnote_client.SpringnoteError.NotAuthorized:
                        confirmed = False
                    else:
                        self.is_auth_save = self.authdialog.is_auth_save
                        if self.is_auth_save:
                            self.save_user_file(access_token.key,access_token.secret)
                        confirmed = True
                        self.authdialog.Destroy()

                elif rval == wx.ID_CANCEL:
                    confirmed = True
                    self.quit_app()


        springnote_client.Page.set_page_client(client)

    def create_new_memo(self, type, title, rel=None, sub=False):
        ''' Memo 생성, self.memos에 append '''
        ''' sub : rootpage의 sub로 생성한다 '''
        if sub == True:
#            memo = Memo(type,title,rel=self.rootmemo.page.identifier)
            memo = Memo.create(type,title,rel=self.rootmemo.page.identifier)
        else:
            memo = Memo(type,title,rel)
        self.memos.append(memo)
        return memo


    def init_all_memos(self):
        ''' Root페이지와 하부 모든 페이지를 가져온다 '''
        pages = springnote_client.Page.get_all_pages(self.rootmemo)

        if not pages:
            return

        for page in pages:
            memo = Memo.from_page(page)
            self.memos.append(memo)

    def quit_app(self,memo_update=False,save_auth=False):
        ''' note_update가 True면 전체 Memo를 돌아가며 최신인지 아닌지 판단,
            저장한다. save_auth가 True면, 현재 access_file과 비교하여 저장
        '''
        exit(1)
        

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

        memo.header = PageHeader(type=type)

        memo.view = memo.get_view(type=type,title=title)

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

    def delete_memo(self):
        if self.view.IsShown():
            self.view.Close()
        self.view.Destroy()
        self.page.delete_page()
        

    def get_save_source(self,view=None,header=None):
        ''' self.view의 데이터를 시리얼라이즈 하여(self.view.serialize?)
            self.header.make_source_from_header() 와 합쳐서 업로드
            page와 header가 있으면 그걸로, 없으면 self.으로..
        /// view가 열리지 않은 page라면?
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
#        if header.is_open == True: #열린상태일때만 생김
#            memo.view = memo.get_view(header.type,page.title)
        memo.view = memo.get_view(header.type,page.title) #무조건 생김
        return memo

    def set_title(self,title):
        self.view.initTitle(title)
        self.page.title = title

    def get_view(self,type,title,is_open=True,parent=None,id=-1):
        print "type :: %d" % type
        if type == MEMO_TYPE_NORMAL:
            view = notegui.NormalNote(parent,id,title,self)
        print "type : %d" % type
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
#    springmemo.user_authorize()
#    print "now getroot"
#    springmemo.rootmemo = Memo.get_root_memo()
#    print "root :: %s" % springmemo.rootmemo.page
#    springmemo.init_all_memos()

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



