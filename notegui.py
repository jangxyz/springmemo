#-*-coding:utf8-*-
#!/usr/bin/python
import wx
import os

ID_BUTTON_CLOSE = 2
ID_STATIC_TITLE = 3
ID_STATIC_STATUS = 4
ID_PANEL_MAINPANEL = 5
ID_TASK_NEW = 6
ID_TASK_LIST = 7
ID_TASK_CONFIG = 8
ID_TASK_QUIT = 9

DEFAULT_TIMER_TIME = 5000

ID_STATUS_MODIFIED = 1
ID_STATUS_RECENT = 2



class NoteTaskBar(wx.TaskBarIcon):
    def __init__(self,controller=None):
        wx.TaskBarIcon.__init__(self)
        icon = wx.Icon('./nicotine2.ico', wx.BITMAP_TYPE_ICO,25,25)
        icon.SetWidth(25)
        icon.SetHeight(25)
        self.SetIcon(icon,"springmemo")
        self.initMenu()
#        print "controller::%s"%controller
        self.select_note = None
        self.controller = controller

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
        print event
        self.PopupMenu(self.menu)

    def OnNew(self,event):
        if self.select_note == None:
            self.select_note = SelectNoteDlg(None,-1,"select Note")
            rval = self.select_note.ShowModal()
            if rval == wx.ID_OK:
                type = self.select_note.selected_type
                title = self.select_note.text_title.GetValue()
                self.controller.create_new_memo(type,title,sub=True)

            self.select_note.Destroy()
            self.select_note = None
        print 'new'

    def OnList(self,event):
        print 'list'

    def OnConfig(self,event):
        print event
        print 'config'

    def OnQuit(self,event):
        print 'quit'
        exit(1)

