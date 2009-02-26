import wx

class MyTaskBarIcon(wx.TaskBarIcon):
    TBMENU_BLACKLIST = wx.NewId()
    TBMENU_WHITELIST = wx.NewId()
   
    def __init__(self, frame = None):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
#        icon = wx.Icon('privosquid.ico', wx.BITMAP_TYPE_ICO)
        icon = wx.Icon('nicotine.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon, "Privosquid")
        self.SetIcon(icon, "Privosquid")
        self.SetIcon(icon, "Privosquid")
        self.SetIcon(icon, "Privosquid")
        self.SetIcon(icon, "Privosquid")
        self.SetIcon(icon, "Privosquid")
        self.Bind(wx.EVT_MENU, self.OnBLACKLIST, id = self.TBMENU_BLACKLIST)
        self.Bind(wx.EVT_MENU, self.OnWHITELIST, id = self.TBMENU_WHITELIST)
        self.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.CreateMenu)
        self.menu = wx.Menu()
        self.menu.AppendCheckItem(self.TBMENU_BLACKLIST, "Liste Noire")
        self.menu.AppendSeparator()
        self.menu.AppendCheckItem(self.TBMENU_WHITELIST, "Liste Blanche")
        self.menu.AppendSeparator()
       
    def CreateMenu(self, event):
        self.PopupMenu(self.menu)
       
    def OnBLACKLIST(self, event):
        if not self.menu.IsChecked(self.TBMENU_BLACKLIST):
            self.menu.Check(self.TBMENU_BLACKLIST, True)
            self.menu.Check(self.TBMENU_WHITELIST, False)
       
    def OnWHITELIST(self, event):
        if not self.menu.IsChecked(self.TBMENU_WHITELIST):
            self.menu.Check(self.TBMENU_WHITELIST, True)
            self.menu.Check(self.TBMENU_BLACKLIST, False)
       
class MaFenetre(wx.Frame):
    MNU_1 = wx.NewId()
    MNU_2 = wx.NewId()
    def __init__(self, titre = "Sans titre"):
        wx.Frame.__init__(self, None,  -1, title = titre, size = wx.Size(500, 300))
        self.menu = wx.Menu()
        self.menu.Append(self.MNU_1, "Ajouter la TaskBar")
        self.menu.AppendSeparator()
        self.menu.Append(self.MNU_2, "Supprimer la TaskBar")
        self.task = False
#        self.taskBar = None
        self.taskBar = MyTaskBarIcon()
       
        wx.EVT_RIGHT_UP(self, self.AfficheMenu)
        wx.EVT_MENU(self, self.MNU_1, self.ClickMenu)
        wx.EVT_MENU(self, self.MNU_2, self.ClickMenu)
       
    def  ClickMenu(self, event):
        choix = event.GetId()
        if choix == self.MNU_1 :
            if not self.task :
                self.taskBar = MyTaskBarIcon()
                self.task = True
        else:
            if self.task :
                self.taskBar.Destroy()
                self.taskBar = None
                self.task = False
               
    def AfficheMenu(self, event):
        pos = event.GetPosition()
        self.PopupMenu(self.menu, pos)
       
class MonApp(wx.App):
    def OnInit(self):
        fen = MaFenetre("Essai")
        fen.Show(True)
        self.SetTopWindow(fen)
        return True
       
app = MonApp()
app.MainLoop() 
