"""Module for model implementation"""
import pickle
import copy
from abc import ABC, abstractmethod
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor,RandomForestClassifier
from sklearn.model_selection import cross_val_score,GridSearchCV,KFold
from sklearn.neural_network import MLPRegressor,MLPClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.svm import SVR,SVC
from sklearn.metrics import r2_score,mean_squared_error,f1_score,accuracy_score,precision_recall_curve,auc,recall_score,precision_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn import tree
import numpy as np
from .neurofuzzy import NeuroFuzzy
from .neuroclassifier import NeuroClassifier
from itertools import combinations
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import pandas as pd
from sklearn.model_selection import StratifiedKFold

class Model(ABC):
    
    @staticmethod
    def GET_REGRESSION_LIST():
        return ["Linear Regression","Support Vector Machine Regressor","Random Forest Regressor","Multiple Layer Perceptron Regressor"]
    
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
                    'Linear Regression': {
                        'fit_intercept': [True, False],
                        'normalize': [True, False],
                    },
                    'Random Forest Classifier': {
                        'n_estimators': [10, 50, 100],
                        'criterion': ['gini', 'entropy'],
                        'max_depth': [None, 10, 20],
                        'min_samples_split': [2, 5, 10],
                        'min_samples_leaf': [1, 2, 4],
                        'max_features': ['auto', 'sqrt', 'log2'],
                    },
                    'Random Forest Regressor': {
                        'n_estimators': [10, 50, 100],
                        'criterion': ['mse', 'mae'],
                        'max_depth': [None, 10, 20],
                        'min_samples_split': [2, 5, 10],
                        'min_samples_leaf': [1, 2, 4],
                        'max_features': ['auto', 'sqrt', 'log2'],
                    },
                    'MLP Classifier': {
                        'hidden_layer_sizes': [(50, 50), (100,)],
                        'activation': ['relu', 'logistic', 'tanh'],
                        'solver': ['sgd', 'adam'],
                        'alpha': [0.0001, 0.05],
                    },
                    'MLP Regressor': {
                        'hidden_layer_sizes': [(50, 50), (100,)],
                        'activation': ['relu', 'logistic', 'tanh'],
                        'solver': ['sgd', 'adam'],
                        'alpha': [0.0001, 0.05],
                    },
                    'Support Vector Machine': {
                        'C': [0.1, 1, 10],
                        'kernel': ['linear', 'rbf', 'poly'],
                        'gamma': ['scale', 'auto'],
                    },
                    'Support Vector Machine Regressor': {
                        'C': [0.1, 1, 10],
                        'kernel': ['linear', 'rbf', 'poly'],
                        'gamma': ['scale', 'auto'],
                    },
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

        elif model=="Support Vector Machine Regressor":
            self.model=SVR()
            self.estimator_type="regressor"

        elif model=="Support Vector Machine":
            self.model=SVC()
            self.estimator_type="classifier"

        elif model=="Random Forest":
            self.model=RandomForestClassifier()
            self.estimator_type="classifier"

        elif model=="Multiple Layer Perceptron":
            self.model=MLPClassifier()
            self.estimator_type="classifier"

        elif model=="K-Nearest Neighbours":
            self.model=KNeighborsClassifier()
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
        self.n_classes=len(class_names)
        self.class_names=class_names
        scores=self.get_score(X=input,y=target)
        test_scores=self.get_score(self.X_test,self.y_test)
        self.submodels['all']={'model':self.model,'training_score':scores,'test_score':test_scores,'best':self.model,'inputs':input_names}
        self.training_scores=scores
        self.test_scores=test_scores


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
        
        X_test=copy.deepcopy(self.X_test)
        X_test=np.delete(X_test,toDel,axis=1)
       
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
            X_test_tmp=X_test[:,indexes]

            if len(names)==1:
                X=X.reshape(-1,1)

            self.model=NeuroFuzzy(input=X,output=target,types=types,n_membership_input=n_membership_input,n_membership_output=n_membership_output,output_name=name_output,input_names=names)
            
            self.model.fit()

            scores=self.get_score(X=X,y=target)
            
            if len(X_test_tmp.shape)==1:
                X_test_tmp=X_test_tmp.reshape(-1,1)

            test_scores=self.get_score(X=X_test_tmp,y=self.y_test)
            
            bestmodel=False
            if scores['r2']>r2:
                bestmodel=True
            self.submodels[name_]={'model':self.model,'training_score':scores,'test_score':test_scores,'best':bestmodel,'inputs':names}            
            i+=1
        #submodel pruning
        self.submodels=self.SRM(self.submodels)
        self._generate_ensemble_model(input.shape[0],target)

    def SRM(self,submodels):
        print("---------------------------------------------")
        print("IMPLEMENTACION DE STRUCTURAL RISK MINIMIZATION")
        print(self.submodels)
        worth_submodels={}
        max_score=-np.inf
        #primer bucle para determinar la mejor medicion
        for submodel in submodels:
            average_metric=(0.7*submodels[submodel]['test_score']['r2']+0.3*submodels[submodel]['training_score']['r2'])/len(submodels[submodel]['inputs'])
            if average_metric>max_score:
                max_score=average_metric

        i=1
        #segundo bucle para quedarse unicamente con los modelos que no empeoran mucho al mejor
        for submodel in submodels:
            average_metric=(0.7*submodels[submodel]['test_score']['r2']+0.3*submodels[submodel]['training_score']['r2'])/len(submodels[submodel]['inputs'])
            if not average_metric<(0.8*max_score):
                worth_submodels['submodel_'+str(i)]=submodels[submodel]
                i+=1
        print("---------------------------------------------")
        return worth_submodels

    def _submodels_pruning(self):
        print("delete worsts models")

    def get_enssemble_metrics(self):
        return self.ensembled_model_metrics
    
    def cross_validation(self,n_folds,model):
        if n_folds>self.X_test.shape[0] or n_folds<0:
            raise ValueError("Invalid number of folds")

        cv_results={}
        kf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
        for fold, (train_index, test_index) in enumerate(kf.split(self.X_test, self.y_test)):
            X_train, X_test = self.X_test[train_index], self.X_test[test_index]
            y_train, y_test = self.y_test[train_index], self.y_test[test_index]

            model.fit(X_train,y_train)
            #self.get_score(X_test,y_test)
            #cv_results=self._calculate_average(cv_results,self.get_score(X_test,y_test))
        
        return cv_results

    def _calculate_average(self,results,new_results):
        toret={}
        if len(results)==0:
            toret=new_results
        else: 
            keys=list(results.keys())
            for key in keys:
                toret[key]=(results[key]+new_results[key])/2

        return toret

    def plot_model_results(self):
        if self.estimator_type=="classifier" and not self.rule_generator:
            y_pred = self.model.predict(self.X_test)

            cm = confusion_matrix(self.y_test, y_pred)

            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt="d", cmap=sns.color_palette("vlag", as_cmap=True), cbar=False,
                        xticklabels=self.class_names, yticklabels=self.class_names)
            plt.xlabel('Predicted Labels')
            plt.ylabel('True Labels')
            plt.title('Confusion Matrix')
            return plt

        elif self.estimator_type=="regressor" and not self.rule_generator:
            y_pred = self.model.predict(self.X_test)
            
            sns.scatterplot(data=pd.DataFrame({'Actual Values':self.y_test,'Predicted Values':y_pred}))
            
            plt.xlabel(self.name_output)
            
            plt.title("Model precision graph")
            return plt
        
    def _generate_ensemble_model(self,input_size,y):
        n=len(self.submodels)
        if n!=0:
            inputs=np.zeros((input_size,n))
            X_test=np.zeros((self.X_test.shape[0],n))
            i=0

            for submodel in self.submodels:  
                inputs[:,i]=(self.submodels[submodel]['model'].get_predictions_on_train().flatten())
                names=self.submodels[submodel]['inputs']
                indexes=[ self.names_input.index(elem) for elem in names]
                X_test[:,i]=(self.submodels[submodel]['model'].predict(self.X_test[:,indexes]))
                i+=1

            ensemble=LinearRegression()
            ensemble.fit(inputs,y)
            
            self.ensembled_model=ensemble
            #METRICAS CON VALIDACION TEST
            self.ensembled_model_metrics=ensemble.score(X_test,self.y_test)
            print(self.ensembled_model_metrics)
            #METRICAS CON VALIDACION TRAIN
            #self.ensembled_model_metrics=ensemble.score(inputs,y)
        else:
            self.ensembled_model=None
            self.ensembled_model_metrics=0.0

    def _fit_prediction_model(self,input,target,cv=False,subsets=10,gridSearch=False):
        scorer=""
        if self.estimator_type=="regressor":
            scorer="r2"
        else:
            self.class_names=np.unique(target)
            self.n_classes=len(self.class_names)
            self.class_names=np.unique(target)
            scorer="accuracy"
        if gridSearch:
            self.grid_search=gridSearch
            grid=ParamsMapper.model_params()

            crf=GridSearchCV(self.model,param_grid=grid[self.modelname],cv=subsets,scoring=scorer)
            crf.fit(input,target)
            self.training_scores={scorer:crf.best_score_}
            self.model=crf.best_estimator_
        elif cv:

            self.cv=True
            kf = KFold(n_splits=subsets, shuffle=True, random_state=42)
            self.folds=kf
            #print(f' CV RESULTS {self.cross_validation(subsets,self.model)}')
            scores = cross_val_score(self.model,input,target, cv=kf,scoring=scorer)
            self.model.fit(input,target)
            self.test_scores=self.get_score(self.X_test,self.y_test)
            self.training_scores={'average_'+scorer:np.mean(scores),'folds_'+scorer:scores}
        else:
            self.model.fit(input,target)
            self.training_scores=self.get_score(input,target)
            self.test_scores=self.get_score(self.X_test,self.y_test)
        
    def predict(self,input,submodel=None):
        if self.rule_generator and self.estimator_type=="regressor":
            model=self.submodels[submodel['submodel']]['model']
            return model.predict(input)
        else:
            return self.model.predict(input)

    def get_params(self):
        return {'params':self.model.get_params(),'grid_search':self.grid_search}
    
    def set_params(self, dict):
        self.model.set_params(dict)
        
    def get_info(self):
        print(self.model)

    def get_score(self,X,y):
        tmp={}
        y_pred=self.model.predict(X)
        if self.estimator_type=="regressor": 
            tmp['r2']=r2_score(y_pred=y_pred,y_true=y)
            min=np.min(y)
            max=np.max(y)
            tmp['mse']=mean_squared_error(y_pred=y_pred,y_true=y)/(max-min)
            tmp['rmse']=np.sqrt(tmp['mse'])
            
        elif self.estimator_type=="classifier":
            
            avg="binary"
            if self.n_classes>2:
                avg="weighted"
            tmp['accuracy']=accuracy_score(y_pred=y_pred,y_true=y)
            tmp['f1']=f1_score(y_pred=y_pred,y_true=y,labels=self.class_names,average=avg,pos_label=self.class_names[0])
            tmp['precision']=precision_score(y,y_pred,pos_label=self.class_names[0],average=avg)
            tmp['recall']=recall_score(y_pred,y,pos_label=self.class_names[0],average=avg)

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