#-*-coding:utf8-*-
#!/usr/bin/python
import wx
import wx.grid
import os
import re
import webbrowser

DEFAULT_TIMER_TIME = 5000

COLOR_245 = wx.Colour(245,245,245)
COLOR_240 = wx.Colour(240,240,240)
COLOR_230 = wx.Colour(230,230,230)
COLOR_220 = wx.Colour(220,220,220)



class NoteTaskBar(wx.TaskBarIcon):
    def __init__(self,controller=None):
        wx.TaskBarIcon.__init__(self)
        icon = wx.Icon('./nicotine2.ico', wx.BITMAP_TYPE_ICO,25,25)
        icon.SetWidth(25)
        icon.SetHeight(25)
        self.SetIcon(icon,"springmemo")
        self.initMenu()
        self.select_memo = None
        self.memo_list = None
        self.configdlg = None
        self.controller = controller

    def initMenu(self):
        self.menu = wx.Menu()
        task_new = wx.MenuItem(self.menu, -1, u'새 메모')
        task_list = wx.MenuItem(self.menu, -1, u'메모 목록')
        task_config = wx.MenuItem(self.menu, -1, u'환경 설정')
        task_quit = wx.MenuItem(self.menu, -1, u'종료')
        self.menu.AppendItem(task_new)
        self.menu.AppendItem(task_list)
        self.menu.AppendItem(task_config)
        self.menu.AppendItem(task_quit)
        self.Bind(wx.EVT_MENU, self.OnNew, task_new)
        self.Bind(wx.EVT_MENU, self.OnList, task_list)
        self.Bind(wx.EVT_MENU, self.OnConfig, task_config)
        self.Bind(wx.EVT_MENU, self.OnQuit, task_quit)


        wx.EVT_TASKBAR_RIGHT_UP(self,self.OnTaskBarRight)

    def OnTaskBarRight(self,event):
        print event
        self.PopupMenu(self.menu)

    def OnNew(self,event):
        if self.select_memo == None:
            self.select_memo = SelectNoteDlg(None,-1,u"메모 선택")
            rval = self.select_memo.ShowModal()
            if rval == wx.ID_OK:
                type = self.select_memo.GetSelectedType()
                title = self.select_memo.text_title.GetValue()
                self.controller.create_new_memo(type,title,sub=True)

            self.select_memo.Destroy()
            self.select_memo = None

    def OnList(self,event):
        self.memo_list = MemoList(None,-1,"",self.controller)

    def OnConfig(self,event):
        if self.configdlg == None:
            self.configdlg = ConfigDlg(None,-1,u"환경설정",self.controller.is_auth_save)
            rval = self.configdlg.ShowModal()
            if rval == wx.ID_OK:
                self.controller.is_auth_save = self.configdlg.is_auth_save
                self.controller.check_auth_save()

            self.configdlg.Destroy()
                

    def OnQuit(self,event):
        self.controller.quit_app()


class AuthDialog(wx.Dialog):
    def __init__(self,parent=None,id=-1,auth_url=None):
        title = u"SpringMemo 인증"
        wx.Dialog.__init__(self, parent, id, title)

        self.is_auth_clicked = False
        self.auth_url = auth_url
        self.is_auth_save = False

        self.SetBackgroundColour(COLOR_240)
        self.bitmap_guide = wx.StaticBitmap(self, -1, wx.Bitmap(u"guide_image.png", wx.BITMAP_TYPE_ANY))
        self.button_goauth = wx.Button(self, -1, u"인증하러 가기")
        self.button_ok = wx.Button(self, -1, u"다음으로")
        self.button_quit = wx.Button(self, -1, u"종료")
        self.checkbox_issave = wx.CheckBox(self, -1, u"인증저장")
        self.__set_properties()
        self.__do_layout()
        self.set_event()

    def set_event(self):
        self.Bind(wx.EVT_BUTTON,self.OnGoAuth,self.button_goauth)
        self.Bind(wx.EVT_BUTTON,self.OnOk,self.button_ok)
        self.Bind(wx.EVT_BUTTON,self.OnQuit,self.button_quit)
        self.Bind(wx.EVT_CHECKBOX,self.OnCheck,self.checkbox_issave)

    def __set_properties(self):
        # begin wxGlade: MyDialog1.__set_properties
