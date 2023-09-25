
from .ML.model import ModelImplementation
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score,mean_squared_error,f1_score,accuracy_score,precision_recall_curve,auc

class Task():


    def __init__(self,name,data,outputs,validation):

        assert name!="" and name!=None

        assert data!=None

        assert outputs!=None

        assert validation!=None


        self.taskName=name
        self.contextData=data
        self.outputs=outputs
        self.validation=validation
        self.models={}
        self.results={}

        for variable in outputs:
            self.models[variable]=[]
            
            for model in self.outputs[variable]['model']:
                
                self.models[variable].append(ModelImplementation(model=model))


        indexes = list(range(self.contextData.values.shape[0])) 
        X=self.contextData.get_values_inputs()
        print(self.validation)
        train_index, test_index= train_test_split(indexes, test_size=self.validation['params']['test_size'], random_state=42, shuffle=True)

        self.train_index=train_index
        self.test_index=test_index

        self.X_train = X[train_index]
        self.X_test = X[test_index]

        self.saved=False
        self.executed=False
    
    @staticmethod
    def load(path):
        print(f"Loading task from {path}")

    def save(self):
        print("Saving task ...")

    def execute(self,callable,*args,**kwargs):
        
        i=0
        inc=100/len(self.models)

        print("Performing model training ...")
        for variable in self.models:
            y=self.contextData.get_values_output(variable)
            y_train=y[self.train_index]

    
            for model in self.models[variable]:
                #grid search?
                #test train split ?
                #cv ?
                
                model.train(self.X_train,y_train,self.validation['method']=="Cross Validation",self.validation['params']['subsets'],self.outputs[variable]['params'])
                
                callable(self._update_progressbar,args[0][0],int(i))           
                i+=inc

        print("Training finished")
                
            
    def _update_progressbar(self,progressbar,value):
        
        progressbar.Update(value,"Training in progress...")

    def get_report(self):
        print("Returning all results")

    def get_report(self,variable):
        toret={}
        models=self.models[variable]

        for model in models:

            tmp={}
            y=self.contextData.get_values_output(variable)
            y_test=y[self.test_index]
            y_pred=model.predict(self.X_test)

            if model.estimator_type=="regressor": 
                tmp['r2']=r2_score(y_pred=y_pred,y_true=y_test)
                tmp['mse']=mean_squared_error(y_pred=y_pred,y_true=y_test)
            elif model.estimator_type=="regressor":
                tmp['accuracy']=accuracy_score(y_pred=y_pred,y_true=y_test)
                tmp['f1']=f1_score(y_pred=y_pred,y_true=y_test)
                tmp['precision']=precision_recall_curve(y_pred=y_pred,y_true=y_test)
                tmp['auc']=auc(y_pred,y_test)
            
            toret[model.modelname]=tmp

        return toret

    def get_info(self):
        message="Name: "+self.taskName+"\n\n"
        message=message+"Validation: "+self.validation['method']+"\n\n"
        message=message+"Outputs:"+"\n"
        for variable in self.outputs:
            message=message+" - "+variable+": \n     Model: "
            for model in self.outputs[variable]['model']:
                message=message+str(model)+","
            
            message=message+"\n     Grid Search: "+str(self.outputs[variable]['params'])+"\n\n"
        
        return message
    
    def get_output_result(self,output):
        print(f"Returning the concrete result for {output}")
    
    def get_prediction(self,input,output_variable):
        print(f"Returning the prediction of {output_variable} with the input:{input}")
        


