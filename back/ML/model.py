from abc import ABC, abstractmethod
import pickle
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor,RandomForestClassifier
from sklearn.model_selection import cross_val_score,GridSearchCV,KFold
from sklearn.neural_network import MLPRegressor,MLPClassifier
from sklearn.metrics import r2_score,mean_squared_error,f1_score,accuracy_score,precision_recall_curve,auc
import numpy as np
from .neurofuzzy import NeuroFuzzy
from itertools import combinations

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
                                    'copy_X': [True, False], 
                                }
            
        }
    

        

class ModelImplementation(Model):
    
    def __init__(self,model,filename=None,params=None):
        
        print(model)
        self.model=None
        self.modelname=model
        self.estimator_type=None
        self.folds=None
        self.training_scores=None
        self.grid_search=False
        self.cv=False

        self.rule_generator=False

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

        elif model=="Neurofuzzy":
            self.estimator_type="regressor"
            self.rule_generator=True
            self.submodels={}

        else:
            raise ValueError("Not supported model")
        
        
        if(not filename == None):
             self.model=pickle.load(open(filename, 'rb'))
             
    def train(self,input,target,cv=False,subsets=10,gridSearch=False,names_input=None,name_output=None,types=None):
        if self.rule_generator:
            self._fit_rule_generating(input,target,names_input=names_input,name_output=name_output,types=types)
        else:
            self._fit_prediction_model(input,target,cv=cv,subsets=subsets,gridSearch=gridSearch)

    def _fit_rule_generating(self,input,target,names_input,name_output,types):
        print("Fitting neurofuzzy system")
        r2=-100
        combs=names_input+list(combinations(names_input,2))
        
        n_membership_input=2
        n_membership_output=2
        name="submodel_"
        i=1
        for combination in combs:
            name_=name+str(i)
            indexes=[]
            names=[]
            
            
            if isinstance(combination,str):
                names.append(combination)
                indexes=names_input.index(combination)
            else:
                for element in combination:
                    indexes.append(names_input.index(element))
                    names.append(element)
            
            
            X=input[:,indexes]    
            
            if len(names)==1:
                X=X.reshape(-1,1)

            self.model=NeuroFuzzy(input=X,output=target,types=types,n_membership_input=n_membership_input,n_membership_output=n_membership_output,output_name=name_output,input_names=names)
            
            self.model.fit()
            
            scores=self.get_score(X=X,y_true=target)
            bestmodel=False
            if scores['r2']>r2:
                bestmodel=True

            self.submodels[name_]={'model':self.model,'trainig_score':self.get_score(X=X,y_true=target),'best':bestmodel,'inputs':names}
            
            i+=1
            

    def _fit_prediction_model(self,input,target,cv=False,subsets=10,gridSearch=False):
        if gridSearch:
            self.grid_search=gridSearch
            grid=ParamsMapper.model_params()
            scorer=""
            if self.estimator_type=="regressor":
                scorer="r2"
            else:
                scorer="accuracy"
                
            crf=GridSearchCV(self.model,param_grid=grid[self.modelname],cv=subsets,scoring=scorer)
            
            crf.fit(input,target)

            self.training_scores={scorer:crf.best_score_}
            self.model=crf.best_estimator_
        elif cv:
            self.cv=True
            kf = KFold(n_splits=subsets, shuffle=True, random_state=42)
            self.folds=kf
            scorer=""
            if self.estimator_type=="regressor":
                scorer="r2"
            else:
                scorer="accuracy"
            scores = cross_val_score(self.model,input,target, cv=kf,scoring=scorer)

            self.training_scores={'average_'+scorer:np.mean(scores),'folds_'+scorer:scores}

            print(self.training_scores)
            self.model.fit(input,target)
        else:
            self.model.fit(input,target)
            self.training_scores=self.get_score(input,target)


    def SRM(self,X_test,y_test):
        print("IMPLEMENTACION DE STRUCTURAL RISK MINIMIZATION")
        
    def predict(self,input):
        return self.model.predict(input)

    def get_params(self):
        return {'params':self.model.get_params(),'grid_search':self.grid_search}
    
    def set_params(self, dict):
        self.model.set_params(dict)
        
    def get_info(self):
        print(self.model)

    def get_score(self,X,y_true):
        tmp={}
        y_pred=self.predict(X)
        
        if self.estimator_type=="regressor": 
            tmp['r2']=r2_score(y_pred=y_pred,y_true=y_true)
            
            tmp['mse']=mean_squared_error(y_pred=y_pred,y_true=y_true)
            
            tmp['rmse']=np.sqrt(tmp['mse'])
            
        elif self.estimator_type=="classifier":
                        
            labels=np.unique(y_pred)
            n_class=len(labels)

            average="binary"
            if n_class>2:
                average="micro"
            tmp['accuracy']=accuracy_score(y_pred=y_pred,y_true=y_true)
            tmp['f1']=f1_score(y_pred=y_pred,y_true=y_true,labels=labels,average=average,pos_label=labels[0])
            #tmp['precision']=precision_recall_curve(y_test,y_pred)
            #tmp['auc']=auc(y_pred,y_test)
        return tmp

    def report(self,X,y_true):
                
        return {'test_validation':self.get_score(X,y_true),'training_validation':self.training_scores}

    def save(self, filename):
        try:
            pickle.dump(self.model, open(filename, 'wb'))
            return True
        except Exception as exc:
            return False
        

        