#        self.SetTitle("SpringMemo 인증창")
#        self.SetSize((400, 350))
#        self.bitmap_guide.SetMinSize((400, 300))
        self.SetSize((600, 450))
        self.bitmap_guide.SetMinSize((600, 400))
        self.button_ok.Enable(False)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyDialog1.__do_layout
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.bitmap_guide, 0, 0, 0)
        sizer_3.Add(self.button_goauth, 1, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 10)
        sizer_3.Add(self.checkbox_issave, 1, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 10)
        sizer_3.Add(self.button_ok, 1, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 10)
        sizer_3.Add(self.button_quit, 1, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 10)
        sizer_2.Add(sizer_3, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 10)
        self.SetSizer(sizer_2)
        self.Layout()
        # end wxGlade


    def OnGoAuth(self,evt):
        ''' self.auth_url을 타겟으로 브라우저를 띄워준다 '''
        webbrowser.open_new(self.auth_url)
        self.is_auth_clicked = True
        self.button_ok.Enable(True)
#        print "i opened : %s" % self.auth_url

    def OnOk(self,evt):
        if self.is_auth_clicked:
            self.EndModal(wx.ID_OK)

    def OnQuit(self,evt):
        self.EndModal(wx.ID_CANCEL)

    def OnCheck(self,evt):
        self.is_auth_save = self.checkbox_issave.GetValue()




class MemoList(wx.Frame):
    def __init__(self,parent=None,id=-1,title=None,controller=None):
        self.controller = controller
        wx.Frame.__init__(self, parent, id, title, style=wx.NO_BORDER)
        self.SetBackgroundColour(COLOR_240)
        self.titlebar = TitleBar(self, -1, u"메모 목록")

        self.__set_properties()
        self.__do_layout()
        self.InitData()
        self.mainbox.Fit(self)

        self.Show(True)

    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
