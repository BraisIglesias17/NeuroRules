from abc import ABC, abstractmethod
import pickle
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor,RandomForestClassifier
from sklearn.model_selection import cross_val_score,GridSearchCV,KFold
from sklearn.neural_network import MLPRegressor,MLPClassifier

class Model(ABC):
    
    @staticmethod
    def GET_REGRESSION_LIST():
        return ["Linear Regression","Support Vector Machine","Random Forest Regressor","Multiple Layer Perceptron Regressor"]
    
    @staticmethod
    def GET_CLASSIFICATION_LIST():
        return ["Support Vector Machine","Random Forest","Multiple Layer Perceptron","K-Nearest Neighbours"]
    
    @abstractmethod
    def train(self,input,target):
        pass

    @abstractmethod
    def predict(self,input):
        pass 

    @abstractmethod
    def report(self):
        pass

    @abstractmethod
    def save(self,filename):
        pass

    @abstractmethod
    def set_params(self,dict):
        pass


class ParamsMapper():

    @staticmethod
    def model_params():

        return {

            'Linear Regression':{
                                    'fit_intercept': [True, False], 
                                    'normalize': [True, False],  
                                    'copy_X': [True, False], 
                                }
            
        }
    

        

class ModelImplementation(Model):
    
    def __init__(self,model,filename=None):

        self.model=None
        self.modelname=model
        self.estimator_type=None
        self.score_cv=None


        if model=="Linear Regression":
            self.model=LinearRegression()
            self.estimator_type="regressor"
        elif model=="Random Forest Regressor":
            self.model=RandomForestRegressor()
            self.estimator_type="regressor"
        elif model=="Multiple Layer Perceptron Regressor":
            self.model=MLPRegressor()
            self.estimator_type="regressor"

        elif model=="Random Forest":
            self.model=RandomForestClassifier()
            self.estimator_type="classifier"
        elif model=="Multiple Layer Perceptron":
            self.model=MLPClassifier()
            self.estimator_type="classifier"
        else:
            raise ValueError("Not supported model")
        
        
        if(not filename == None):
             self.model=pickle.load(open(filename, 'rb'))
             
    def train(self,input,target,cv=False,subsets=10,gridSearch=False):
        if gridSearch:
            grid=ParamsMapper.model_params()
            
            crf=GridSearchCV(self.model,param_grid=grid[self.modelname],cv=subsets)
            print(input)
            print(target)
            x,y=crf.fit(input,target)
            self.model=crf.best_estimator_
        elif cv:
            kf = KFold(n_splits=subsets, shuffle=True, random_state=42)
            scorer=""
            if self.estimator_type=="regressor":
                scorer="r2"
            else:
                scorer="accuracy"
            scores = cross_val_score(self.model,input,target, cv=kf)
            self.score_cv=scores

        else:
            self.model.fit(input,target)
  
    def predict(self,input):
        return self.model.predict(input)

    def set_params(self, dict):
        self.model.set_params(dict)
        
    def get_info(self):
        print(self.model)

    def report(self,X,y):
        return self.model.score(X,y)

    def save(self, filename):
        try:
            pickle.dump(self.model, open(filename, 'wb'))
            return True
        except Exception as exc:
            return False
        

        
