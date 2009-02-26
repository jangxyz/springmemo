#-*-coding:utf8-*-
#!/usr/bin/python
import wx
import os

ID_OPEN = 1
ID_SAVE = 2
ID_QUIT = 3
ID_TEXT = 4
ID_STATUS = 4
ID_SAVEAS = 5
ID_TASK_NEW = 6
ID_TASK_LIST = 7
ID_TASK_CONFIG = 8
ID_TASK_QUIT = 9

class NoteTaskBar(wx.TaskBarIcon):
    def __init__(self):
        wx.TaskBarIcon.__init__(self)
        icon = wx.Icon('./nicotine.ico', wx.BITMAP_TYPE_ICO,25,25)
        icon.SetWidth(25)
        icon.SetHeight(25)
        self.SetIcon(icon,"springmemo")
        self.initMenu()

    def initMenu(self):
        self.menu = wx.Menu()
        task_new = wx.MenuItem(self.menu, ID_TASK_NEW, '새 노트')
        task_list = wx.MenuItem(self.menu, ID_TASK_LIST, '노트 목록')
        task_config = wx.MenuItem(self.menu, ID_TASK_CONFIG, '환경 설정')
        task_quit = wx.MenuItem(self.menu, ID_TASK_QUIT, '종료')
        self.menu.AppendItem(task_new)
        self.menu.AppendItem(task_list)
        self.menu.AppendItem(task_config)
        self.menu.AppendItem(task_quit)
        self.Bind(wx.EVT_MENU, self.OnNew, id=ID_TASK_NEW)
        self.Bind(wx.EVT_MENU, self.OnList, id=ID_TASK_LIST)
        self.Bind(wx.EVT_MENU, self.OnConfig, id=ID_TASK_CONFIG)
        self.Bind(wx.EVT_MENU, self.OnQuit, id=ID_TASK_QUIT)


        wx.EVT_TASKBAR_RIGHT_UP(self,self.OnTaskBarRight)

    def OnTaskBarRight(self,event):
        self.PopupMenu(self.menu)

    def OnNew(self,event):
        print 'new'
    def OnList(self,event):
        print 'list'
    def OnConfig(self,event):
        print 'config'
    def OnQuit(self,event):
        print 'quit'





class NoteGui(wx.Frame):
    def __init__(self,parent,id,title):
        self.initData()
        self.initGUI(parent,id,title)
        self.Centre()
        self.Show(True)
        
    def initData(self):
        self.workingDir = None
        self.text = None
        self.status = None
        
        
    def initGUI(self,parent,id,title):
        wx.Frame.__init__(self,parent,id,title,size=(250,200))
        
        menubar = wx.MenuBar()
        file = wx.Menu()

        open = wx.MenuItem(file,ID_OPEN,'&Open\tCtrl+O')
        save = wx.MenuItem(file,ID_SAVE,'&Save\tCtrl+S')
        saveas = wx.MenuItem(file,ID_SAVEAS,'Save &As\tCtrl+A')
        quit = wx.MenuItem(file,ID_QUIT,'&Quit\tCtrl+Q')
        
#        quit.SetBitmap(wx.Bitmap('icons/exit.png'))

        file.AppendItem(open)
        file.AppendItem(save)
        file.AppendItem(saveas)
        file.AppendSeparator()
        file.AppendItem(quit)
        
        self.Bind(wx.EVT_MENU,self.OnOpen,id=ID_OPEN)
        self.Bind(wx.EVT_MENU,self.OnSave,id=ID_SAVE)
        self.Bind(wx.EVT_MENU,self.OnSaveAs,id=ID_SAVEAS)
        self.Bind(wx.EVT_MENU,self.OnQuit,id=ID_QUIT)
        
        
        menubar.Append(file, '&File')
        self.SetMenuBar(menubar)
        
        vbox = wx.BoxSizer(wx.VERTICAL)

# hbox        
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        static = wx.StaticText(self,-1,'Status:',(5,5))
        self.status = wx.TextCtrl(self,ID_STATUS)
        self.status.Enable(False)
        hbox.Add(static,0,wx.EXPAND,0)
        hbox.Add(self.status,1,wx.EXPAND,0)

# vbox

        self.text = wx.TextCtrl(self,ID_TEXT,style=wx.TE_MULTILINE)

        vbox.Add(self.text,1,wx.EXPAND|wx.ALL,0)
        vbox.Add(hbox,0,wx.EXPAND|wx.TOP,0)
        

        self.SetSizer(vbox)
        
        

    def OnOpen(self,event):
        self.SetStatus('OnOpen')
        dlg = wx.FileDialog(self,message="열기",defaultDir=os.getcwd(),wildcard="*",
            style=wx.OPEN|wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            self.workingDir = dlg.GetPath()
            self.OpenFile(self.workingDir)
        else:
            self.SetStatus('open canceled')
            return False
        
        
    def OpenFile(self,path):
        file = open(self.workingDir)
        str = file.read()
        self.SetText(str)
        
            
    def GetSaveDir(self):
        self.SetStatus('GetSaveDir')
        dlg = wx.FileDialog(self,message="저장",defaultDir=os.getcwd(),wildcard="*",
            style=wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            self.workingDir = dlg.GetPath()
            return True
        else:
            return False

    def OnSave(self,event):
        if (self.workingDir == None):            
            ret = self.GetSaveDir()
            if(ret == False):
                self.SetStatus('save canceled.')
                return False
        if((self.SaveFile(self.workingDir))== True):
            wx.MessageBox("Saved.","SpringMemo")
            self.SetStatus("saved")
            
    def OnSaveAs(self,event):
        ret = self.GetSaveDir()
        if(ret == False):
            self.SetStatus('saveas canceled.')
            return False
        if((self.SaveFile(self.workingDir))== True):
            wx.MessageBox("Saved As.","SpringMemo")
            self.SetStatus("saved as")

        
    
    def SaveFile(self,path):
#        if(os.path.exists(path)):
#            ret = wx.MessageBox('덮어 쓰시겠습니까?','SpringMemo',wx.YES_NO|wx.CENTRE|wx.NO_DEFAULT,self,100,100)
#            if(ret == wx.NO):
#                return
        file = open(path,"w+")
        file.write(self.GetText())
#        self.text.SaveFile(path)
        return True

        
    def OnQuit(self,event):
        self.Close()
        
    def SetText(self,str):
        self.text.SetValue(str)
    
    def GetText(self):
        return self.text.GetValue()
        
    def SetStatus(self,str):
        self.status.SetValue(str)

if __name__ == "__main__":
    app = wx.App()
    NoteTaskBar()
    NoteGui(None,-1,'NoteGUI')
    app.MainLoop()

