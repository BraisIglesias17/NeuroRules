import wx
from front.views.mainWindow import MainWindow
import sys

if getattr(sys, 'frozen', False):
    import pyi_splash

if __name__ == '__main__':

    print("---------------------------------- ")
    
    print("------- Starting NEURORULE ------- ")
    
    app = wx.App()
    
    frame = MainWindow(None, wx.ID_ANY, "")

    if getattr(sys, 'frozen', False):
        pyi_splash.close()
        
    app.MainLoop()

    print("Exiting ... ")
    print("---------------------------------- ")
    
    




