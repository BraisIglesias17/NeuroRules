""" Module for managing the open file/dir dialog"""
import wx
import pandas as pd
from back.respuestas import Response,Status

class IOManage():
    """ Class that provides with static methods to obtain 
    file and folders from UI and to create frames"""
    @staticmethod
    def GetPath(window,message:str,wildcard:str,default_folder:str="",default_name:str=""):
        """
         Function to obtain a path to store a file
         Args:  
                - Window: parent window
                - message: message to display
                - wildcard: wildcard for the correspondant type of file
                - default_folder: default directory to be located 
                - default_name: defualt file name to store
        """
        with wx.FileDialog(window, message, wildcard=wildcard
                           ,defaultFile=default_name,defaultDir=default_folder,
                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return  Response(data="",status=Status.CANCEL)
            pathname = file_dialog.GetPath()
            return Response(data=pathname,status=Status.OK)
    @staticmethod 
    def get_path_folder(window,message:str):
        """
         Function to obtain a path to a folder
         Args:  
                - Window: parent window
                - message: message to display
        """
        with wx.DirDialog(window, message,
                        style=wx.DD_DIR_MUST_EXIST) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return  Response(data="",status=Status.CANCEL)
            pathname = file_dialog.GetPath()
            return Response(data=pathname,status=Status.OK) 
    @staticmethod
    def get_path_import(window,message:str,wildcard:str,default_name:str=""):
        """
         Function to obtain a path to store a file
         Args:  
                - Window: parent window
                - message: message to display
        """
        with wx.FileDialog(window, message, wildcard=wildcard,defaultFile=default_name,
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return  Response(data="",status=Status.CANCEL)
            
            pathname = file_dialog.GetPath()
            return Response(data=pathname,status=Status.OK)  
    @staticmethod
    def load_file(conf):
        """
         Function that returns a data frame formed from a filename path
         Args:  
                - conf: dictionary with the configuration of the 
                        file: name, separator character and decimal character.
        """
        pathname=conf['pathname']
        if str(pathname).endswith(".csv"):
            with open(pathname, 'r',encoding="utf-8") as file:
                data = pd.read_csv(file,sep=conf['sep'],decimal=conf['dec'])
                name=file.name
        elif str(pathname).endswith(".xlsx"):
            with open(pathname, 'r',encoding="utf-8") as file:
                data = pd.read_excel(file.name,decimal=conf['dec'])
                name=file.name
        else:
            df=None
        df = pd.DataFrame(data)
        return df,name
    