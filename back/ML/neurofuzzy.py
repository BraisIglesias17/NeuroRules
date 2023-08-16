import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from scipy.optimize import minimize
from mpl_toolkits.mplot3d import Axes3D
from sklearn.metrics import r2_score


class NeuroFuzzy():
    """

    CLASE PARA MODELADO DE SISTEMA NEURO-FUZZY

    """


    ""
    def NAMES(self,number):
        """
        Esta funcion devuelve el nombre de las membresías.

        Argumentos: number - numero de membresías

        Return: nombres para esa cantidad de membresías
        
        """
        if number == 2:
            return ['Low','High']
        elif number == 3:
            return ['Low','Medium','High']
        elif number ==4:
            return['Low','Medium_1','Medium_2','High']    
    


    def __init__(self,input,input_names,output,output_name,n_membership_input,n_membership_output,memebership_function="default"):
        
        """
        Constructor
        
        Argumentos:
            -input: variables numéricas de entrada de la red
            -input_names: nombres de las variables de entrada
            -output: variable de salida de la red "target"
            -ouput_name: nombre de la variable target
            -n_membership_input: numero de membresias para las entradas
            -n_membership_output: numero de membresias para las salidas
            -memebership_function: tipo de funcion de membresía a utilizar (NO USADO DE MOMENTO)

        """
        self.n_variables=input.shape[1]
        self.n_membership=n_membership_input
        self.n_membership_output=n_membership_output
        self.trained=False

        self.memb_func=memebership_function
        self.X_names=input_names
        self.X=input
        self.y=output
        self.y_name=output_name

        #variable que contendrá la matriz de valores fuzzificados
        self.fuzz_X=None

        #array de pesos de cada regla
        # el numero de reglas se determina por el numero de funciones de membresia de entrada elevada al numero de variables
        self.weigths=np.zeros(self.n_membership**self.n_variables)


        #lista que contendrá las reglas
        self.rules=[]

        #lista de objetos Antecedent de skfuzzy (uno por cada variable de entrada)
        self.antecedents=[]
        for i in range(0,len(input_names),1):
            self.antecedents.append(ctrl.Antecedent(np.sort(input[:,i]),input_names[i]))
        
        #objeto Consequence de skfuzzy para la variable target
        self.consecuence=ctrl.Consequent(np.sort(output.flatten()),output_name)
      
        #generación de las funciones de membresía con skfuzzy
        self.consecuence.automf(n_membership_output,names=self.NAMES(self.n_membership_output))
    

        #variables utilizadas para almacenar la salida de la red en cada etapa
        self.layer_1_output=None
        self.layer_2_output=None
        self.layer_3_output=None
        self.layer_4_output=None

        self.r2=0.0
        
        
    def fuzzyfication(self,C=0.3):
        """
        Funcion utilziada para generar los valores difusos para cada variable en cada membresía y las almacena en la 
        variable de clase fuzz_X

        Argumento: coeficiente C (NO USADO)

        Return: DataFrame de los valores difusos.
        """
        try:

            X=self.X
            toret=pd.DataFrame()
            n_cols = X.shape[1]
    
            # Recorrer la matriz por columnas
            for i in range(n_cols):
                col = X[:, i]
            
                col=np.sort(col)
                #control_points=min(col),np.percentile(col,30),np.mean(col),np.percentile(col,60),max(col)
                
                #Utilizacion de la funcion automf con el numero de membresias de entrada para generar las membresías
                self.antecedents[i].automf(self.n_membership,names=self.NAMES(self.n_membership))

                #lista que almacena las funciones de membresía (NO USADA)
                mfs=[]
                
                for j in range(self.n_membership):
                    
                    mf=fuzz.interp_membership(x=self.antecedents[i].universe,xmf=self.antecedents[i][self.NAMES(self.n_membership)[j]].mf,xx=col)
                    tmp=pd.DataFrame(mf,columns=[self.X_names[i]+'_'+str(self.NAMES(self.n_membership)[j])])
                    mfs.append(mf)
                    toret=pd.concat([toret,tmp],axis=1)
                """
                mf_low=fuzz.interp_membership(x=col,xmf=self.antecedents[i]['Low'].mf,xx=col)
                #mf_medium=fuzz.interp_membership(x=col,xmf=self.antecedents[i]['Med'].mf,xx=col)
                mf_high=fuzz.interp_membership(x=col,xmf=self.antecedents[i]['High'].mf,xx=col)
            
                tmp1=pd.DataFrame(mf_low,columns=[self.X_names[i]+'_plow'])
                #tmp3=pd.DataFrame(mf_medium,columns=[self.X_names[i]+'_med'])
                tmp2=pd.DataFrame(mf_high,columns=[self.X_names[i]+'_high'])
                toret=pd.concat([toret,tmp1,tmp2],axis=1)
                """
            self.fuzz_X=toret.values

            return toret

        except Exception as exc:
            print(exc)

    def to_fuzzy(self,input):
        """
        Funcion que fuzzifica un registro de entrada de la red

        Argumentos:
            -input: valores de entrada de la red para cada variable
            -output: valores de salida de la red (fuzzificacion de la entrada)
        """
        
        toret=pd.DataFrame()
        i=0
        for ant in self.antecedents: 

            #Se puede eliminar esta lista  
            mfs=[]
            
            for j in range(self.n_membership):
                mf=fuzz.interp_membership(x=ant.universe,xmf=ant[self.NAMES(self.n_membership)[j]].mf,xx=input[i])
                tmp=pd.DataFrame([mf],columns=[self.X_names[i]+'_'+str(self.NAMES(self.n_membership)[j])])
                mfs.append(mf)
                toret=pd.concat([toret,tmp],axis=1)
            
            """
            mf_low=fuzz.interp_membership(x=ant.universe,xmf=ant['Low'].mf,xx=input[i])
            #mf_medium=fuzz.interp_membership(x=col,xmf=self.antecedents[i]['Med'].mf,xx=col)
            mf_high=fuzz.interp_membership(x=ant.universe,xmf=ant['High'].mf,xx=input[i])
            
            tmp1=pd.DataFrame([mf_low],columns=[self.X_names[i]+'_plow'])
            #tmp3=pd.DataFrame(mf_medium,columns=[self.X_names[i]+'_med'])
            tmp2=pd.DataFrame([mf_high],columns=[self.X_names[i]+'_high'])
                   
            toret=pd.concat([toret,tmp1,tmp2],axis=1)
            """
            
        
            i+=1
       
        return toret

    def fit(self,learning_rate=0.01,epochs=25):
        self.fuzzyfication()
        self.gradient_descent(learning_rate=learning_rate,epochs=epochs)

    def multivariate_memb(self,input):

        """
        Capa de la red cuyo objetivo es generar los valores de multivariable aplicando a los valores difusos de entrda una operación T NORMA

        Argumentos:
            - input: array de valores de entrada de la red fuzzyficadas (salida de la funcion to_fuzzy) 
            
        Return:
            - output: array de valores difussos de funcion multivariable 
        
        """
        toret=None
        size=self.n_membership*self.X.shape[1]
        
        if self.n_variables == 1:

            #Combinaciones para una variable variables dos membresias
            r=[]
            length=len(self.rules)
            for i in range(self.n_membership):
                r.append(input[i])
                #si es la primera ieracion se crean las reglas
                if length==0:
                    self.rules.append("IF "+self.X_names[0]+" is "+self.NAMES(self.n_membership)[i]+" THEN")
            toret=r

        elif self.n_variables==2 and self.n_membership==2:
            #Combinaciones para dos variables dos membresias

            #si es la primera ieracion se crean las reglas
            if len(self.rules)==0:
                self.rules.append("IF "+self.X_names[0]+" is LOW AND "+self.X_names[1]+" is LOW THEN")
                self.rules.append("IF "+self.X_names[0]+" is LOW AND "+self.X_names[1]+" is HIGH THEN")
                self.rules.append("IF "+self.X_names[0]+" is HIGH AND "+self.X_names[1]+" is LOW THEN")
                self.rules.append("IF "+self.X_names[0]+" is HIGH AND "+self.X_names[1]+" is HIGH THEN")

            
            r1=self.product_tnorm(input[0],input[2])
            r2=self.product_tnorm(input[0],input[3])
            r3=self.product_tnorm(input[1],input[2])         
            r4=self.product_tnorm(input[1],input[3])

            toret=[r1,r2,r3,r4]

        elif self.n_variables==2 and self.n_membership == 3:
            
            #Combinaciones para dos variables tres membresias

            #si es la primera ieracion se crean las reglas
            if len(self.rules)==0:
                self.rules.append("IF "+self.X_names[0]+" is LOW AND "+self.X_names[1]+" is LOW THEN")
                self.rules.append("IF "+self.X_names[0]+" is LOW AND "+self.X_names[1]+" is MED THEN")
                self.rules.append("IF "+self.X_names[0]+" is LOW AND "+self.X_names[1]+" is HIGH THEN")
                self.rules.append("IF "+self.X_names[0]+" is MED AND "+self.X_names[1]+" is LOW THEN")
                self.rules.append("IF "+self.X_names[0]+" is MED AND "+self.X_names[1]+" is MED THEN")
                self.rules.append("IF "+self.X_names[0]+" is MED AND "+self.X_names[1]+" is HIGH THEN")
                self.rules.append("IF "+self.X_names[0]+" is HIGH AND "+self.X_names[1]+" is LOW THEN")
                self.rules.append("IF "+self.X_names[0]+" is HIGH AND "+self.X_names[1]+" is MED THEN")
                self.rules.append("IF "+self.X_names[0]+" is HIGH AND "+self.X_names[1]+" is HIGH THEN")

            #Combinaciones para dos variables dos membresias
            r1=self.product_tnorm(input[0],input[3])
            r2=self.product_tnorm(input[0],input[4])
            r3=self.product_tnorm(input[0],input[5])
            r4=self.product_tnorm(input[1],input[3])
            r5=self.product_tnorm(input[1],input[4])
            r6=self.product_tnorm(input[1],input[5])
            r7=self.product_tnorm(input[2],input[3])
            r8=self.product_tnorm(input[2],input[4])
            r9=self.product_tnorm(input[2],input[5])

            toret=[r1,r2,r3,r4,r5,r6,r7,r8,r9]
        
        return toret
       

    def normalization_layer(self,input):

        """
        Capa de normalizacion de los valores de entrada

        Argumentos:
            - input: array de entrada

        Return:
            - output: array de valores de entrada normalizados
        
        """
        s=np.sum(input)
        if s != 0:
            output=input/np.sum(input)
        else:
            output=input

        return output
    

    def fit(self, learning_rate=0.01,epochs=25):

        """
        Funcion de entrenamiento de la red

        Argumentos:
            - learning_Rate: coeficiente de aprendizaje de la red
            - epochs: numero de repeticiones al conjunto de entrenamiento
        
        """

        #fuzzyfication del conjunto de entrenamiento
        self.fuzzyfication()

        training_size = self.fuzz_X.shape[0]
        y_calculada = np.zeros(training_size)
        
        for iteration in range(epochs):
            #array de salidas que se van a calcular
            y_calculada = np.zeros(training_size)
            

            for i in range(training_size):
                #para cada registro del conjunto de entrenamiento
                # input -> fuzzy
                x_i = self.fuzz_X[i] 
                # se pasas el registro de valores fuzzyficados por el pipeline de la red y se obtiene la predicción
                # fuzzy -> neural net   
                y_calculada[i]=self.nn(x_i)

                # se calcula el error con la variable de salida de referencia
                error = y_calculada[i] - self.y[i]
                
                gradients = self.layer_3_output

                #se actualizan los pesos de la red
                self.weigths = self.weigths - learning_rate * error * gradients
            #se calcula le r2 score tras cada iteración
            self.r2=r2_score(self.y,y_calculada)
            print(f'ITERATION {iteration} : #####  r2 {self.r2}')
            
        #invoca funcion que genera las consecuencias de las reglas
        self.rules_consecuences()

        
    def nn(self,input):
        """
        Funcion que actua como pipeline de la red, recibe un array de valores fuzzy y atraviesa toda la red para devolver el valor 
        esperado

        Argumentos:
            - input: array de valores fuzzyficados de las variables de entrada

        Return:
            - output: prediccion sobre la variable de salida de la red
        
        """
        #Multivarite memebership function layer
        self.layer_2_output=self.multivariate_memb(input)
        #Normalization Layer
        self.layer_3_output=self.normalization_layer(self.layer_2_output)   
        #Activation Layer
        self.layer_4_output = self.calculate_output(self.layer_3_output, self.weigths)
    
        return self.layer_4_output


    def calculate_output(self,x, weights):
        """
        Funcion de activación de la red que consiste en el producto mas sumatorio de cada entrada a la neurona por los pesos de la misma
        
        """
        y = np.dot(x, weights)
        return y
    
    def min_tnorm(self,a, b):
        """
            Funcion minimo
        """
        return np.minimum(a, b)
    
    def product_tnorm(self,a, b):
        """
            Funcion T-Norm
        """
        return np.multiply(a, b)

    def rules_consecuences(self):
        i=0
        for weight in self.weigths:
            confs=[]
            for j in range(self.n_membership_output):
                conf=fuzz.interp_membership(x=self.consecuence.universe,xmf=self.consecuence[self.NAMES(self.n_membership_output)[j]].mf,xx=weight)
                confs.append(conf)

            #confHigh=fuzz.interp_membership(x=self.consecuence.universe,xmf=self.consecuence['High'].mf,xx=weight)
            #confLow=fuzz.interp_membership(x=self.consecuence.universe,xmf=self.consecuence['Low'].mf,xx=weight)
            #actual=actual+" "+self.y_name+" is HIGH ("+str(round(confHigh,2))+") and LOW ("+str(round(confLow,2))+")"
            actual=self.rules[i]
            for j in range(self.n_membership_output):
                actual=actual+" "+self.y_name+" is "+self.NAMES(self.n_membership_output)[j]+" ("+str(round(confs[j],2))+")"
            
            self.rules[i]=actual
            i+=1
            

    def predict(self,input):

        """
        Funcion para predecir un registro una vez esta entrenada

        Argumentos:
            - input: valores de variables de entrada
        Return:
            -output: valor de y esperado
        """
        if self.trained:
            input_fuzzy=self.to_fuzzy(input)
    
            return self.nn(input_fuzzy.values[0])
        
        else:
            return None
        
    def get_weigths(self):
        """
        Funcion para ver los pesos de la red
        """
        return self.weigths
    
    def get_rules(self):
        """
        Funcion para ver las reglas generadas
        """
        return self.rules 

    def plot_membership_functions(self):
        """
        Funcion para ver las graficas de las funciones de membresia de los antecedentes
        """
        for ant in self.antecedents:
            ant.view()
            


data=pd.read_csv("C:/Users/USUARIO/Desktop/TFM/project/invitro_g.csv",sep=",")
print(data.describe())
"""
X=data[['PolymerA']]
y=data[['8hr']]

model=NeuroFuzzy(input=X.values,output=y.values,n_membership_input=3,n_membership_output=3,output_name="8hr",input_names=["PolymerA"])
model.fit(learning_rate=0.01,epochs=50)
for rule in model.get_rules():
    print(rule)
print(model.predict([33.0,5.0]))
"""

