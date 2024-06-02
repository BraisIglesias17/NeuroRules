import pandas as pd
import numpy as np
import statistics as stat
from sklearn.preprocessing import LabelEncoder,OneHotEncoder,QuantileTransformer,StandardScaler,RobustScaler,Normalizer,MinMaxScaler
from numpy.typing import ArrayLike
from pandas import DataFrame
from typing import Union

Number=Union[int,float]

def remove_outliers(dataframe: DataFrame,variable: str,upper_bound:Number,lower_bound:Number):
    indexes=[]
    if dataframe[variable].dtype != "object":
        q1 = dataframe[variable].quantile(lower_bound)
        q3 = dataframe[variable].quantile(upper_bound)
        
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        #toret = dataframe[(dataframe[variable] >= lower_bound) & (dataframe[variable] <= upper_bound)]
        indexes=dataframe.index[((dataframe[variable] < lower_bound) | (dataframe[variable] > upper_bound))].tolist()
    else:
        toret=dataframe

    return indexes


def remove_missing(dataframe: DataFrame,variable: str):
    return dataframe.dropna(subset=[variable])

def substitute_outliers(dataframe: DataFrame,variable: str,method: ['Mean','Median','Adjust Closer'],upper_bound: Number,lower_bound: Number):
    
    if dataframe[variable].dtype != "object":
        higher=0.0
        lower=0.0

        q1 = dataframe[variable].quantile(lower_bound)
        q3 = dataframe[variable].quantile(upper_bound)
        
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        #lower_bound=q1
        #upper_bound=q3
        
        if method=="Mean":
            higher=np.mean(dataframe[variable])
            lower=higher
        elif method=="Median":
            higher=np.median(dataframe[variable])
            lower=higher
        elif method=="Adjust closer":
            higher=q1
            lower=q3
            
        count=np.sum(dataframe[variable].apply(count_outliers, args=(lower_bound, upper_bound)))
        dataframe[variable] = dataframe[variable].apply(replace_outliers, args=(lower_bound, upper_bound,higher,lower))
        
        #sum=dataframe.apply(lambda x: x[variable] > upper_bound or x[variable] < lower_bound).sum()

    return dataframe,count

def count_outliers(x: ArrayLike, lower_bound: Number, upper_bound: Number):
    if x < lower_bound:
        return True
    elif x > upper_bound:
        return True
    return False

def replace_outliers(x: ArrayLike, lower_bound: Number, upper_bound: Number, higher: Number,lower: Number):
    
    if x < lower_bound:
        return lower
    elif x > upper_bound:
        
        return higher
    
    return x

def susbstitute_missing(dataframe: DataFrame,variable: str,method: str):
    value=None
    if dataframe[variable].dtype != "object":
        if method == "Mean":
            value=np.mean(dataframe[variable])
        elif method=="Median":
            value=np.median(dataframe[variable])   
    else:
        value=stat.mode(dataframe[variable])
    dataframe[variable] = dataframe[variable].fillna(value)

    return dataframe



class Transformer():

    def __init__(self,name: str,variable_name: str):
        
        self.operation=None
        self.name=name
        self.x=None
        self.variable_name=variable_name
        #Creo el objeto adecuado
        if name == "Normalization (MinMax)":
            self.operation=MinMaxScaler()
        elif name == "Label encoding":
            self.operation=LabelEncoder()
        elif name == "One hot encoding":
            self.operation=OneHotEncoder()
        elif name == "Quantile Scaler":
            self.operation=QuantileTransformer()
        elif name == "Robust Scaler":
            self.operation=RobustScaler()
        elif name == "Standard Scaler":
            self.operation=StandardScaler()

    def fit(self,x: ArrayLike):
        self.x=x
        if self.name=="One hot encoding":
            x=x.reshape(-1,1)

        result=self.operation.fit_transform(x)
        
        if self.name=="One hot encoding":
            result=result.toarray()
            names=[]
            for name in np.unique(self.x):
                names.append(self.variable_name+"_"+str(name))
            result=pd.DataFrame(columns=names,data=result)
                    
        return result 
    
    def transform(self,x: ArrayLike):
        if self.name=="Label encoding":
            x=np.array([x])
        else:
            x=x.reshape(1,-1)
        result=self.operation.transform(x)    
        return result



