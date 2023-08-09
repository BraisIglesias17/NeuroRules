import wx
import pandas as pd
from ..respuestas import Response,Status

class IOManage():
    
    @staticmethod
    def LoadFile(self,event):
        # otherwise ask the user what new file to open
        with wx.FileDialog(self, "Open file", wildcard="(*.csv)|*.csv|(*.xlsx)|*.xlsx",
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return Response(data=None,status=Status.CANCEL)# the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'r') as file:
                    return IOManage.load_file(self,file)
            except IOError:
                wx.LogError("Cannot open file '%s'.")
    
    @staticmethod
    def load_file(self,file):
        
        if str(file.name).endswith(".csv"):
            
            data = pd.read_csv(file)
        elif str(file.name).endswith(".xlsx"):
            
            data = pd.read_excel(file.name)
            
        else:
            df=None
        
        df = pd.DataFrame(data)
        return df
        
    @staticmethod
    def OnSaveAs(self, event,data,message,wildcard):
        with wx.FileDialog(self, message, wildcard=wildcard,
                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  Response(data="",status=Status.CANCEL)# the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            toret=Response()
            try:
                pathname=str(pathname).replace("\\","/")
                if str(pathname).endswith(".xlsx"):
                    
                    data.to_csv(pathname)
                elif str(pathname).endswith(".csv"):
                    
                    print(type(data))
                    data.to_excel(pathname)
                elif str(pathname).endswith(".txt"):
                    with open(pathname, 'w') as file:
                        file.write(data)    
                    
                toret=Response(data=pathname,status=Status.OK)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)
                toret=Response(data=None,status=Status.IO_ERROR)
            except Exception as exc:
                print(exc)
            finally:
                return toret

