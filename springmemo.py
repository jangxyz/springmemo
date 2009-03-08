#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import springnote_client
import notegui
import wx

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
            memo = None
            memo = Memo.from_page(page,MEMO_TYPE_NORMAL)
            if memo != None:
                self.memos.append(memo)


class Memo:
    def __init__(self, type=None, title=None, rel=None):
        ''' writer생성 후 연결(writer내에서 자동으로 createpage..) '''
        self.view = None
        self.page = None
        self.type = type

        if title != None:
            self.page = springnote_client.Page.create_new_page(title,rel)
    
        if type != None:
            self.view = self.get_view(type=type,title=title)


    def get_view(self,type,parent=None,id=-1,title=""):
        if type == MEMO_TYPE_NORMAL:
            view = notegui.NormalNote(parent,id,title,self)
        return view


    @staticmethod
    def from_page(page,type):
        ''' page정보로 Memo 생성'''
        ''' page의 header로, On상태일때 view를 Show해줌 '''
        '''  '''

        memo = Memo()
        memo.page = page
        memo.view = memo.get_view(type=type)
        return memo


    @staticmethod
    def get_root_memo():
        memo = Memo()
        memo.page = springnote_client.Page.get_root_page()
        return memo


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


#### for Main ####

if __name__=="__main__":
    run()
