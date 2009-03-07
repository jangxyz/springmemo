#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import springnote_client
import notegui
import wx

MEMO_TYPE_NORMAL = 1

DEFAULT_FILE_NAME = "access_file.txt"

class SpringMemo:
    def __init__(self):
        self.notegui = notegui.NoteTaskBar(self)
        self.memos = []
        #self.rootmemo = Memo.get_root_memo()

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
            #여기서 대기
            access_token = client.fetch_access_token(request_token)

        springnote_client.Page.set_page_client(client)

    def create_new_memo(self,type, title, rel=None):
        ''' Memo 생성, self.memos에 append '''
        memo = Memo(type,title,rel)
        self.memos.append(memo)
        return memo

class Memo:
    def __init__(self, type=None, title=None, rel=None):
        ''' writer생성 후 연결(writer내에서 자동으로 createpage..) '''
#        self.view = None
#        if type != None and title != None:

#        self.view = notegui.NoteGui
        self.page = springnote_client.Page.create_new_page(type,title,rel)

    @staticmethod
    def get_root_memo():
        memo = Memo()
        memo.model = springnote_client.Model.get_root_model(memo)


#### Run() Method ####


def run():
    app = notegui.wx.App()
    springmemo = SpringMemo()
    app.MainLoop()


#### for Main ####

if __name__=="__main__":
    run()
