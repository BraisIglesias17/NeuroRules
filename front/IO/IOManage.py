import wx
import pandas as pd
from back.respuestas import Response,Status
from ..constants import WILCARD_TASK,WILDCARD_DATA_FILE
import platform

class IOManage():
    

    @staticmethod
    def GetPath(window,message,wildcard,defaultDir,defaultname=""):
    
        #defaultname=defaultname
        with wx.FileDialog(window, message, wildcard=wildcard,defaultFile=defaultname,defaultDir=str(defaultDir),
                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  Response(data="",status=Status.CANCEL)# the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            return Response(data=pathname,status=Status.OK)

    @staticmethod 
    def GetPathFolder(window,message):
        
        with wx.DirDialog(window, message,
                        style=wx.DD_DIR_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  Response(data="",status=Status.CANCEL)# the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            return Response(data=pathname,status=Status.OK) 
        
    @staticmethod
    def GetPathImport(window,message,wildcard,defaultname=""):
        with wx.FileDialog(window, message, wildcard=wildcard,defaultFile=defaultname,
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  Response(data="",status=Status.CANCEL)# the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()

            return Response(data=pathname,status=Status.OK)  
        


    @staticmethod
    def LoadFile(self,event):
        # otherwise ask the user what new file to open
        with wx.FileDialog(self, "Open file", wildcard=WILDCARD_DATA_FILE,
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return Response(data=None,status=Status.CANCEL)# the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            return Response(data=pathname,status=Status.OK)
            """
            
            try:
                with open(pathname, 'r') as file:
                    tmp=IOManage.load_file(file)
                    df=tmp[0]
                    filename=tmp[1]
                    return Response(data={'df':df,'filename':filename},status=Status.OK)
                
            except IOError:
                wx.LogError("Cannot open file '%s'.")
            """
    
    @staticmethod
    def load_file(conf):
        pathname=conf['pathname']
        if str(pathname).endswith(".csv"):
            with open(pathname, 'r') as file:
                data = pd.read_csv(file,sep=conf['sep'],decimal=conf['dec'])
                name=file.name

        elif str(pathname).endswith(".xlsx"):
            with open(pathname, 'r') as file:
                data = pd.read_excel(file.name,decimal=conf['dec'])
                name=file.name
            
        else:
            df=None
        
        df = pd.DataFrame(data)
        return df,name
        
    @staticmethod
    def OnSaveAs(window,message,wildcard,dir="",file=""):
        with wx.FileDialog(window, message, wildcard=wildcard,defaultDir=dir,defaultFile=file,
                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  Response(data="",status=Status.CANCEL)# the user changed their mind

            try:
                # save the current contents in the file
                pathname = fileDialog.GetPath()
                toret=Response(data=pathname,status=Status.OK)

            except Exception as exc:
                print(exc)
                toret=Response(data=None,status=Status.IO_ERROR)
            finally:
                return toret

