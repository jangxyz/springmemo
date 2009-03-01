#-*-coding:utf8-*-
#!/usr/bin/python

import unittest
import notegui
import wx

class NoteGUITestCase(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.taskbar = notegui.NoteTaskBar()
        self.menuNameSet = ['새 노트','노트 목록','환경 설정','종료']


    def test_init_taskbar(self):
        self.assertTrue(isinstance(self.taskbar,notegui.NoteTaskBar))

    def test_menu_names(self):

        for item in self.taskbar.menu.GetMenuItems():
            print item.GetLabel()
#            self.assertTrue(item.GetLabel() in self.menuNameSet)


    def test_menu_new(self):
        menu_new = None
        for item in self.taskbar.menu.GetMenuItems():
            if item.GetLabel() == unicode("새 노트",'utf-8'):
                menu_new = item
        print menu_new
        self.assertTrue(menu_new)
        event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED,menu_new.GetId())
        self.taskbar.menu.GetEventHandler().ProcessEvent(event)

### 이벤트가 완료된 상황에서 뭔가 처리해줘야 함 


    def test_menu_list(self):
        menu_list = None
        for item in self.taskbar.menu.GetMenuItems():
            if item.GetLabel() == unicode("노트 목록",'utf-8'):
                menu_list = item
        print menu_list
        self.assertTrue(menu_list)
        event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED,menu_list.GetId())
        self.taskbar.menu.GetEventHandler().ProcessEvent(event)

    def test_menu_config(self):
        menu_config = None
        for item in self.taskbar.menu.GetMenuItems():
            if item.GetLabel() == unicode("환경 설정",'utf-8'):
                menu_config = item
        print menu_config
        self.assertTrue(menu_config)
        event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED,menu_config.GetId())
        self.taskbar.menu.GetEventHandler().ProcessEvent(event)

    def test_menu_quit(self):
        menu_quit = None
        for item in self.taskbar.menu.GetMenuItems():
            if item.GetLabel() == unicode("종료",'utf-8'):
                menu_quit = item
        print menu_quit
        self.assertTrue(menu_quit)
        event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED,menu_quit.GetId())
        self.taskbar.menu.GetEventHandler().ProcessEvent(event)



if __name__ == '__main__':
    loader = unittest.defaultTestLoader
    loader.testMethodPrefix = 'test'
    unittest.main(testLoader = loader)



