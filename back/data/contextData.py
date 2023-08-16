import pandas as pd
import numpy as np
from ..validation.validation import Validator
from .process import substitute_outliers,susbstitute_missing,remove_missing,remove_outliers

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
        self._get_types()

        self.values=self.data.to_numpy()

        self.variables=[]
        self.targets=[]
        self.variables_index=[]
        self.targets_index=[]

        self.data_cleanse={} # 'lubricant':{'delete_missing':0,'substitute_missing':'Mean','delete_outliers':0,'substitute_outliers':'Mean'}
        self.data_preprocess={} # 'lubricant':{'preprocess':'normalization'}

        self.set_initial_cleanse()
    
    def set_initial_cleanse(self):
        for variable in self.data.columns:
            self.data_cleanse[variable]={'delete_missing':True,'substitute_missing':'None','delete_outliers':False,'highlight_outliers':False,'substitute_outliers':'None'}
    
        
    def update_set(self,df):
        self.__init__(df)
        
    def get_data(self):
        return self.data
    def _get_types(self):
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
    
    
    def apply_cleanse(self,variable):
        settings=self.data_cleanse[variable]

        n_rows_begin=self.data.shape[0]

        if settings['delete_missing']:
            self.data=remove_missing(self.data,variable)
        else:
            if settings['substitute_missing']!="None":
                self.data=susbstitute_missing(self.data,variable,settings['substitute_missing'])

        if settings['delete_outliers']:
            self.data=remove_outliers(self.data,variable,0.75,0.25)
        else:
            if settings['substitute_outliers']!="None":
                
                self.data=substitute_outliers(self.data,variable,settings['substitute_outliers'],0.75,0.25)
                
        
        

        self.data=self.data.reset_index(drop=True)
        self.values=self.data.to_numpy()
        n_rows_end=self.data.shape[0]

        return (n_rows_begin-n_rows_end)


    def delete_row(self,rows):
       
        rows=self._list_validation(rows,self.data.shape[0],0)
                
        self.data=self.data.drop(rows,axis=0)
        self.data=self.data.reset_index(drop=True)
        self.values=self.data.to_numpy()
    
            
        return True
    
    def _list_validation(self,list,upper_bound,lower_bound):
        toDel=[]
        
        for row in list:   
            if not (upper_bound>row and row >= lower_bound):
                toDel.append(row)
        for val in toDel:
            list.remove(val)
        
        return list
    
    def delete_column(self,cols):

        cols=self._list_validation(cols,self.data.shape[1],0)
        names=self.get_names()
        toDel=names[cols]
        
        self.data=self.data.drop(toDel,axis=1)
        self.data=self.data.reset_index(drop=True)
        self.values=self.data.to_numpy()
        
        for var in toDel:
            self.data_cleanse.pop(var)

        for col in cols:
            if col in self.variables_index:
                index=self.varaibles_index.index(col)
                self.variables_index.pop(index)
                self.variables.pop(index)
                
            if col in self.targets_index:
                index=self.targets_index.index(col)
                self.targets_index.pop(index)
                self.targets_index.pop(index)

            self._get_types()

        
        return True

    def get_cleanse(self):
        return self.data_cleanse
    
    def set_cleanse(self,variable,options):
        if variable in self.data.columns:
            self.data_cleanse[variable]=options
           
            return True
        else:
            raise ValueError("Not a valid variable")
    

