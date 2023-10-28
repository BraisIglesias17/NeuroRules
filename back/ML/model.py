from abc import ABC, abstractmethod
import pickle
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor,RandomForestClassifier
from sklearn.model_selection import cross_val_score,GridSearchCV,KFold
from sklearn.neural_network import MLPRegressor,MLPClassifier
from sklearn.metrics import r2_score,mean_squared_error,f1_score,accuracy_score,precision_recall_curve,auc
from sklearn import tree
import numpy as np
from .neurofuzzy import NeuroFuzzy
from .neuroclassifier import NeuroClassifier
from itertools import combinations
from scipy.stats import pearsonr



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
        
        
        self.model=None
        self.modelname=model
        self.estimator_type=None
        self.folds=None
        self.training_scores=None
        self.X_test=None
        self.y_test=None
        self.name_output=None
        self.names_input=None
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
        
        elif model=="DecisionTree":
            self.estimator_type="classifier"
            self.rule_generator=True
            self.submodels={}

        else:
            raise ValueError("Not supported model")
        
        if(not filename == None):
             self.model=pickle.load(open(filename, 'rb'))
             
    def train(self,input,target,cv=False,subsets=10,gridSearch=False,names_input=None,name_output=None,types=None,X_test=None,y_test=None):
        self.X_test=X_test
        self.y_test=y_test
        self.name_output=name_output
        self.names_input=names_input

        if self.rule_generator and self.estimator_type=="regressor":
            self._fit_rule_generating_regression(input,target,names_input=names_input,name_output=name_output,types=types)
        elif self.rule_generator and self.estimator_type=="classifier":
            self._fit_rule_generating_classifier(input,target,names_input,np.unique(target))
        else:
            self._fit_prediction_model(input,target,cv=cv,subsets=subsets,gridSearch=gridSearch)



    def _fit_rule_generating_classifier(self,input,target,input_names,class_names):
        
        self.model=NeuroClassifier(input_names,class_names)
        self.model.fit(X=input,y=target)
        
        scores=self.get_score(X=input,y=target)
        test_scores=self.get_score(self.X_test,self.y_test)
        self.submodels['all']={'model':self.model,'training_score':scores,'test_scores':test_scores,'best':self.model,'inputs':input_names}
        


    def _fit_rule_generating_regression(self,input,target,names_input,name_output,types):
        
        
        #filtrar por correlacion
        toDel=[]
        self.discarded={}
        for i in range(input.shape[1]):
            col=input[:,i]
            pvalue=pearsonr(col,target).pvalue
            
            if pvalue>0.5:
                toDel.append(i)
                self.discarded[names_input[i]]=pvalue
        
        #eliminar columnas y nombres
        tmp = [names_input[i] for i in range(len(names_input)) if i not in toDel]
        names_input=tmp

        tmp= np.delete(input, toDel, axis=1)
        input=tmp

       
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

           
            scores=self.get_score(X=X,y=target)

            test_scores=self.get_score(X,target)
            
            
            
            bestmodel=False
            if scores['r2']>r2:
                bestmodel=True

            if scores['r2']>0.5:
                self.submodels[name_]={'model':self.model,'training_score':scores,'test_score':test_scores,'best':bestmodel,'inputs':names}
                i+=1

        
        self._generate_ensemble_model(input.shape[0],target)

    def _submodels_pruning(self):
        print("delete worsts models")

    def get_enssemble_metrics(self):
        return self.ensembled_model_metrics
    
    def _generate_ensemble_model(self,input_size,y):
        n=len(self.submodels)
        if n!=0:
            inputs=np.zeros((input_size,n))
            i=0

            for submodel in self.submodels:  
                inputs[:,i]=(self.submodels[submodel]['model'].get_predictions_on_train().flatten())
                i+=1

            ensemble=LinearRegression()
            ensemble.fit(inputs,y)

            self.ensembled_model=ensemble
            self.ensembled_model_metrics=ensemble.score(inputs,y)
        else:
            self.ensembled_model=None
            self.ensembled_model_metrics=0.0

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
        
            self.model.fit(input,target)
        
            self.test_scores=self.get_score(self.X_test,self.y_test)

            self.training_scores={'average_'+scorer:np.mean(scores),'folds_'+scorer:scores}
            
        else:
            self.model.fit(input,target)
            self.training_scores=self.get_score(input,target)
            self.test_scores=self.get_score(self.X_test,self.y_test)


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

    def get_score(self,X,y):
        tmp={}
        y_pred=self.predict(X)
        
        if self.estimator_type=="regressor": 
            tmp['r2']=r2_score(y_pred=y_pred,y_true=y)
            
            min=np.min(y)
            max=np.max(y)
            tmp['mse']=mean_squared_error(y_pred=y_pred,y_true=y)/(max-min)
            
            tmp['rmse']=np.sqrt(tmp['mse'])
            
        elif self.estimator_type=="classifier":
                        
            labels=np.unique(y_pred)
            n_class=len(labels)

            average="binary"
            if n_class>2:
                average="micro"
            tmp['accuracy']=accuracy_score(y_pred=y_pred,y_true=y)
            tmp['f1']=f1_score(y_pred=y_pred,y_true=y,labels=labels,average=average,pos_label=labels[0])
            #tmp['precision']=precision_recall_curve(y_test,y_pred)
            #tmp['auc']=auc(y_pred,y_test)
        return tmp

    def report(self):
        return {'test_validation':self.test_scores,'training_validation':self.training_scores}

    def save(self, filename):
        try:
            pickle.dump(self.model, open(filename, 'wb'))
            return True
        except Exception as exc:
            return False
        
    def get_text_report(self):
        
        report=" ----- "+self.modelname+" ----- \n"
    
        report=report+"Inputs:"

        for name in self.names_input:
            report+=name
            if name!=self.names_input[-1]:
                report+=", "
        
        report+="\n"

        report+="Output: "+self.name_output+"\n\n"

        if self.modelname!="Neurofuzzy":

            report+="Training metrics:\n"
            
            report+=self._dict_to_text(self.training_scores,"=",0)

            report+="\n"
            report+="Testing metrics:\n"
          
            report+=self._dict_to_text(self.test_scores,"=",0)

            report+="\n"
            report+="Model params:\n"
            params=self.model.get_params()
            for param in params:
                report+=" - "+param+"= "+str(params[param])+"\n"

        else:
            report+="Discarded inputs (name(correlation p-value)):\n"
            
            for discarded in self.discarded:
                report+=" - "+discarded+" ("+str(np.round(self.discarded[discarded],3))+")"+"\n"

            report+="\n\n"
            report+="Submodels:\n"

            for submodel in self.submodels:
                report+=" - "+submodel+":\n"

                report+="\t Inputs: "
                for input in self.submodels[submodel]['inputs']:
                    report+=input+" "
                    #if input!=self.submodels[submodel]['inputs'][input][-1]:
                    #    report=report+", "
                report+="\n"

                report+="\t Training scores: \n"

                report+=self._dict_to_text(self.submodels[submodel]['training_score'],"=",2)

                report+="\t Test scores: \n"

                report+=self._dict_to_text(self.submodels[submodel]['test_score'],"=",2)

                report=report+"\t Rules: \n"

                rules=self.submodels[submodel]['model'].get_rules()
                for rule in rules:
                    report+="\t\t"+rule+"\n"

        return report
        

    def _dict_to_text(self,dict,sep,tabs):
        toret=""
        for elemn in dict:
            
            for i in range(tabs):
                toret+="\t"
            toret+=" - "+elemn+sep+str(dict[elemn])+"\n"
        
        return toret