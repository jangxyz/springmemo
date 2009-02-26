#!/usr/lib/python
import wx

def OnTaskBarRight(event):
    app.ExitMainLoop()
#setup app
app= wx.PySimpleApp()

#setup icon object
icon = wx.Icon("./nicotine.ico", wx.BITMAP_TYPE_ICO)
#icon = wx.Icon("./nicotine.png", wx.BITMAP_TYPE_ICO)
#icon.SetWidth(50)
#icon.SetHeight(50)
print icon.GetWidth()
print icon.GetHeight()

#setup taskbar icon
tbicon = wx.TaskBarIcon()
tbicon.SetIcon(icon, "I am an Icon")

#add taskbar icon event
wx.EVT_TASKBAR_RIGHT_UP(tbicon, OnTaskBarRight)

if __name__ == "__main__":
    app.MainLoop()

