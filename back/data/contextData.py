import pandas as pd
import numpy as np
from ..validation.validation import Validator


class ContextData():
    """
    Class that represents de data to use in a workload

    Attributes:

    data: DataFrame
    variables: list of index of independent variables
    targets: list of index of target variables
    state: bool
    pahtname: string
    """

    def __init__(self, dataFrame=None):    
        self.pathname=""
        self.data=dataFrame
            
        self.state=True
        self.floatValues=[]
        self.characterValues=[]
        self.integerValues=[]
        self.get_types()

        self.values=self.data.to_numpy()

        self.variables=[]
        self.targets=[]
        self.variables_index=[]
        self.targets_index=[]
    
    def update_set(self,df):
        self.__init__(df)
        
    def get_data(self):
        return self.data
    def get_types(self):
        '''
        Check  the type of the variables saved on Dataframe: int, float or string
        '''
        colsDataframe = self.data.columns

        del self.floatValues[:]
        del self.characterValues[:]
        del self.integerValues[:]
        
        for col in colsDataframe:
            if self.data[col].dtypes == 'int64':
                self.integerValues.append(col)
            elif self.data[col].dtypes == 'float64':
                if Validator.check_integer(self.data[col]):
                    self.integerValues.append(col)
                else:
                    self.floatValues.append(col)
            else:
                self.characterValues.append(col)

    
    def _load_file(self,file):
        data = pd.read_csv(file)
        df = pd.DataFrame(data)
        return df
    
    def update_position(self,i,j,value):
        if i < self.data.shape[0] and j < self.data.shape[1]:
            
            col_name=self.data.columns[j]
            if self._validate_update(col_name,value):
               
                self.data.iloc[i,j]=value
                self.values[i,j]=value
                self.state=False

                return True
            else:
                return False
        elif i == self.data.shape[0]:
            print("nueva fila")
            # Nueva Fila
            values={}
            i=0
            names=self.get_names()
            for var in names:
                if var==names[j]:
                    if self._validate_update(var,value):
                    
                        values[var]=[value]
                    else:
                        return False
                else:   
                    values[var]=[None]
            
            temp=pd.DataFrame(values)
            self.data=pd.concat([self.data,temp],ignore_index=True)
            self.values=self.data.to_numpy()
            print(self.data)

        elif j == self.data.shape[1]:
            # Nueva columna
            print("HOLA")

        return True
        
            
    def get_position(self,row,col):
        if row < self.data.shape[0] and col < self.data.shape[1]:
            return self.data.iloc[row,col]

    def _validate_update(self,col_name,value):
        toret=True
        if col_name in self.floatValues:
            toret=Validator.check_float(value)         
        elif col_name in self.integerValues:
            toret=Validator.check_integer(value)            
        else:
            toret=Validator.check_string(value)
          
        
        return toret
    def print(self):
        print(f'filename: {self.pathname} \n Data: {self.data} \n State: {self.state}')


    def get_shape(self):
        return self.data.shape
    
    def _check_bounds(self,fil=None,col=None):
        toret=True

        if not (fil == None) and fil > self.data.shape[0]:
            toret=False
        
        if not (col == None) and col > self.data.shape[1]:
            toret=False
        
        return toret

    def get_column(self,index):
        if self._check_bounds(col=index):
            return self.values[:,index]
        else:
            return None
        
    def get_names(self):
        return self.data.columns
    
    def get_row(self,index):
        if self._check_bounds(fil=index):
            return self.values[index,:]
        else:
            return None
        
    
    def set_variables(self,indexes):
        names=self.data.columns
        self.variables=names[indexes]
        self.variables_index=indexes
        if not self._check_consistency():
            self.variables=[]
            self.variables_index=[]

    def set_target(self,indexes):
        names=self.data.columns[indexes]
        self.targets=names
        self.targets_index=indexes

        if not self._check_consistency():
            self.targets=[]
            self.targets_index=[]

    def _check_consistency(self):
        toret=True
        for i in self.variables:
            if i in self.targets:
                toret=False
                break
        return toret
    
    def get_variables(self):
        return self.values[:,self.variables_index]
    
    def get_targets(self):
        return self.values[:,self.targets_index]
    

    def get_data_summary(self):
        toret=pd.DataFrame()

        toret=self.data.describe()
        
        return toret
    
        
    

