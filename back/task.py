
from .ML.model import ModelImplementation
from sklearn.model_selection import train_test_split
import pickle
import time

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
        
        self.input_names=list(self.contextData.variables)
        self.output_name=self.contextData.targets[0]

        for variable in outputs:
            self.models[variable]=[]
            
            for model in self.outputs[variable]['model']:
                
                self.models[variable].append(ModelImplementation(model=model))


        indexes = list(range(self.contextData.values.shape[0])) 
        tmp=self.contextData.get_values_inputs()
        X=tmp[0]
        self.types=tmp[1]
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
        with open(path, 'rb') as file:
            task = pickle.load(file)
        return task

    def save(self,pathname):
        with open(pathname, 'wb') as file:
            pickle.dump(self, file)
        
    def execute(self,callable,*args,**kwargs):
        
        i=0
        inc=100/len(self.models)
        i+=inc

        callable(self._update_progressbar,args[0][0],int(i))  
        
        print("Performing model training ...")
        for variable in self.models:
            y=self.contextData.get_values_output(variable)
            y_train=y[self.train_index]

            print(f"\tstarting "+variable+"...")
            for model in self.models[variable]:
                #grid search?
                #test train split ?
                #cv ?
                
                
                model.train(self.X_train,y_train,self.validation['method']=="Cross Validation",self.validation['params']['subsets'],self.outputs[variable]['params'],names_input=self.input_names,name_output=self.output_name,types=self.types)
                
                time.sleep(0.1)
                callable(self._update_progressbar,args[0][0],int(i))           
                i+=inc
            print(f"\tfinishing "+variable+"...")

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
            tmp=model.report(self.X_test,y_test)
            toret[model.modelname]={'validation':self.validation['method'],'metrics':tmp,'options':model.get_params()}
            #toret[model.modelname]['params']=model.get_params()

        
        return toret

    def get_info(self):
        message="Name: "+self.taskName+"\n\n"
        message=message+"Validation: "+self.validation['method']+"\n\n"
        message=message+"Outputs:"+"\n"
        for variable in self.outputs:
            message=message+" - "+variable+": \n     Model: "
            rule_generating=False
            for model in self.outputs[variable]['model']:
                if model=="Neurofuzzy":
                    rule_generating=True
                message=message+str(model)+","

            if not rule_generating:
                message=message+"\n     Grid Search: "+str(self.outputs[variable]['params'])+"\n\n"
        
        return message
    
    def get_output_result(self,output):
        print(f"Returning the concrete result for {output}")
    
    def get_prediction(self,input,output_variable):
        print(f"Returning the prediction of {output_variable} with the input:{input}")
        


