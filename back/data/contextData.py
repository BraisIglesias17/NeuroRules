import pandas as pd
import numpy as np
from ..validation.validation import Validator
from .process import substitute_outliers,susbstitute_missing,remove_missing,remove_outliers,count_outliers,Transformer
from ..statistic.statistic import StatisticTest
import copy
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

    def __init__(self, dataFrame=pd.DataFrame()):    
        

        ## ADD ASSERTIONS

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
        
        self.identifier_cols=[]


        self.data_cleanse={} # 'lubricant':{'delete_missing':0,'substitute_missing':'Mean','delete_outliers':0,'substitute_outliers':'Mean'}
        self.data_preprocess={} # 'lubricant':{'preprocess':'normalization'}

        self.set_initial_cleanse()
        self.set_initial_preprocess()

        self.COV_THRESHOLD=1
        self.NORMALITY_THRESHOLD=0.05
        self.DIFFERENCE_THRESHOLD=0.05
    
    def set_initial_cleanse(self):
        for variable in self.data.columns:
            self.data_cleanse[variable]={'delete_missing':True,'substitute_missing':'None','delete_outliers':False,'highlight_outliers':False,'substitute_outliers':'None','upper_bound':0.75,'lower_bound':0.25}
    

    def set_initial_preprocess(self):
        self.data_preprocess['All']={'apply':True,'numerical':'None','categorical':'None'}   

        for variable in self.data.columns:
            self.data_preprocess[variable]={'transformation':'None','keep_original':True} 
    
    def update_set(self,df):
        self.__init__(df)
        
    def get_data(self):
        return self.data

    def get_values_inputs(self):
        return self.values[:,self.variables_index]
    
    def get_values_output(self,output):
        index=list(self.data.columns).index(output)
        return self.values[:,index]
    
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

    
    def get_types(self):
        return self.floatValues,self.integerValues,self.characterValues
    
    def _load_file(self,file):
        data = pd.read_csv(file)
        df = pd.DataFrame(data)
        return df
    
    def update_position(self,i,j,value):
        
        
        if i < self.data.shape[0] and j < self.data.shape[1]:
            
            col_name=self.data.columns[j]
            if self._validate_update(col_name,value):
                if col_name in self.floatValues:
                    value=np.float64(value)
                elif col_name in self.integerValues:
                    value=np.int64(value)

                #convertir al tipo que sea
                self.data.iloc[i,j]=value
                self.values[i,j]=value
                self.state=False
                
                return True
            else:
                raise ValueError("Tipo de dato no valido")
            
        elif i == self.data.shape[0]:
            print("nueva fila")
            # Nueva Fila
            values={}
            names=self.get_names()
            for var in names:
                if var==names[j]:
                    if self._validate_update(var,value):
                    
                        if var in self.integerValues:
                            values[var]=[np.int64(value)]
                        elif var in self.floatValues:
                            values[var]=[np.float64(value)]
                        else:
                            values[var]=[value]
                    else:
                        raise ValueError("Tipo de dato no valido")
                else:
                    if var in self.floatValues:
                        values[var]=[np.nan]
                    elif var in self.integerValues:
                        values[var]=[-1]
                    else:
                        values[var]=[None]
            
            temp=pd.DataFrame(values)
            self.data=pd.concat([self.data,temp],ignore_index=True)
            self.values=self.data.to_numpy()

        elif j == self.data.shape[1]:
            # Nueva columna
            print("NUEVA COLUMNA TO DO")


        return True
        

    def add_identifier_col(self,name):
        #check if name exists
        self.identifier_cols.append(name)
        

    def remove_identifier_col(self,name):
        #check if name exists
        self.identifier_cols.remove(name)
        
    
    def get_normal_variables(self):
        data=self.get_numeric_variables()
        normal_variables=[]

        for id in self.identifier_cols:
            if id in data.columns:
                data=data.drop(id,axis=1)
        
            
        for col in data:
            result=StatisticTest.shapiro_wilk((data[col]))
            if result.pvalue>self.NORMALITY_THRESHOLD:
                normal_variables.append(col)

        return normal_variables
        
    def get_covariance_pairs(self):
        valid_columns=self.data.select_dtypes(include=['number']).columns

        X=self.data[valid_columns].cov()
        
        directly_proportional=[]
        inverse_proportional=[]
    
        resting_cols=list(X.columns)

        for column in X.columns:
            resting_cols.remove(column)
            if not column in self.identifier_cols:
                for row in resting_cols:
                    if not row in self.identifier_cols:
                        value=(X.loc[row,column])
                        info={'variables':(str(row+','+column)),'covariance':value}
                        
                        if value < -self.COV_THRESHOLD:
                            inverse_proportional.append(info)
                        elif value > self.COV_THRESHOLD:
                            directly_proportional.append(info)
        
        return directly_proportional,inverse_proportional

    def get_differences_in_groups(self):
        numeric_cols=self.data.select_dtypes(include=['number']).columns
        nominal_cols=self.data.select_dtypes(include=['object']).columns
        toret=[]
        X=self.data[numeric_cols].columns
        group=self.data[nominal_cols]

        for nominal in group:
            if not nominal in self.identifier_cols:
                values=group[nominal].unique()

                i=0
                j=0
                for i in range(len(values)-1):
                    for j in range(i+1,len(values)):
                        groupA=values[i]
                        groupB=values[j]
                        
                        for variable in X:
                        
                            data=self.data[variable]
                            result=StatisticTest.shapiro_wilk(data)

                            query=str("`"+nominal+"`=='"+groupA+"'")
                            a=self.data.query(query)[variable]
                            query=str("`"+nominal+"`=='"+groupB+"'")
                            b=self.data.query(query)[variable]

                            if a.shape[0]==1 or b.shape[0]==1:
                                raise Exception("The test could not be perfomed because there is groups of "+nominal+" with one element only in "+variable)
                            
                            if result.pvalue>self.NORMALITY_THRESHOLD:
                                result=StatisticTest.ANOVA(a,b)
                                
                                if result.pvalue<self.DIFFERENCE_THRESHOLD:
                                    toret.append({'variable':variable,'groupby':nominal,'pair':str(groupA+" , "+groupB),'pvalue':result.pvalue})
                            else:
                                result=StatisticTest.wilcoxon(a,b)
                                
                                if result.pvalue<self.DIFFERENCE_THRESHOLD:
                                    toret.append({'variable':variable,'groupby':nominal,'pair':str(groupA+" , "+groupB),'pvalue':result.pvalue})
       
        return toret


    def get_position(self,row,col):
        if row < self.data.shape[0] and col < self.data.shape[1]:
            return self.data.iloc[row,col]

    def _validate_update(self,col_name,value):
        toret=True
        if col_name in self.floatValues:
            toret=Validator.check_float(float(value))         
        elif col_name in self.integerValues:
            toret=Validator.check_integer(int(value))            
        else:
            toret=Validator.check_string(value)
          
        
        return toret
    

    def print(self):
        print(f'filename: {self.pathname} \n Data: {self.data} \n State: {self.state}')

    def get_outliers(self):
        
        toret={}
        for variable in self.data:
            
            if self.data_cleanse[variable]['highlight_outliers']==True:
                outliers=list()
                
                lower_bound=self.data_cleanse[variable]['lower_bound']
                upper_bound=self.data_cleanse[variable]['upper_bound']
                i=0
                q1=self.data[variable].quantile(lower_bound)
                q3=self.data[variable].quantile(upper_bound)
                
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                for value in self.data[variable]:
                   
                    if count_outliers(value,lower_bound,upper_bound):
                        outliers.append(i)

                    i+=1
                index=list(self.data.columns).index(variable)
                toret[variable]={'index':index,'outliers':outliers}
                

        
        return toret

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
    
    def get_numeric_variables(self):
        return self.data.select_dtypes(include=["int16", "int32", "int64", "float16", "float32", "float64"])
    
    def get_data_summary(self):
        selection=self.get_numeric_variables()
        
        toret=selection.describe()
        
        return toret
    
    def get_variable_summary(self,variable,group=None):

    
        if not variable in self.data.columns:
            raise ValueError("Variable not found")
        if group!=None and not group in self.data.columns:
            raise ValueError("Group not found")
        if group!=None and not group in self.characterValues:
            raise ValueError("Group by variable must be categorical")
        
        if group==None:
            return self.data[variable].describe()
        else:
            return self.data.groupby(group)[variable].describe()

    
    def apply_preprocess(self,variable):
    
        settings=self.data_preprocess[variable]

        if variable!="All":    
            numerical=False
            
            transformation=settings['transformation']
            keep_original=settings['keep_original']
            
            if transformation!="None":
                index=list(self.data.columns).index(variable)
                original=self.values[:,index]

                if not variable in self.characterValues:
                    original=original.reshape(-1,1)
                    numerical=True
                
                transformer=Transformer(transformation,variable)
                transformed=transformer.fit(original)
                
                if transformation=="One hot encoding":
                    for col in transformed:
                        self.data_cleanse[col]={'delete_missing':True,'substitute_missing':'None','delete_outliers':False,'highlight_outliers':False,'substitute_outliers':'None','upper_bound':0.75,'lower_bound':0.25}
                        self.data_preprocess[col]={'transformation':'None','keep_original':True}

                    self.data=self.data.join(transformed)
                else:
                    if numerical:
                        transformed=transformed.reshape(1,-1)[0]
                        
                    if not keep_original:
                        self.data[variable]=transformed
                    else:
                        col_name=variable+"_processed"
                        i=1
                        aux=copy.deepcopy(col_name)
                        while col_name in self.data.columns:
                            col_name=aux+"_"+str(i)
                            i+=1
                        self.data=pd.concat([self.data,pd.DataFrame(columns=[col_name],data=transformed)],axis=1)
                        self.data_cleanse[col_name]={'delete_missing':True,'substitute_missing':'None','delete_outliers':False,'highlight_outliers':False,'substitute_outliers':'None','upper_bound':0.75,'lower_bound':0.25}
                        self.data_preprocess[col_name]={'transformation':'None','keep_original':True} 
                
                self.values=self.data.values
                            
        
    def apply_cleanse(self,variable):
        settings=self.data_cleanse[variable]

        n_rows_begin=self.data.shape[0]
        modified_rows=0
        
        if settings['delete_missing']:
            self.data=remove_missing(self.data,variable)
        else:
            if settings['substitute_missing']!="None":
                self.data=susbstitute_missing(self.data,variable,settings['substitute_missing'])

        if not variable in self.characterValues:
            if settings['delete_outliers']:
            
                result=remove_outliers(self.data,variable,settings['upper_bound'],settings['lower_bound'])
                self.data=result
                
            else:
                if settings['substitute_outliers']!="None":
                    
                    result=substitute_outliers(self.data,variable,settings['substitute_outliers'],settings['upper_bound'],settings['lower_bound'])
                    self.data=result[0]
                    modified_rows+=result[1]
    
        self.data=self.data.reset_index(drop=True)
        self.values=self.data.to_numpy()
        n_rows_end=self.data.shape[0]

        return (n_rows_begin-n_rows_end),modified_rows


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
            self.data_preprocess.pop(var)

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
    
    def get_preprocess(self):
        return self.data_cleanse
    
    def get_type_process_target(self):
        toret={}

        for variable in self.targets:
            if variable in self.characterValues:
                toret[variable]='classification'
            else:
                toret[variable]='regression'

        return toret

    def set_cleanse(self,variable,options):
        if variable in self.data.columns:
            self.data_cleanse[variable]=options
           
            return True
        else:
            raise ValueError("Not a valid variable")
        
    def set_preprocess(self,variable,options):
        if variable in self.data.columns or variable=="All":
            
            self.data_preprocess[variable]=options


            return True
        else:
            raise ValueError("Not a valid variable")

    def rename_col(self,new_name,old_name):
        
        if not old_name in list(self.data.columns):
            raise ValueError("Old name not found in current data")
            
            
        if not Validator.validate_name(new_name):
            raise ValueError("Invalid name format")
        
        change={old_name:new_name}
        self.data.rename(columns=change,inplace=True)
        
        return True
            
        
    """
    Añadir columna
    """
    """
    Añadir fila
    """
    

