from back.data.contextData import ContextData
from back.respuestas import Response,Status
from ..ML.model import Model
from ..task import Task
from ..saver import Saver
from ..tracer import Trace
from numpy.typing import ArrayLike
from pandas import DataFrame
import traceback

class Controller():

    def __init__(self):
        """
            Inicializar objetos 

        """
        self.contextData: ContextData=None
        self.currentTask: Task=None
        self.trace=Trace()

    def template_method(function):
        def wrapper(*args, **kwargs):
            try:
                response = function(*args, **kwargs)
                return response
            except Exception as exc:
                traceback.print_exc()
                trace=Trace()
                trace.log(message=str(exc),level=Trace.ERROR)
                return Response(data=str(exc),status=Status.GENERAL_ERROR)
        return wrapper

    @template_method
    def load_content(self,df: DataFrame,filename):
        self.contextData=ContextData(df)
        info={'data':self.contextData.data,'file':filename}
        Trace().log("Content loaded from file: "+filename)
        return Response(data=info,status=Status.OK)

           
    @template_method
    def create_empty_set(self,dict):
        self.contextData=ContextData(dict=dict)
        Trace().log("Created empty set succesfully")
        return Response(data=self.contextData.data,status=Status.OK)
        
    
    @template_method
    def add_columns(self,dict):
        if self.contextData!=None:
            self.contextData.add_columns(dict)
            Trace().log("Columns added")
        else:
            self.contextData=ContextData(dict)
            Trace().log("Created empty set succesfully")

        return Response(data=self.contextData.data,status=Status.OK)

    
    
    @template_method
    def update_data_position(self,row:int,col:int,value):
        if self.contextData!=None:
            self.contextData.update_position(row,col,value)
        Trace().log(f"Position ({row},{col}) updated manually with new value {value}")
        return Response(data="",status=Status.OK)
    

    @template_method     
    def get_types(self):
        return Response(data=self.contextData.get_types(),status=Status.OK)
        
    
    @template_method
    def get_data(self):
        if self.contextData==None:
            toret=None
        else:
            toret=self.contextData.get_data()
        return Response(data=toret,status=Status.OK)
        
    
    @template_method
    def get_data_shape(self):
        toret=None
        if self.contextData!=None:
            toret=self.contextData.get_shape()
        return Response(data=toret,status=Status.OK)
        
    
    
    @template_method
    def get_independent_indexes(self):
        return Response(data=self.contextData.variables_index,status=Status.OK)
        
    
    @template_method
    def get_target_indexes(self):
        return Response(data=self.contextData.targets_index,status=Status.OK)
        
    
    @template_method
    def get_target_process_type(self):
        return Response(data=self.contextData.get_type_process_target(),status=Status.OK)
        

    @template_method
    def get_summary(self): 
        data=self.contextData.get_data_summary()
        return Response(data=data,status=Status.OK)
        
    
    @template_method
    def get_variable_summary(self,variable:str,group:str):
        data=self.contextData.get_variable_summary(variable,group)    
        return Response(data=data,status=Status.OK)
        
        
    @template_method
    def set_independent_variables(self,indexes:list[int]):
        self.contextData.set_variables(indexes)
        return Response(data={},status=Status.OK)
        
        
    @template_method
    def get_names(self):
        if self.contextData!=None:
            data=self.contextData.get_names()
        else:
            data=[]
        return Response(data=data,status=Status.OK)
       
    
    @template_method
    def set_targets(self,indexes:list[int]):
        self.contextData.set_target(indexes)
        return Response(data="",status=Status.OK)
        

    @template_method
    def get_position(self,row:int,col:int):
        value=self.contextData.get_position(row,col)
        return Response(data=value,status=Status.OK)
        
        
    @template_method
    def get_column(self,col:int):
        value=self.contextData.get_column(col)
        return Response(data=value,status=Status.OK)
        
    
    @template_method
    def clear_data(self):
        self.contextData=ContextData()
        self.trace.log(f"Data cleared")
        return Response(data="",status=Status.OK)
        
        

    @template_method
    def clear_task(self):
        del self.currentTask
        self.currentTask=None
        self.trace.log(f"Task cleared")
        return Response(data="",status=Status.OK)
         

    @template_method
    def save_data(self,pathname: str):
        if self.contextData!=None:
            self.contextData.save(pathname)
            self.trace.log(f"Data saved on "+pathname)
        return Response(data="",status=Status.OK)
        
    
    @template_method
    def set_cleanse_option(self,variable:str,options):
        self.contextData.set_cleanse(variable,options)
        return Response(data="",status=Status.OK)
        
        
    
    @template_method
    def set_preprocess_option(self,variable:str,options):
        self.contextData.set_preprocess(variable,options)
        return Response(data="",status=Status.OK)
        
        

    @template_method
    def get_cleanse(self):
        value=self.contextData.get_cleanse()
        return Response(data=value,status=Status.OK)
    
        
    @template_method
    def get_preprocess(self):
        ret=self.contextData.get_preprocess()
        return Response(data=ret,status=Status.OK)
        
    
    @template_method
    def confirm_delete(self):
        self.contextData.delete_marked()
        return Response(data={},status=Status.OK)
     
    
    @template_method 
    def apply_cleanse(self,variable:str):
        result=self.contextData.apply_cleanse(variable) 
        Trace().log(f"Cleanse applied to {variable} with {result[0]} deleted and {result[1]} modified")
        return Response(data={'deleted_rows':result[0],'modified_rows':result[1]},status=Status.OK)
        
        
    @template_method
    def apply_preprocess(self,variable:str):
        result=self.contextData.apply_preprocess(variable)
        Trace().log(f"Transformation applied to {variable} ")
        return Response(data={result},status=Status.OK)
        
    
    @template_method
    def refresh_types(self):
        self.contextData._get_types()
        return Response(data={},status=Status.OK)
        

    @template_method
    def delete_row(self,row:int):
        value=self.contextData.delete_row(row)
        Trace().log(f"Row {row} deleted")
        return Response(data={value},status=Status.OK)
        
    
    @template_method
    def delete_col(self,col:int):
        value=self.contextData.delete_column(col)
        Trace().log(f"Column {col} deleted")
        return Response(data={value},status=Status.OK)


    @template_method
    def set_col_as_id(self,name:str,remove:bool=False):
        if remove:
            self.contextData.remove_identifier_col(name)
            print("HOLSSS")
            Trace().log(f"Removed {name} from identifier list")
        else:
            self.contextData.add_identifier_col(name)
            Trace().log(f"Added {name} to identifier list")
        return Response(data={},status=Status.OK)
        

    @template_method
    def rename_col(self,new_name: str,old_name:str):
        res=self.contextData.rename_col(new_name,old_name)
        if res:
            Trace().log(f"Variable {old_name} renamed to {new_name}")
            return Response(data={},status=Status.OK)
        

    @template_method
    def get_outliers(self):
        res=self.contextData.get_outliers()
        return Response(data=res,status=Status.OK)
        

    @template_method
    def get_available_models(self):
        res={'regression':Model.GET_REGRESSION_LIST(),'classification':Model.GET_CLASSIFICATION_LIST()}
        return Response(data=res,status=Status.OK)
        
 
    @template_method
    def automatic_statistic_test(self):
        normal_variables=self.contextData.get_normal_variables()
        correlation_pairs=self.contextData.get_correlation_pairs()
        covariance_pairs=self.contextData.get_covariance_pairs()
        difference_in_groups=self.contextData.get_differences_in_groups()
        covariance={'directly':covariance_pairs[0],'inverse':covariance_pairs[1]}
        correlation={'directly':correlation_pairs[0],'inverse':correlation_pairs[1]}
        return Response(data={'normal_variables':normal_variables,'correlation':correlation
                                  ,'covariance':covariance,'differences':difference_in_groups},status=Status.OK)

 
    @template_method
    def create_task(self,taskname:str,models,validation,rules):
        self.currentTask=Task(taskname,self.contextData,models,validation,rules)
        Trace().log(f"Created task {taskname}")
        return Response(data={},status=Status.OK)
 
  
    @template_method
    def get_task_info(self):
        info=self.currentTask.get_info()
        return Response(data=info,status=Status.OK)
        
   
    @template_method
    def execute_task(self,callable,*args):
        self.currentTask.execute(callable) 
        Trace().log(f"Executed task")   
        return Response(data={},status=Status.OK)
      
   
    @template_method
    def get_variable_models(self):
        if self.currentTask!=None:
            return Response(data=self.currentTask.models,status=Status.OK)

  
    @template_method
    def get_output_info(self,variable:str):    
        return Response(data=self.currentTask.get_report(variable),status=Status.OK)
  
        
    
    @template_method
    def get_text_reports(self,variable:str):    
        return Response(data=self.currentTask.get_text_reports(variable),status=Status.OK)
 
 
    @template_method
    def get_task_name(self): 
        name=""
        if self.currentTask!=None:
            name=self.currentTask.task_name
        return Response(data=name,status=Status.OK)
 
    
   
    @template_method
    def task_state(self):
        if self.currentTask!=None and self.currentTask.executed and self.currentTask.saved:
            #se cierra la tarea actual
            return Response(data={'name':self.currentTask.task_name,'rules':self.currentTask.rules},status=Status.EXISTING_TASK)
        elif self.currentTask!=None and self.currentTask.executed and not self.currentTask.saved:
            #se pregunta al usuario si quiere guardar
            return Response(data={'name':self.currentTask.task_name,'rules':self.currentTask.rules},status=Status.EXISTING_TASK_UNSAVED)
        elif self.currentTask!=None and not self.currentTask.executed:
            #se pregunta al usuario si quiere mantener las variables o si quiere cambiar
            return Response(data={'name':self.currentTask.task_name,'rules':self.currentTask.rules},status=Status.EXISTING_TASK_NO_EXECUTED)            
        else:
            return Response(data='There is no task',status=Status.UNEXISTING_TASK)
        

    @template_method
    def save_task(self,path:str):
        if self.currentTask==None:
            raise ValueError("Non existing task")
        self.currentTask.save(path)
        Trace().log(f"Task saved in {path}")  
        return Response(data={},status=Status.OK)
        

    @template_method
    def get_inputs_task(self):
        return Response(data=self.currentTask.input_names,status=Status.OK)

    @template_method
    def import_task(self,path: str):
        self.currentTask=Task.load(path)
        self.contextData=self.currentTask.context_data  
        Trace().log(f"Task imported from {path}")    
        return Response(data={},status=Status.OK)
        
  
    @template_method
    def get_prediction(self,variable:str,model:str,input,submodel:{}=None):
        prediction=self.currentTask.get_prediction(variable,model,input,submodel)
        return Response(data=prediction,status=Status.OK)
   
  
    @template_method
    def get_task_metadata(self):
        #REVISAR
        if self.currentTask!=None:
            result=self.currentTask.get_metadata()

            return Response(data=result,status=Status.OK)
        

    @template_method
    def save_file(self,content,path: str):
        saver=Saver(path=path,content=content)
        saver.save()
        Trace().log(f"File saved in {path}")  
        return Response(data={},status=Status.OK)

           
    @template_method
    def get_model_plot(self,variable:str,model:str):
        figure=self.currentTask.get_model_plot(variable,model)
        return Response(data=figure,status=Status.OK)


    @template_method
    def get_nominal_classes(self):    
        return Response(data=self.contextData.get_nominals_classes(),status=Status.OK)
    
    