class SelectNoteDlg(wx.Dialog):
    def __init__(self,parent,id,title):
        # begin wxGlade: MyDialog1.__init__
        wx.Dialog.__init__(self, parent, id, title)
        self.radio_type = wx.RadioBox(self, -1, "radio_box_1", choices=["Normal", "Todo", "Calender"], majorDimension=3, style=wx.RA_SPECIFY_COLS)
        self.label_1 = wx.StaticText(self, -1, "title")
        self.text_title = wx.TextCtrl(self, -1, "")
        self.button_ok = wx.Button(self, wx.ID_OK, "OK")
        self.button_cancel = wx.Button(self, wx.ID_CANCEL, "Cancel")

        self.selected_type = None

        self.__set_properties()
        self.__do_layout()
        self.__set_event_handler()
        # end wxGlade


    def __set_event_handler(self):
        self.Bind(wx.EVT_RADIOBOX,self.OnRadioChanged,self.radio_type)
        self.Bind(wx.EVT_BUTTON,self.OnOk,self.button_ok)
        self.Bind(wx.EVT_BUTTON,self.OnCancel,self.button_cancel)

    

    def __set_properties(self):
        # begin wxGlade: MyDialog1.__set_properties
        self.SetTitle("Select Note")
        self.SetSize((310, 150))
        self.radio_type.SetSelection(0)
        self.text_title.SetMinSize((200, 23))

    def __do_layout(self):
        # begin wxGlade: MyDialog1.__do_layout

        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1.Add(self.radio_type, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 15)
        sizer_3.Add(self.label_1, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_3.Add(self.text_title, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_1.Add(sizer_3, 1, wx.TOP|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 10)
        sizer_2.Add(self.button_ok, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_2.Add(self.button_cancel, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_1.Add(sizer_2, 1, wx.TOP|wx.BOTTOM|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 10)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade


    def OnRadioChanged(self,evt):
        print "changed. %s" % self.radio_type.GetSelection()
        self.selected_type = self.radio_type.GetSelection()

    def OnOk(self,evt):
        if len(self.text_title.GetValue()) > 0:
            self.EndModal(wx.ID_OK)

    def OnCancel(self,evt):
        self.EndModal(wx.ID_CANCEL)




class Note(wx.Frame):
    def __init__(self,parent,id,title,memo):
        self.memo = memo
        self.body = None        #실제 데이터를 serialize한 값? 최신 값
#        self.recent_body = None
        self.status = None      #status, ID_STATUS_MODIFIED:changed, ID_STATUS_RECENT:last, ..
#        self.is_open = None     #창이 열려있는지, 닫겨있는지

        self.initGUI(parent,id,title)
        self.Centre()
        self.Show(True)
        self.is_open = True
        
    def initData(self):
        ''' for overriding '''
        pass

    def initGUI(self,parent,id,title=""):
        wx.Frame.__init__(self,parent,id,title,size=(200,250),style=wx.NO_BORDER)
        
        vbox = wx.BoxSizer(wx.VERTICAL)

# hbox        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.title = wx.StaticText(self,ID_STATIC_TITLE,'',(0,0))
        self.status = wx.StaticText(self,ID_STATIC_STATUS,'o',(0,0),size=(20,20),style=wx.ALIGN_CENTRE|wx.SUNKEN_BORDER)
        self.button_close = wx.Button(self,ID_BUTTON_CLOSE,"X",(0,0),size=(20,20),style=wx.SIMPLE_BORDER)
        hbox.Add(self.title,1,wx.EXPAND,0)
        hbox.Add(self.status,0,wx.EXPAND,1)
        hbox.Add(self.button_close,0,wx.EXPAND,1)

# vbox
        self.mainpanel = wx.Panel(self,ID_PANEL_MAINPANEL)
        vbox.Add(hbox,0,wx.EXPAND|wx.TOP,0)
        vbox.Add(self.mainpanel,1,wx.EXPAND|wx.ALL,0)

        self.Bind(wx.EVT_BUTTON,self.OnClose,id=ID_BUTTON_CLOSE)

        self.SetSizer(vbox)
     
        self.Bind(wx.EVT_TIMER,self.OnTimerEvent)
        self.timer = wx.Timer(self)

    def StartTimer(self,max_time=None):
        if self.timer.IsRunning():
            self.timer.Stop()
        if max_time:
            self.timer.Start(max_time)
        else:
            self.timer.Start(DEFAULT_TIMER_TIME)

    def OnTimerEvent(self,evt):
        ''' 자동 저장 부분 '''
        print "event finished"
        self.timer.Stop()
        
    
    def SetStatusModified(self):
        self.status.SetValue("+")

    def SetStatusRecent(self):
        self.status.SetValue("o")

    def SetTitle(self,str):
        self.title.SetValue(str)

    def OnClose(self,event):
        print "closeclose"
        self.is_open = False

    def SetChangeState(self):
        ''' 내용이 변경되었는지 확인하는 부분(이벤트 바인딩 처리) '''
        pass

    def initCustomGUI(self):
        ''' for overriding '''
        pass

    
    def GetBody(self):
        ''' for overriding '''
        pass
        
    def SerializeBody(self):
        ''' for overriding '''
        pass

    def UpdateNote(self):
        '''  '''

class NormalNote(Note):
    ID_TEXT = 2

    def __init__(self,parent,id,title,memo=None):
        Note.__init__(self,parent,id,title,memo)
        self.initCustomGUI()
        self.SetChangeState()
        self.initData()

    def initCustomGUI(self):
        ''' for overriding '''
        custombox = wx.BoxSizer(wx.HORIZONTAL)
        self.text = wx.TextCtrl(self.mainpanel,NormalNote.ID_TEXT,pos=(0,0),style=wx.TE_MULTILINE,name="text")

        custombox.Add(self.text,1,wx.EXPAND,1)
        self.mainpanel.SetSizer(custombox)
        self.Layout()

    def initData(self):
        print "text : %s" %self.memo.page.source
        self.SetBody(self.memo.page.source)
 
    def SetChangeState(self):
        self.Bind(wx.EVT_TEXT,self.OnChange,id=NormalNote.ID_TEXT)
        if self.text.IsModified():
            print "mmm"
    
    def OnChange(self,evt):
        self.StartTimer()
        print "mmm"

        
    def SerializeBody(self):
        ''' for overriding '''
        pass

    def SetBody(self,str):
        self.text.SetValue(str)
    
    def GetBody(self):
        return self.text.GetValue()



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
        file = open(path,"w+")
        file.write(self.GetText())
        return True

        
    def OnQuit(self,event):
#        self.Close()
        pass
        
    def SetText(self,str):
        self.text.SetValue(str)
    
    def GetText(self):
        return self.text.GetValue()
        
    def SetStatus(self,str):
        self.status.SetValue(str)

if __name__ == "__main__":
    app = wx.App()
    NoteTaskBar()
#    NoteGui(None,-1,'NoteGUI')
#    Note(None,-1,'Note')
    NormalNote(None,-1,'Note')
    app.MainLoop()

