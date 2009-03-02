import springnote_client
import notegui
import wx

class SpringMemo:
    def __init__(self):
        self.client = springnote_client.SpringnoteClient()
        self.notegui = notegui.NoteTaskBar(self)




#### Run() Method ####


def run():
    app = notegui.wx.App()
    springmemo = SpringMemo()
    app.MainLoop()


#### for Main ####

if __name__=="__main__":
    run()
