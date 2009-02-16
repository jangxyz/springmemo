import wx

class SimpleTextEditor(wx.Frame):
    #constructor
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Simple Text Editor", size=(400,300))
        panel = wx.Panel(self, -1)
        self.richText = wx.TextCtrl(panel, -1, size=(400,300), style=wx.TE_MULTILINE|wx.TE_RICH2)
        self.richText.SetInsertionPoint(0)
        self.CreateStatusBar()
        #make menu
        menu = wx.Menu()
        fopen = menu.Append(-1, "Open", "Selecting this item will open file")
        fsave = menu.Append(-1, "Save", "Selecting this item will save file")
        menu.AppendSeparator()
        exit = menu.Append(-1, "Exit", "Selecting this item will exit the program")
        self.Bind(wx.EVT_MENU, self.OnOpen, fopen)
        self.Bind(wx.EVT_MENU, self.OnSave, fsave)
        self.Bind(wx.EVT_MENU, self.OnExit, exit)
        #make menubar
        menuBar = wx.MenuBar()
        menuBar.Append(menu, "Menu")
        self.SetMenuBar(menuBar)
    
    #open menu    
    def OnOpen(self, event):
        try:
            f = open("./file.txt")
            try:
                self.richText.SetValue(f.read())
                wx.MessageBox("file opened.")
            finally:
                f.close()
        except IOError:
            pass
    
    #save menu    
    def OnSave(self, event):
        try:
            f = open("./file.txt", "a")
            try:
                f.write(self.richText.GetValue())
                wx.MessageBox("file saved.")
            finally:
                f.close()
        except IOError:
            pass
    
    #exit menu    
    def OnExit(self, event):
        self.Close()
        
if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = SimpleTextEditor()
    frame.Show()
    app.MainLoop()