#        self.SetTitle("Note List")
#        self.SetScrollbar(wx.VERTICAL,10,10,10)
#        self.SetSize((310,400))
        self.SetMinSize((310,50))

    def __do_layout(self):
        self.mainbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.mainbox.Add(self.titlebar,0,wx.EXPAND,0)
        self.mainbox.Add(self.vbox,1,wx.EXPAND,0)

        self.SetSizer(self.mainbox)

    def InitData(self):
        memos = self.controller.memos;
        for memo in memos:
            self.vbox.Add(self.MemoNode(memo,parent=self), 1, wx.TOP|wx.BOTTOM, 5)

    def DeleteMemoNode(self,target):
        self.vbox.Remove(target)
        self.mainbox.Fit(self)


    class MemoNode(wx.Panel):
        def __init__(self,memo,parent=None,id=-1):
            wx.Panel.__init__(self, parent, id)

            self.parent = parent
            self.on_modifying = False
            self.memo = memo
            self.hbox = wx.BoxSizer(wx.HORIZONTAL)
            self.text_title = wx.TextCtrl(self, -1, "", style=wx.NO_BORDER|wx.TE_PROCESS_ENTER)
            self.SetBackgroundColour(COLOR_240)
            self.text_title.SetBackgroundColour(COLOR_245)
            self.button_modify = wx.Button(self, -1, u"수정")
            self.button_isopen = wx.Button(self, -1, u"열림")
            self.button_delete = wx.Button(self, -1, u"삭제")

            self.__set_properties()
            self.__do_layout()
            self.SetEvent()

            self.InitData()

        def __set_properties(self):
            self.SetSize((310,35))
            self.text_title.SetMinSize((200, 23))
            self.text_title.SetEditable(False)
            self.button_modify.SetMinSize((40, 25))
            self.button_isopen.SetMinSize((40, 25))
            self.button_delete.SetMinSize((40, 25))
        
        def __do_layout(self):
            self.hbox.Add(self.text_title, 0, wx.LEFT|wx.RIGHT, 5)
            self.hbox.Add(self.button_modify, 0, wx.LEFT, 5)
            self.hbox.Add(self.button_isopen, 0, wx.LEFT, 5)
            self.hbox.Add(self.button_delete, 0, wx.LEFT|wx.RIGHT, 5)
            self.SetSizer(self.hbox)

        def SetEvent(self):
            self.Bind(wx.EVT_BUTTON,self.OnButtonModify,self.button_modify)
            self.Bind(wx.EVT_BUTTON,self.OnButtonIsOpen,self.button_isopen)
            self.Bind(wx.EVT_BUTTON,self.OnButtonDelete,self.button_delete)
            self.Bind(wx.EVT_TEXT_ENTER,self.OnButtonModify,self.text_title)

        def InitData(self):
            self.SetText(self.memo.page.title)
            self.CheckIsOpen()


        def OnButtonModify(self,evt):
            ''' self.text_title을 활성화하고 다른 두버튼을 비활성화 한 다음
                현재 버튼을 '수정완료'쯤으로 바꿔서 수정이 가능하게 한다
                완료 후 page.title을 수정하고 업로드
            '''
            if evt.GetEventType() == wx.EVT_TEXT_ENTER.evtType[0]\
                and not self.on_modifying:
                return

            if not self.on_modifying:
                self.on_modifying = True
                self.text_title.SetBackgroundColour(wx.Colour(250,250,5))
                self.text_title.SetEditable(True)

                self.button_modify.SetLabel(u"저장")
            else:
                if len(self.text_title.GetValue()) > 0:
                    self.memo.set_title(self.text_title.GetValue())
                    self.memo.save_memo()
                    self.text_title.SetBackgroundColour(wx.Colour(245,245,245))
                    self.button_modify.SetLabel(u"수정")
                    self.on_modifying = False
                    self.text_title.SetEditable(False)

                #여기서 저장

        def OnButtonIsOpen(self,evt):
            ''' is_open상태를 수정하고 서버로 업로드  '''
            self.memo.header.is_open = not self.memo.header.is_open
            self.memo.view.CheckShowNote(self.memo.header.is_open)
            self.memo.save_memo()
            self.CheckIsOpen()

        def OnButtonDelete(self,evt):
            ''' 이 메모를 서버에서 삭제하고 프로그램에서도 지운다 '''
            self.parent.controller.memos.remove(self.memo)
            self.memo.delete_memo()
            self.parent.DeleteMemoNode(self)


        def SetText(self,str):
            self.text_title.SetValue(str)

        def CheckIsOpen(self):
            if self.memo.header.is_open:
                self.button_isopen.SetLabel(u"열림")
            else:
                self.button_isopen.SetLabel(u"닫힘")

class ConfigDlg(wx.Dialog):
    def __init__(self,parent,id,title,is_auth_save):
        # begin wxGlade: MyDialog.__init__
        wx.Dialog.__init__(self, parent, id, title,style=wx.NO_BORDER)
        self.is_auth_save = is_auth_save
        self.checkbox_auth_save = wx.CheckBox(self, -1, u"인증 저장")
        self.button_ok = wx.Button(self, -1, u"확인")
        self.button_cancel = wx.Button(self, -1, u"취소")
        self.titlebar = TitleBar(self,-1,title)

        self.__set_properties()
        self.__do_layout()
        self.SetEvent()
        # end wxGlade

    def __set_properties(self):
#        self.SetSize((310, 150))
#        self.text_title.SetMinSize((200, 23))
        self.checkbox_auth_save.SetValue(self.is_auth_save)

    def __do_layout(self):
        # begin wxGlade: MyDialog.__do_layout
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(self.titlebar,0,wx.EXPAND,0)
        sizer_3.Add(self.checkbox_auth_save, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 10)
        sizer_4.Add(self.button_ok, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 10)
        sizer_4.Add(self.button_cancel, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 10)
        sizer_3.Add(sizer_4, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 10)
        self.SetSizer(sizer_3)
        sizer_3.Fit(self)
        self.Layout()
        # end wxGlade


    def SetEvent(self):
        self.Bind(wx.EVT_CHECKBOX,self.OnCheckChanged,self.checkbox_auth_save)
        self.Bind(wx.EVT_BUTTON,self.OnOk,self.button_ok)
        self.Bind(wx.EVT_BUTTON,self.OnCancel,self.button_cancel)

    def OnCheckChanged(self,evt):
        self.is_auth_save = self.checkbox_auth_save.GetValue()

    def OnOk(self,evt):
        self.EndModal(wx.ID_OK)

    def OnCancel(self,evt):
        self.EndModal(wx.ID_CANCEL)




