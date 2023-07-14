import wx
import pandas as pd

class IOManage():
    
    @staticmethod
    def LoadFile(self,event):
        # otherwise ask the user what new file to open
        with wx.FileDialog(self, "Open CSV file", wildcard="CSV files (*.csv)|*.csv",
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'r') as file:
                    return IOManage.load_file(self,file)
            except IOError:
                wx.LogError("Cannot open file '%s'.")
    
    @staticmethod
    def load_file(self,file):
        data = pd.read_csv(file)
        df = pd.DataFrame(data)
        return df
        
    @staticmethod
    def OnSaveAs(self, event,data):
        with wx.FileDialog(self, "Save XYZ file", wildcard=".txt files (*.txt)|*.txt",
                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'w') as file:
                    file.write(data)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)

