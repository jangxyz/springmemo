import springnote_client
import notegui
import wx

MEMO_TYPE_NORMAL = 1

class SpringMemo:
    def __init__(self):
        self.client = springnote_client.SpringnoteClient()
        self.notegui = notegui.NoteTaskBar(self)
        self.memos = []
        self.rootmemo = Memo.get_root_memo(self)

    def create_new_memo(self,type,title):
        ''' Memo 생성, self.memos에 append '''
        memo = Memo(type,title)
        self.memos.append(memo)
        




class Memo:
    def __init__(self,controller,type=None,title=None):
        ''' writer생성 후 연결(writer내에서 자동으로 createpage..) '''
        self.view = None
        self.controller = controller
        iftype != None and title != None:
            self.model = springnote_client.Model.create_new_model(self,type,title)

    @staticmethod
    def get_root_memo(controller):
        memo = Memo(controller)
        memo.model = springnote_client.Model.get_root_model(self)


#### Run() Method ####


def run():
    app = notegui.wx.App()
    springmemo = SpringMemo()
    app.MainLoop()


#### for Main ####

if __name__=="__main__":
    run()