class SelectNoteDlg(wx.Dialog):
    def __init__(self,parent,id,title):
        # begin wxGlade: MyDialog1.__init__
        wx.Dialog.__init__(self, parent, id, title,style=wx.NO_BORDER)
        self.SetBackgroundColour(COLOR_240)
        self.radio_type = wx.RadioBox(self, -1, u"종류", choices=[u"기본노트", u"To-do", u"캘린더"], majorDimension=3, style=wx.RA_SPECIFY_COLS)
        self.label_1 = wx.StaticText(self, -1, u"제목")
        self.text_title = wx.TextCtrl(self, -1, "")

        self.button_ok = wx.Button(self, wx.ID_OK, "OK")
        self.button_cancel = wx.Button(self, wx.ID_CANCEL, "Cancel")
        self.titlebar = TitleBar(self, -1, u"메모 종류 선택")

        self.selected_type = 0

        self.__set_properties()
        self.__do_layout()
        self.SetEvent()

        self.radio_type.SetSelection(0)
        # end wxGlade


    def SetEvent(self):
        self.Bind(wx.EVT_RADIOBOX,self.OnRadioChanged,self.radio_type)
        self.Bind(wx.EVT_BUTTON,self.OnOk,self.button_ok)
        self.Bind(wx.EVT_BUTTON,self.OnCancel,self.button_cancel)

    

    def __set_properties(self):
        # begin wxGlade: MyDialog1.__set_properties
        self.SetSize((310, 150))
        self.radio_type.SetSelection(0)
        self.text_title.SetMinSize((200, 23))

    def __do_layout(self):
        # begin wxGlade: MyDialog1.__do_layout

        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        
        sizer_1.Add(self.titlebar,0,wx.EXPAND,0)

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
#        print "changed. %s" % self.radio_type.GetSelection()
        self.selected_type = self.radio_type.GetSelection()

    def OnOk(self,evt):
        if len(self.text_title.GetValue()) > 0:
            self.EndModal(wx.ID_OK)

    def OnCancel(self,evt):
        self.EndModal(wx.ID_CANCEL)

    def GetSelectedType(self):
        if self.selected_type == 0:
            return 1  #MEMO_TYPE_NORMAL
        elif self.selected_type == 1:
            return 2  #MEMO_TYPE_TODO
        elif self.selected_type == 2:
            return 3  #MEMO_TYPE_SCHEDULE
        else:
            return 0

### Move Panel ####

class MovePanel(wx.Panel):
    def __init__(self,parent,pos,size,style):
        wx.Panel.__init__(self,parent,-1,pos=pos,size=size,style=style)
        self.left_down = False
        self.parentFrame = parent
        self.SetBackgroundColour(COLOR_220)

        while self.parentFrame.GetParent() is not None:
            self.parentFrame = self.parentFrame.GetParent()

        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)

    def OnLeftDown(self, evt):
        self.CaptureMouse()
        self.left_down = True
        pos = self.ClientToScreen(evt.GetPosition())
        origin = self.parentFrame.GetPosition()
        dx = pos.x - origin.x
        dy = pos.y - origin.y
        self.delta = wx.Point(dx, dy)

    def OnLeftUp(self, evt):
        self.ReleaseMouse()
        self.left_down = False

    def OnMouseMove(self, evt):
        if evt.Dragging() and self.left_down:
            pos = self.ClientToScreen(evt.GetPosition())
            fp = (pos.x - self.delta.x, pos.y - self.delta.y)
            self.parentFrame.Move(fp)

### End Move Panel ####


### Title Bar ####

class TitleBar(wx.Panel):
    def __init__(self,parent=None,id=-1,title=None):
