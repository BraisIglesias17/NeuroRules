""" Module for implementing data file saving methods"""
from abc import ABC, abstractmethod
import pandas as pd

class FileSaver(ABC):
    """
        Template class for saving an abstract file
    """
    def save(self, filename, content,index=False):
        """
            Method that will be used to save the concrete file
            Args:
                - filename: name of the file to store
                - content: content of the file to store
                - index: if its a csv or xls index indicates if the index is include in th writing
        """
        self._save(filename,content,index)
    @abstractmethod
    def _save(self,filename,content,index):
        """
            Method to be overwrite for specific class with each method required
        """
class DataSetSaver(FileSaver):
    """
        General class for saving an data files
    """
    def save(self,filename,content,index=False):
        """
            Method that will be used to save the concrete file
            Args:
                - filename: name of the file to store
                - content: content of the file to store
                - index: if its a csv or xls index indicates if the index is include in th writing
        """
        if not isinstance(content,pd.DataFrame):
            raise ValueError("Must be an pandas dataframe") 
        self._save(filename,content,index)
    @abstractmethod
    def _save(self,filename,content,index):
        pass
class CSVFileSaver(DataSetSaver):
    """
        Class for saving CSV files
    """
    def _save(self, filename, content,index=False):
        """
            Method that will be used to save the concrete file
            Args:
                - filename: name of the file to store
                - content: content of the file to store
                - index: if its a csv or xls index indicates if the index is include in th writing
        """
        content.to_csv(filename,index=index)
class XLSFileSaver(DataSetSaver):
    """
        Class for saving XLS files
    """
    def _save(self, filename, content,index=False):
        """
            Method that will be used to save the concrete file
            Args:
                - filename: name of the file to store
                - content: content of the file to store
                - index: if its a csv or xls index indicates if the index is include in th writing
        """
        content.to_excel(filename,index=index)
class TextFileSaver(FileSaver):
    """
        Class for saving TXT files
    """
    def _save(self, filename, content,index=False):
        """
            Method that will be used to save the concrete file
            Args:
                - filename: name of the file to store
                - content: content of the file to store
                - index: if its a csv or xls index indicates if the index is include in th writing
        """
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content) 
class Saver():
    """
        Class for use as saver and abstract the concrete file
    """
    def __init__(self,path,content,index=False):
        self.saver=None
        self.path=path
        self.content=content
        self.index=index
        pathname=str(path).replace("\\","/").lower()
        if pathname.endswith(".xlsx"):
            self.saver=XLSFileSaver()
        elif pathname.endswith(".csv"):
            self.saver=CSVFileSaver()
        elif pathname.endswith(".txt"):
            self.saver=TextFileSaver()
        else:
            raise ValueError("Invalid file type")
    def save(self):
        """
        Save content to file
        """
        self.saver.save(self.path,self.content,self.index)
