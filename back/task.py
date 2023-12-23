
""" Module for task """
import pickle
import datetime
import numpy as np
from numpy.typing import ArrayLike
from sklearn.model_selection import train_test_split
from .ML.model import ModelImplementation


class Task():
    """ Class that defines a task """

    def __init__(self,name,data,outputs,validation,rules=False):
        assert name!="" and name is not None, "Taskname missing"
        assert data is not None, "Input data can not be None"
        assert outputs is not None, "Output data can not be None"
        assert len(outputs)>0, "Incorrect value input for outputs."
        assert validation is not None, "Validation information can not be None"
        assert len(validation) > 0, "Incorrect value input for validation."
        #Rule generating task indicator
        self.rules=rules
        #Name of the task
        self.task_name=name
        #Task date creation
        self.date=datetime.date.today()
        #Path where the task is stored
        self.path=None
        #Reference to the associated data
        self.context_data=data
        #Dictionary with the outputs and the models for each output
        self.outputs=outputs
        #Dictionary with the validation options
        self.validation=validation
        self.models={}
        self.results={}
        self.input_names=list(self.context_data.variables)
        self.output_name=self.context_data.targets[0]
        self._initialize_models(outputs)
        """
        for variable in outputs:
            self.models[variable]=[]
            for model in self.outputs[variable]['model']:
                self.models[variable].append(ModelImplementation(model=model))
        """   
        self._generate_splits()   
        """
        indexes = list(range(self.context_data.values.shape[0])) 
        tmp=self.context_data.get_values_inputs()
        X=tmp[0]
        self.types=tmp[1]
        self.split_test=self.validation['params']['test_size']
        train_index, test_index= train_test_split(indexes, 
        test_size=self.validation['params']['test_size']
        , random_state=42, shuffle=True)

        self.train_index=train_index
        self.test_index=test_index

        self.X_train = X[train_index]
        self.X_test = X[test_index]
        """ 
        self.saved=False
        self.executed=False
    
    @staticmethod
    def load(path: str):
        """
        Static function that loads a task serialized object from a file.

        Args: path - route to the file

        return: the Task objet created

        """
        print(f"Loading task from {path}")
        with open(path, 'rb') as file:
            task = pickle.load(file)
            if not isinstance(task,Task):
                raise ValueError("There is a problem with the task file.")
        return task

    def _generate_splits(self) :
        """
        Function that creates the distribution of the train and test set

        Args: None

        return: None

        """
        indexes = list(range(self.context_data.values.shape[0])) 
        tmp=self.context_data.get_values_inputs()
        X=tmp[0]
        self.types=tmp[1]
        self.split_test=self.validation['params']['test_size']
        train_index, test_index= train_test_split(indexes, test_size=self.split_test
                                                  , random_state=42, shuffle=True)
        self.train_index=train_index
        self.test_index=test_index
        self.X_train = X[train_index]
        self.X_test = X[test_index]

    def _initialize_models(self,outputs):
        """
        Function that intialize te model structure and creates the model obejects.

        Args: None

        return: None

        """
        for variable in outputs:
            self.models[variable]=[]
            for model in self.outputs[variable]['model']:
                params=self.outputs[variable]['params']
                self.models[variable].append(ModelImplementation(model=model,params=params))

    def get_metadata(self):
        """
            Function that returns a dictionary with the metadata of the task
        """
        return {'name':self.task_name,'date':self.date.strftime("%Y-%m-%d")
                ,'path':self.path,'saved':self.saved}
    
    def save(self,pathname: str):
        """
            Function that saves the task on a file
        """
        try:
            self.path=pathname
            self.saved=True
            with open(pathname, 'wb') as file:
                pickle.dump(self, file)
        except Exception as exc:
            raise ValueError("Error while saving task") from exc
        
    def execute(self,callable_function):
        """
            Function used to execute the task adn therefore train all models.

            Args:
                - callable: callable function used for updating the progress
                - *args:
                - **kwargs:
                
            return: None
    
        """
        inc=100
        i=0
        print("Performing model training ...")
        for variable in self.models:
            print(f"\tstarting {variable}...")
            n_models=len(self.models[variable])
            
            for model in self.models[variable]:
                y=self.context_data.get_values_output(variable)
                y_train=y[self.train_index]
                y_test=y[self.test_index]
                model.train(self.X_train,y_train,self.validation['method']=="Cross Validation"
                            ,self.validation['params']['subsets'],self.outputs[variable]['params']
                            ,names_input=self.input_names
                            ,name_output=self.output_name
                            ,types=self.types,X_test=self.X_test,y_test=y_test)
                if callable_function is not None:
                    callable_function(int(i))       
                i+=inc/n_models
            print(f"\tfinishing {variable}...")
        self.executed=True
        print("Training finished")
       
    def _update_progressbar(self,progressbar,value):
        progressbar.Update(value,"Training in progress...")

    def get_report(self,variable):
        """
            Function that return a report of the task as a data structure
        Args:
            - Variable: specific output variable of the that the report is wanted
            
        return: dictionary with the report of the output
    
        """
        toret={}
        models=self.models[variable]
        for model in models:
            tmp={}
            tmp=model.report()
            toret[model.modelname]={'validation':self.validation['method']
                                    ,'metrics':tmp,'options':model.get_params()}
        return toret

    def get_text_reports(self,variable):
        """
           Function that return a report of the task as text
        Args:
            - Variable: specific output variable of the that the report is wanted
            
        return: string with the report of the output

        """
        toret={}
        models=self.models[variable]
        for model in models:
            toret[model.modelname]=model.get_text_report()
        return toret

    def get_model_plot(self,variable: str,model:str):
        """
        Method to get the plot of a trained model

        Args:
            - variable: name of the variable wanted
            - model: model trained wanted
        return: PLot of the specified model
    
        """
        if self.executed:
            for model_obj in self.models[variable]:
                if model_obj.modelname==model:
                    return model_obj.plot_model_results()
        else:
            raise ValueError("Not trained model")
    def get_info(self):
        """
            Function that generates the text report of the task

            Arg. None

            return: string of the information of the task
        
        """
        message="Name: "+self.task_name+"\n\n"
        message=message+"Validation: "+self.validation['method']+"\n"
        message=message+"Split: test("+str(self.split_test)+") train("+str((1-self.split_test))+")"+"\n\n"
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
    
    def get_prediction(self,output_variable:str,model:str,input: ArrayLike,submodel:{}=None):
        """
        Method that returns the correspondent prediction of the specified model.

        Args: 
            -  output_variable: name of the output variable wanted to predict
            -  mode: which of the models trained will be used for prediction
            - input: input data for prediction

        return:  prediction of the given input
        
        """
        i=0
        prediction=None
        if submodel!=None and len(input)!=len(self.input_names):
            input=self._transform_input(submodel['inputs'],input)
        else:
            input=self._transform_input(self.input_names,input)
            
        for mod in self.models[output_variable]:
            if mod.modelname==model:
                prediction=mod.predict(np.array(input,dtype=np.float64).reshape(1,-1),submodel=submodel)
                return prediction
        return None
        
        
    def _transform_input(self,list,input):
        i=0
        for variable in list:
                input[i]=self.context_data.apply_transform(variable,input[i])
                i+=1
        return input

