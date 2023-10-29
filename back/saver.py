from abc import ABC, abstractmethod
import pandas as pd
class FileSaver(ABC):
   
    def save(self, filename, content):
        self._save(filename,content)
    
    @abstractmethod
    def _save(self,filename,content):
        pass

class DataSetSaver(FileSaver):

    def save(self,filename,content,index):
         if not isinstance(content,pd.DataFrame):
            raise ValueError("Must be an pandas dataframe") 
         else:
             self._save(filename,content,index)
    @abstractmethod
    def _save(self,filename,content,index):
        pass

class CSVFileSaver(DataSetSaver):
    def _save(self, filename, content,index):
        content.to_csv(filename,index=index)

class XLSFileSaver(DataSetSaver):
    def _save(self, filename, content,index):
        content.to_excel(filename,index=index)
        
class TextFileSaver(FileSaver):
    def _save(self, filename, content,index):
        with open(filename, 'w') as file:
                file.write(content) 


class Saver():
    def __init__(self,path,content,index=False):
        self.saver=None
        self.path=path
        self.content=content
        self.index=index

        pathname=str(path).replace("\\","/")
        if str(pathname).endswith(".xlsx"):
            self.saver=XLSFileSaver()
        elif str(pathname).endswith(".csv"):
            self.saver=CSVFileSaver()
        elif str(pathname).endswith(".txt"):
            self.saver=TextFileSaver()
        else:
            raise ValueError("Invalid file type")
    
    def save(self):
        self.saver.save(self.path,self.content,self.index)
            