#        wx.Panel.__init__(self,parent,id,style=wx.SIMPLE_BORDER)
        wx.Panel.__init__(self,parent,id,style=wx.NO_BORDER)
        self.SetBackgroundColour(COLOR_230)
        self.parentFrame = parent

        while self.parentFrame.GetParent() is not None:
            self.parentFrame = self.parentFrame.GetParent()

        self.titlebox = wx.BoxSizer(wx.HORIZONTAL)
        self.panel_move = MovePanel(self,pos=(0,0),size=(20,20),style=wx.SIMPLE_BORDER)
        self.title = wx.StaticText(self,-1,'',(0,0))
        self.button_close = wx.BitmapButton(self,-1,wx.Bitmap("./icons2/red1.png"),style=wx.NO_BORDER,size=(20,20))

        self.__do_layout()
        self.SetEvent()
        self.title.SetLabel(title)

    def __do_layout(self):

        self.titlebox.Add(self.panel_move,0,wx.EXPAND,1)
        self.titlebox.Add(self.title,1,wx.EXPAND|wx.LEFT|wx.TOP,5)
        self.titlebox.Add(self.button_close,0,wx.EXPAND,0)

        self.SetSizer(self.titlebox)


    def SetEvent(self):
        self.Bind(wx.EVT_BUTTON,self.OnClose,self.button_close)

    def OnClose(self,evt):
#        print "parent : %s" % self.parentFrame
        self.parentFrame.Close()


### End Title Bar ###



class Note(wx.Frame):
    re_get_body = re.compile("<div[^>]*?id=\"body\"[^>]*?>(.*?)</div>",re.M|re.I|re.U|re.S)



    def __init__(self,parent,id,title,memo):
        self.memo = memo
        self.body = None        #실제 데이터를 serialize한 값? 최신 값
        self.is_modified = False

        self.delta = wx.Point(0,0)

        self.initGUI(parent,id,title)
        self.Centre()

        self.initTitle(title)
        self.CheckShowNote()

    def initTitle(self,str):
        self.title.SetLabel(str)

    def initData(self):
        ''' for overriding '''
        pass

    def initGUI(self,parent,id,title=""):
        wx.Frame.__init__(self,parent,id,title,size=(200,250),style=wx.NO_BORDER)
        self.SetBackgroundColour(COLOR_230)
        self.SetClientSize(wx.Size(195,220))
        vbox = wx.BoxSizer(wx.VERTICAL)

# hbox        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.panel_move = MovePanel(self,pos=(0,0),size=(20,20),style=wx.SIMPLE_BORDER)
        self.title = wx.StaticText(self,-1,'',(0,0))
        self.title.Wrap(10)
        self.button_status = wx.BitmapButton(self,-1,wx.Bitmap("./icons2/green1.png"),style=wx.NO_BORDER,size=(20,20))
#        self.button_status.SetBitmapHover(wx.Bitmap("./icons2/green2.png"))

        self.button_close = wx.BitmapButton(self,-1,wx.Bitmap("./icons2/red1.png"),style=wx.NO_BORDER,size=(20,20))
#        self.button_close.SetBitmapHover(wx.Bitmap("./icons2/red2.png"))
#        self.button_close.SetBitmapHover(wx.Bitmap("./icons2/green2.png"))
        hbox.Add(self.panel_move,0,wx.EXPAND,1)
        hbox.Add(self.title,1,wx.EXPAND|wx.LEFT|wx.TOP,5)
        hbox.Add(self.button_status,0,wx.EXPAND,0)
        hbox.Add(self.button_close,0,wx.EXPAND,0)


