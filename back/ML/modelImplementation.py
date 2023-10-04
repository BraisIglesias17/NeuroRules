from back.ML.model import ModelImplementation
import pandas as pd
import numpy as np
from sklearn.svm import SVC,SVR
from sklearn.ensemble import RandomForestClassifier

##DEFINIR TODOS LOS MODELOS QUE SE QUIERAN 

class SVMModel(ModelImplementation):
    def __init__(self,parameters=None):
        self.parameters=parameters
        self.model=SVC()

class SVRModel(ModelImplementation):
    def __init__(self,parameters=None):
        self.parameters=parameters
        self.model=SVR()
    
class RandomForest(ModelImplementation):

    def __init__(self,parameters=None):
        self.parameters=parameters
        self.model=RandomForestClassifier()


