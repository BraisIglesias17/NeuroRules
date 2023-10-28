import wx
from front.views.mainWindow import MainWindow


if __name__ == '__main__':

    print("---------------------------------- ")
    
    print("------- Starting NEURORULE ------- ")
    app = wx.App()
    
    frame = MainWindow(None, wx.ID_ANY, "")
    
    app.MainLoop()

    print("Exiting ... ")
    print("---------------------------------- ")
    
    




