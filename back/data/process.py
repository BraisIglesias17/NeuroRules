import pandas as pd
import numpy as np
import statistics as stat


def remove_outliers(dataframe,variable,upper_bound,lower_bound):

    if dataframe[variable].dtype != "object":
        q1 = dataframe[variable].quantile(lower_bound)
        q3 = dataframe[variable].quantile(upper_bound)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        toret = dataframe[(dataframe[variable] >= lower_bound) & (dataframe[variable] <= upper_bound)]
    else:
        toret=dataframe

    return toret

def remove_missing(dataframe,variable):
    return dataframe.dropna(subset=[variable])

def substitute_outliers(dataframe,variable,method,upper_bound,lower_bound):
    
    if dataframe[variable].dtype != "object":
        higher=0.0
        lower=0.0

        q1 = dataframe[variable].quantile(lower_bound)
        q3 = dataframe[variable].quantile(upper_bound)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        if method=="Mean":
            higher=np.mean(dataframe[variable])
            lower=higher
        elif method=="Median":
            higher=np.median(dataframe[variable])
            lower=higher
        elif method=="Closer":
            higher=upper_bound
            lower=lower_bound
            
        dataframe[variable] = dataframe[variable].apply(replace_outliers, args=(lower_bound, upper_bound,higher,lower))

    return dataframe

def replace_outliers(x, lower_bound, upper_bound, higher,lower):
    
    if x < lower_bound:
        return lower
    elif x > upper_bound:
        return higher
    
    return x

def susbstitute_missing(dataframe,variable,method):
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
