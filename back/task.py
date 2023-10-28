
from .ML.model import ModelImplementation
from sklearn.model_selection import train_test_split
import pickle
import datetime
import numpy as np

class Task():


    def __init__(self,name,data,outputs,validation,rules=False):

        assert name!="" and name!=None

        assert data!=None

        assert outputs!=None

        assert validation!=None


        self.rules=rules

        ##metadata
        self.taskName=name
        self.date=datetime.date.today()

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
            
        self.saved=True
        
    def execute(self,callable,*args,**kwargs):
        
        
        inc=100
        i=inc
        #i+=inc

        #callable(self._update_progressbar,args[0][0],int(i))  
        
        print("Performing model training ...")
        for variable in self.models:
            

            print(f"\tstarting "+variable+"...")
            for model in self.models[variable]:
                y=self.contextData.get_values_output(variable)
                y_train=y[self.train_index]
                y_test=y[self.test_index]
                model.train(self.X_train,y_train,self.validation['method']=="Cross Validation",self.validation['params']['subsets'],self.outputs[variable]['params'],names_input=self.input_names,name_output=self.output_name,types=self.types,X_test=self.X_test,y_test=y_test)
                
                #time.sleep(0.1)
                if callable!=None:
                    callable(int(i))       
                    
                i+=inc
            print(f"\tfinishing "+variable+"...")

        self.executed=True
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
            #y=self.contextData.get_values_output(variable)
            #y_test=y[self.test_index]
            tmp=model.report()
            
            toret[model.modelname]={'validation':self.validation['method'],'metrics':tmp,'options':model.get_params()}
            #toret[model.modelname]['params']=model.get_params()

        
        return toret

    def get_text_reports(self,variable):
        toret={}
        models=self.models[variable]

        for model in models:
            toret[model.modelname]=model.get_text_report()
        
        return toret

    def get_info(self):
        message="Name: "+self.taskName+"\n\n"
        message=message+"Validation: "+self.validation['method']+"\n\n"
        message=message+"Outputs:"+"\n"
        for variable in self.outputs:
            message=message+" - "+variable+": \n     Model: "
            
            for model in self.outputs[variable]['model']:
                message=message+str(model)

                if model!=self.outputs[variable]['model'][-1]:
                    message=message+","

            if not self.rules:
                message=message+"\n     Grid Search: "+str(self.outputs[variable]['params'])+"\n\n"
            else:
                message=message+"\n\n"
        
        return message
    
    def get_output_result(self,output):
        print(f"Returning the concrete result for {output}")
    
    def get_prediction(self,output_variable,model,input):
        #apply transformations to inputs
        i=0
        prediction=None
        for variable in self.input_names:
            input[i]=self.contextData.apply_transform(variable,input[i])
            i+=1
        if not self.rules:
            for model in self.models[output_variable]:
                if model==model:
                    prediction=model.predict(np.array(input,dtype=np.float64).reshape(1,-1))
        
        return prediction
        
        