# vbox
#        self.mainpanel = wx.Panel(self,ID_PANEL_MAINPANEL)
        self.mainpanel = wx.Panel(self,-1)
        vbox.Add(hbox,0,wx.EXPAND|wx.TOP,0)
        vbox.Add(self.mainpanel,1,wx.EXPAND|wx.ALL,0)

        self.Bind(wx.EVT_BUTTON,self.OnClose,self.button_close)
        self.Bind(wx.EVT_BUTTON,self.OnStatus,self.button_status)

        self.SetSizer(vbox)
     
        self.Bind(wx.EVT_TIMER,self.OnTimerEvent)
        self.timer = wx.Timer(self)

    def StartTimer(self,max_time=DEFAULT_TIMER_TIME):
        if self.timer.IsRunning():
            self.timer.Stop()
        self.timer.Start(max_time)

    def StopTimer(self):
        self.timer.Stop()

    def OnTimerEvent(self,evt):
        ''' 자동 저장 부분 '''
        print "event finished"
        self.StopTimer()
        self.UpdateNote()
        self.SetStatusRecent()
        

    
    def SetStatusModified(self):
        self.is_modified = True
        self.button_status.SetBitmapLabel(wx.Bitmap("./icons2/blue1.png"))


    def SetStatusRecent(self):
        self.is_modified = False
        self.button_status.SetBitmapLabel(wx.Bitmap("./icons2/green1.png"))


    def SetTitle(self,str):
        self.title.SetValue(str)

        
    def OnStatus(self,event):
        if self.is_modified:
            self.StopTimer()
            self.UpdateNote()
            self.SetStatusRecent()

    def OnClose(self,event):
        self.CloseNote()
    

    def SetChangeState(self):
        ''' 내용이 변경되었는지 확인하는 부분(이벤트 바인딩 처리) '''
        pass

    def initCustomGUI(self):
        ''' for overriding '''
        pass

    
    def GetBodyFromSource(self):
        ''' for overriding '''
        pass
        
    def SerializeBody(self):
        ''' for overriding '''
        ''' 입력한 데이터를 serialize해서 div에 감싸서 리턴 '''
        pass

    def UpdateNote(self):
        ''' 현재 값으로 springnote에 업로드 한다  '''
        self.memo.save_memo()

    def CloseNote(self):
#        self.Close()
        self.Show(False)
        self.memo.close_memo()
#        self.CheckShowNote()

    def CheckShowNote(self,val=None):
#        if self.memo.header.is_open:
#            self.Show(True)
        if val != None:
            self.Show(val)
        else:
            self.Show(self.memo.header.is_open)


class NormalNote(Note):
    ID_TEXT = 2

    def __init__(self,parent,id,title,memo=None):
        Note.__init__(self,parent,id,title,memo)
        self.initCustomGUI()
        self.initData()
        self.SetChangeState()

    def initCustomGUI(self):
        ''' for overriding '''
        custombox = wx.BoxSizer(wx.HORIZONTAL)
        self.text = wx.TextCtrl(self.mainpanel,NormalNote.ID_TEXT,pos=(0,0),style=wx.TE_MULTILINE,name="text")
        self.text.SetBackgroundColour(COLOR_240)

        custombox.Add(self.text,1,wx.EXPAND,1)
        self.mainpanel.SetSizer(custombox)
        self.Layout()

    def initData(self):
        '''memo로부터 넘어온 page.source를 이용해 실제 serialize된 데이터를
           parsing 한다'''
        if self.memo.page:          #page가 없으면 새 메모로 간주, 시리얼라이즈 하지 않음
            self.body = self.GetBodyFromSource(self.memo.page.source)
            self.SetBody(self.body)


    def SetChangeState(self):
        self.Bind(wx.EVT_TEXT,self.OnChange,id=NormalNote.ID_TEXT)
    
    def OnChange(self,evt):
        self.SetStatusModified()
        self.StartTimer()
        print "mmm"

    def GetBodyFromSource(self,source):
        ''' source값을 변경하여 현재 body를 채운다
            <p>(.*?)</p>로 감싼부분을 (.*?)\n으로 바꿔준다  '''
        body = Note.re_get_body.findall(source)[0]
        re_replace1 = re.compile("<p>(.*?)</p>",re.M|re.I|re.U|re.S)
        body2 = re_replace1.sub('\g<1>\n',body)
#        print "changed body ::::::::%s" % body2

        return body2

    def SerializeBody(self):
        rval = ""
        str = self.GetBody()
        arr = str.split('\n')
        for str2 in str.split('\n'):
            rval += "<p>" + str2 + "</p>"

        body = "<div id=\"body\">" + rval +  "</div>"
        return body


    def SetBody(self,str):
        self.text.SetValue(str)
    
    def GetBody(self):
        return self.text.GetValue()



if __name__ == "__main__":
    app = wx.App()
    NoteTaskBar()
    NormalNote(None,-1,'Note')
    app.MainLoop()

