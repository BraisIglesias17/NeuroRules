from back.data.contextData import ContextData
from back.respuestas import Response,Status
from back.ML.neurofuzzy import NeuroFuzzy
from sklearn.metrics import confusion_matrix, classification_report
import numpy as np
from sklearn.model_selection import train_test_split
from ..statistic.statistic import StatisticTest
from ..ML.model import Model
from ..task import Task
import traceback
from ..saver import Saver
from ..tracer import Trace

class Controller():

    def __init__(self):
        """
            Inicializar objetos 

        """
        self.contextData=None
        self.models={}

        self.currentTask=None

    def load_content(self,df,filename):
        try:
            
            self.contextData=ContextData(df)
            info={'data':self.contextData.data,'file':filename}
            Trace().log("Content loaded from file: "+filename)
            return Response(data=info,status=Status.OK)
        except Exception as exc:
            Trace().log("Loading content, "+str(exc))
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
           

    def create_empty_set(self,dict):
        try:
            
            self.contextData=ContextData(dict=dict)
            Trace().log("Created empty set succesfully")
            return Response(data=self.contextData.data,status=Status.OK)

        except Exception as exc:
            Trace().log("Creating set, "+str(exc))
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
    
    def add_columns(self,dict):
        try:
            
            if self.contextData!=None:
                self.contextData.add_columns(dict)
                Trace().log("Columns added")
            else:
                self.contextData=ContextData(dict)
                Trace().log("Created empty set succesfully")

            return Response(data=self.contextData.data,status=Status.OK)

        except Exception as exc:
            Trace().log("Adding columns , "+str(exc))
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
        
    
    def update_data_position(self,row,col,value):

        try:

            if self.contextData!=None:
                self.contextData.update_position(row,col,value)

            Trace().log(f"Position ({row},{col}) updated manually with new value {value}")
            return Response(data="",status=Status.OK)
        except Exception as exc:
            Trace().log(f"Updating position ({row},{col}) with new value {value}")
            return Response(data=str(exc),status=Status.VALIDATION_ERROR)
            
    
    def get_types(self):
        try:
            return Response(data=self.contextData.get_types(),status=Status.OK)
        except Exception as exc:
                return Response(data=str(exc),status=Status.GENERAL_ERROR)
        
    def get_data(self):
        try:
            if self.contextData==None:
                toret=None
            else:
                toret=self.contextData.get_data()
            return Response(data=toret,status=Status.OK)
        except Exception as exc:
                return Response(data=str(exc),status=Status.GENERAL_ERROR)
    
    
    def get_data_shape(self):
        try:

            toret=None
            if self.contextData!=None:
                toret=self.contextData.get_shape()
            return Response(data=toret,status=Status.OK)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
    

    def get_independent_indexes(self):
        try:
            return Response(data=self.contextData.variables_index,status=Status.OK)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
    
    def get_target_indexes(self):
        try:
            return Response(data=self.contextData.targets_index,status=Status.OK)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
    
    def get_target_process_type(self):
        try:
            return Response(data=self.contextData.get_type_process_target(),status=Status.OK)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)

    def get_summary(self):
        try: 
            data=self.contextData.get_data_summary()
            return Response(data=data,status=Status.OK)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
    
    def get_variable_summary(self,variable,group):
        try:
            data=self.contextData.get_variable_summary(variable,group)
            
            return Response(data=data,status=Status.OK)
        
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
        
    def set_independent_variables(self,indexes):
        try:
            self.contextData.set_variables(indexes)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
        
    def get_names(self):
        try:
            data=self.contextData.get_names()
            return Response(data=data,status=Status.OK)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
    

    def set_targets(self,indexes):

        try:
            self.contextData.set_target(indexes)
            return Response(data="",status=Status.OK)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)

    def get_position(self,row,col):

        try:
            value=self.contextData.get_position(row,col)
            return Response(data=value,status=Status.OK)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
        

    def get_column(self,col):
        try:
            value=self.contextData.get_column(col)
            return Response(data=value,status=Status.OK)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
    

    ##NOT USED
    def update_context_data(self,df):
        try:
            if self.contextData==None:
                self.contextData=ContextData(df)
            else:
                self.contextData.update_set(df)
            return Response(data="",status=Status.OK)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
        
    
    def clear_data(self):
        try:
            self.contextData=ContextData()
            Trace().log(f"Data cleared")
            return Response(data="",status=Status.OK)
        except Exception as exc:
            Trace().log(f"Clearing data, "+str(exec))
            return Response(data=str(exc),status=Status.GENERAL_ERROR)

    def clear_task(self):
        try:
            del self.currentTask
            self.currentTask=None
            Trace().log(f"Task cleared")
            return Response(data="",status=Status.OK)
        except Exception as exc:
            Trace().log(f"Clearing task")
            return Response(data=str(exc),status=Status.GENERAL_ERROR)    

    def save_data(self,pathname):
        try:
            if self.contextData!=None:
                self.contextData.save(pathname)
                Trace().log(f"Data saved on "+pathname)
            return Response(data="",status=Status.OK)
        except Exception as exc:
            Trace().log(f"On saving data, "+pathname)
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
    
    def set_cleanse_option(self,variable,options):
        try:
            self.contextData.set_cleanse(variable,options)
            Trace().log(f"Cleanse applied to "+variable)
            return Response(data="",status=Status.OK)
        except Exception as exc:
            Trace().log(f"On applying to "+variable)
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
    
    def set_preprocess_option(self,variable,options):
        try:
            self.contextData.set_preprocess(variable,options)
            return Response(data="",status=Status.OK)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)

    def get_cleanse(self):
        try:
            ret=self.contextData.get_cleanse()
            return Response(data=ret,status=Status.OK)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
        
    def get_preprocess(self):
        try:
            ret=self.contextData.get_preprocess()
            return Response(data=ret,status=Status.OK)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
    
    def confirm_delete(self):
        try:
            self.contextData.delete_marked()
            return Response(data={},status=Status.OK)
        except Exception as exc:
            traceback.print_exc()
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
        
    def apply_cleanse(self,variable):
        try:
            result=self.contextData.apply_cleanse(variable)
            
            return Response(data={'deleted_rows':result[0],'modified_rows':result[1]},status=Status.OK)
        except Exception as exc:
            traceback.print_exc()
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
    
    def apply_preprocess(self,variable):
        try:
            
            result=self.contextData.apply_preprocess(variable)
            
            return Response(data={result},status=Status.OK)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
        
    def refresh_types(self):
        try:
            self.contextData._get_types()
            return Response(data={},status=Status.OK)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)

    def delete_row(self,row):
        try:
            value=self.contextData.delete_row(row)
            return Response(data={},status=Status.OK)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
    
    def delete_col(self,col):
        try:
            value=self.contextData.delete_column(col)
            return Response(data={},status=Status.OK)
        except Exception as exc:
            traceback.print_exc()
            return Response(data=str(exc),status=Status.GENERAL_ERROR)

    def set_col_as_id(self,name,remove=False):
        try:
            if remove:
                self.contextData.remove_identifier_col(name)
            else:
                self.contextData.add_identifier_col(name)

            return Response(data={},status=Status.OK)
        
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
    def clear_data(self):
        try:
            
            self.contextData=ContextData()
            
            return Response(data={},status=Status.OK)
        except Exception as exc:
            print(exc)
            return Response(data=str(exc),status=Status.GENERAL_ERROR)


    def rename_col(self,new_name,old_name):
        try:
            
            res=self.contextData.rename_col(new_name,old_name)
            
            if res:
                return Response(data={},status=Status.OK)
        
        except Exception as exc:
            print(exc)
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
        
    
    def get_outliers(self):
        try:
            
            res=self.contextData.get_outliers()
            
            return Response(data=res,status=Status.OK)
        
        except Exception as exc:
            traceback.print_exc()
            return Response(data=str(exc),status=Status.GENERAL_ERROR)

    def get_available_models(self):
        try:
            
            res={'regression':Model.GET_REGRESSION_LIST(),'classification':Model.GET_CLASSIFICATION_LIST()}
            
            return Response(data=res,status=Status.OK)
        
        except Exception as exc:
            print(exc)
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
        
    def automatic_statistic_test(self):
        try:
            """
            data=self.contextData.get_numeric_variables()
            normal_variables=[]


            for col in data:
                result=StatisticTest.shapiro_wilk((data[col]))
                if result.pvalue>0.05:
                    normal_variables.append(col)"""
            
            normal_variables=self.contextData.get_normal_variables()
            
            covariance_pairs=self.contextData.get_covariance_pairs()
            difference_in_groups=self.contextData.get_differences_in_groups()
            covariance={'directly':covariance_pairs[0],'inverse':covariance_pairs[1]}

            return Response(data={'normal_variables':normal_variables,'covariance':covariance,'differences':difference_in_groups},status=Status.OK)

        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)

    
    def create_task(self,taskname,models,validation,rules):

        try:
            
            self.currentTask=Task(taskname,self.contextData,models,validation,rules)

            return Response(data={},status=Status.OK)
            
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
        
    def get_task_info(self):

        try:
            
            info=self.currentTask.get_info()
            return Response(data=info,status=Status.OK)
            
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
        
    def execute_task(self,callable,*args):
        try:
            
            self.currentTask.execute(callable,args)
            
            return Response(data={},status=Status.OK)
        except Exception as exc:
            print(exc)
            traceback.print_exc() 
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
        
    def get_variable_models(self):
        try:
            
            if self.currentTask!=None:
                return Response(data=self.currentTask.models,status=Status.OK)
            
        except Exception as exc:
            print(exc)
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
    
    def get_output_info(self,variable):

        try:
            
            return Response(data=self.currentTask.get_report(variable),status=Status.OK)
            
        except Exception as exc:
            print(exc)
            return Response(data=str(exc),status=Status.GENERAL_ERROR)

    def get_text_reports(self,variable):
        try:
            
            return Response(data=self.currentTask.get_text_reports(variable),status=Status.OK)
            
        except Exception as exc:
            traceback.print_exc()
            return Response(data=str(exc),status=Status.GENERAL_ERROR)

    def get_task_name(self):
        try:
            
            return Response(data=self.currentTask.taskName,status=Status.OK)
            
        except Exception as exc:
           
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
        
    def task_state(self):
        try:
            
            if self.currentTask!=None and self.currentTask.executed and self.currentTask.saved:
                #se cierra la tarea actual
                return Response(data={'name':self.currentTask.taskName,'rules':self.currentTask.rules},status=Status.EXISTING_TASK)
            elif self.currentTask!=None and self.currentTask.executed and not self.currentTask.saved:
                #se pregunta al usuario si quiere guardar
                return Response(data={'name':self.currentTask.taskName,'rules':self.currentTask.rules},status=Status.EXISTING_TASK_UNSAVED)
            elif self.currentTask!=None and not self.currentTask.executed:
                #se pregunta al usuario si quiere mantener las variables o si quiere cambiar
                return Response(data={'name':self.currentTask.taskName,'rules':self.currentTask.rules},status=Status.EXISTING_TASK_NO_EXECUTED)            
            else:
                return Response(data='There is no task',status=Status.UNEXISTING_TASK)
        except Exception as exc:
            print(exc)
            return Response(data=str(exc),status=Status.GENERAL_ERROR)

    def save_task(self,path):
        try:
            
            if self.currentTask==None:
                raise ValueError("Non existing task")
            
            self.currentTask.save(path)
            return Response(data={},status=Status.OK)
            
        except Exception as exc:
            print(exc)
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
    
    def get_inputs_task(self):
        try:
            
            
            return Response(data=self.currentTask.input_names,status=Status.OK)
            
        except Exception as exc:
            print(exc)
            return Response(data=str(exc),status=Status.GENERAL_ERROR)

    def import_task(self,path):
        try:
            
            self.currentTask=Task.load(path)
            self.contextData=self.currentTask.contextData
            
            return Response(data={},status=Status.OK)
            
        except Exception as exc:
            print(exc)
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
        
    def get_prediction(self,variable,model,input):
        try:
            
            prediction=self.currentTask.get_prediction(variable,model,input)
            return Response(data=prediction,status=Status.OK)
            
        except Exception as exc:
            print(exc)
            #traceback.print_exc()
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
        
    def get_task_metadata(self):
        try:
            
            if self.currentTask!=None:
                result=self.currentTask.get_metadata()

                return Response(data=result,status=Status.OK)
            
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
    def save_file(self,content,path):
        try:
            
            saver=Saver(path=path,content=content)
            
            saver.save()
            
            return Response(data={},status=Status.OK)
        
        except Exception as exc:
            
            traceback.print_exc()
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
        
    def get_model_plot(self,variable,model):
        try:
            
            figure=self.currentTask.get_model_plot(variable,model)
            return Response(data=figure,status=Status.OK)
        
        except Exception as exc:
            
            traceback.print_exc()
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
    
    def get_nominal_classes(self):
        try:
            
            return Response(data=self.contextData.get_nominals_classes(),status=Status.OK)
        
        except Exception as exc:
            
            traceback.print_exc()
            return Response(data=str(exc),status=Status.GENERAL_ERROR)