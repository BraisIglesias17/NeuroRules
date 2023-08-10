from back.data.contextData import ContextData
from back.respuestas import Response,Status
from ..IO.IOManage import IOManage
from back.ML.modelImplementation import SVRModel,RandomForest,SVMModel
from back.ML.neurofuzzy import NeuroFuzzy
from sklearn.metrics import confusion_matrix, classification_report
import numpy as np
from sklearn.model_selection import train_test_split

class Controller():

    def __init__(self):
        """
            Inicializar objetos 

        """
        self.contextData=None
        self.models={}

    def load_content(self,window,event):
        state=True
        try:
            self.contextData=ContextData(IOManage.LoadFile(window,event))
        except Exception as exc:
            state=False

        if state:
            return Response(data=self.contextData.data,status=Status.OK)
        else:
            return Response(data="",status=Status.GENERAL_ERROR)



    def update_data_position(self,row,col,value):

        if self.contextData.update_position(row,col,value):
            return Response(data="",status=Status.OK)
        else:
            return Response(data="",status=Status.VALIDATION_ERROR)
    
    def get_data(self):
        try:
            return Response(data=self.contextData.get_data(),status=Status.OK)
        except Exception as exc:
                return Response(data=str(exc),status=Status.GENERAL_ERROR)
    
    
    def get_data_shape(self):
        try:
            return Response(data=self.contextData.get_shape(),status=Status.OK)
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
    
    def get_summary(self):
        try: 
            data=self.contextData.get_data_summary()
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
            return Response(data="",status=Status.OK)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)


    def create_models(self,model,params):
        
        names=self.contextData.get_names()
        i=0

        toret=[]
        for index in self.contextData.targets_index:
            y=self.contextData.get_column(index)
            X=self.contextData.get_variables()

            index_var=self.contextData.variables_index
            
            #Par X,y de entrenamiento 
            #PCA
            print(f" TRAINING {names[index]}....")
            if all(isinstance(value, str) for value in y):
                #CLASIFICION
                
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                model=SVMModel()
                model.train(X_train,y_train)
                
                predictions = model.predict(X_test)
                report = classification_report(y_test, predictions)
                print(report)
                

            else:
                #Regresión
                y=np.array(y,dtype="float64")
                X=np.array(X,dtype="float64")
                model=NeuroFuzzy(input=X,input_names=names[index_var],output=y,output_name=names[index],n_membership_input=3,n_membership_output=2)
                model.fit(learning_rate=0.01,epochs=50)
                
                toret.append(model.get_rules())
                name="model_"+str(i)
                self.models[name]=model
            print("TRAINED")
            i+=1
            #toret={'R2':,'rules':}
            
        return toret
    
    def set_cleanse_option(self,variable,options):
        try:
            self.contextData.set_cleanse(variable,options)
            return Response(data="",status=Status.OK)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)

    def get_cleanse(self):
        try:
            ret=self.contextData.get_cleanse()
            return Response(data=ret,status=Status.OK)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
        

    def apply_cleanse(self,variable):
        try:
            deleted_rows=self.contextData.apply_cleanse(variable)
            return Response(data={'deleted_rows':deleted_rows},status=Status.OK)
        except Exception as exc:
            return Response(data=str(exc),status=Status.GENERAL_ERROR)
            

    


