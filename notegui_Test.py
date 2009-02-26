import unittest
import notegui
import wx

class NoteGUITestCase(unittest.TestCase):
    def setUp(self):
        self.app = wx.App()
        self.taskbar = notegui.NoteTaskBar()

    def test_init_taskbar(self):
        self.assertTrue(isinstance(self.taskbar,notegui.NoteTaskBar))



if __name__ == '__main__':
    loader = unittest.defaultTestLoader
    loader.testMethodPrefix = 'test'
    unittest.main(testLoader = loader)



