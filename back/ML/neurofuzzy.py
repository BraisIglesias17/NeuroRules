""" Module for neurofuzzy """
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from sklearn.metrics import r2_score,mean_squared_error

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
    

    def __init__(self,input,input_names,output,output_name,n_membership_input,n_membership_output,types,memebership_function="default"):
        
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
        
        
        if self.n_variables!=len(input_names):
            raise ValueError("Inconsistent number of variables and names")
        
        if n_membership_output>4 or n_membership_output<1:
            raise ValueError("Invalid number of output memberships (0 > output memberships < 5)")
        
        if n_membership_input>4 or n_membership_input<1:
            raise ValueError("Invalid number of input memberships (0 > input memberships < 5)")

        self.n_membership=n_membership_input
        self.n_membership_output=n_membership_output
        self.trained=False

        self.memb_func=memebership_function
        self.X_names=input_names
        self.X=input
        self.y=output
        self.y_name=output_name
        self.nominal_variables=[]
        self.types=types
        
        #variable que contendrá la matriz de valores fuzzificados
        self.fuzz_X=None

        #array de pesos de cada regla
        # el numero de reglas se determina por el numero de funciones de membresia de entrada elevada al numero de variables
        self.weigths=np.random.rand(self.n_membership**self.n_variables)
        #self.weigths=np.full(self.n_membership**self.n_variables,fill_value=np.mean(self.y))
        #self.weigths=np.ones(self.n_membership**self.n_variables)
        #self.weigths=np.zeros(self.n_membership**self.n_variables)
        #self.weigths=np.random.normal(0,1,self.n_membership**self.n_variables)
        #print(f'initial weights: {self.weigths}')

        self.historic_weigths=None
        self.historic_error=None
        self.historic_r2=None
        #lista que contendrá las reglas
        self.rules=[]

        #lista de objetos Antecedent de skfuzzy (uno por cada variable de entrada)
        self.antecedents=[]
        
        for i in range(0,len(input_names),1):
            
            if not 'object' in str(self.types[i]):    
                self.antecedents.append(ctrl.Antecedent(np.array(np.sort(input[:,i]),dtype=np.float64),input_names[i]))
                
            else:
                self.antecedents.append(ctrl.Antecedent([0,1],input_names[i]))
                self.nominal_variables.append(i)
            
        self.mebm_info={}
        i=0
        self.n_rules=1
        for name in input_names:
            
            if not i in self.nominal_variables:
                self.mebm_info[name]=n_membership_input
                self.n_rules=self.n_rules*n_membership_input
            else:
                val=len(np.unique(input[:,i]))
                self.mebm_info[name]=val
                self.n_rules=self.n_rules*val
            i+=1

        
        #objeto Consequence de skfuzzy para la variable target
        self.consecuence=ctrl.Consequent(np.sort(output.flatten()),output_name)

        
        #generación de las funciones de membresía con skfuzzy
        self.consecuence.automf(n_membership_output,names=self.NAMES(self.n_membership_output))
    
        #variables utilizadas para almacenar la salida de la red en cada etapa
        self.layer_1_output=None
        self.layer_2_output=None
        self.layer_3_output=None
        self.layer_4_output=None

        self.metrics={'r2':0.0,'rmse':0.0,'mse':0.0}
        
        self.done=False
        
    def fuzzyfication(self,C=0.3):
        """
        Funcion utilziada para generar los valores difusos para cada variable en cada membresía y las almacena en la 
        variable de clase fuzz_X

        Argumento: coeficiente C (NO USADO)

        Return: DataFrame de los valores difusos.
        """
       

        X=self.X
        toret=pd.DataFrame()
        n_cols = X.shape[1]
            
        # Recorrer la matriz por columnas
        for i in range(n_cols):
            col = X[:, i]
            
                
            if not i in self.nominal_variables:
                
                
                #Utilizacion de la funcion automf con el numero de membresias de entrada para generar las membresías
                self.antecedents[i].automf(self.n_membership,names=self.NAMES(self.n_membership))
                
                #lista que almacena las funciones de membresía (NO USADA)
                mfs=[]
                    
                for j in range(self.n_membership):
                    col=np.array(col,dtype=np.float64)

                    mf=fuzz.interp_membership(x=self.antecedents[i].universe,xmf=self.antecedents[i][self.NAMES(self.n_membership)[j]].mf,xx=col)
                         
                    tmp=pd.DataFrame(mf,columns=[self.X_names[i]+'_'+str(self.NAMES(self.n_membership)[j])])
                    mfs.append(mf)
                    toret=pd.concat([toret,tmp],axis=1)
            else:
                name=self.X_names[i]
                data=self.X[:,i]
                values=np.unique(data)
                for value in values:
                    col_name=name+"_"+value
                    vals=[1.0 if num==value else 0.0 for num in data]
                    tmp=pd.DataFrame(vals,columns=[col_name])
                    toret=pd.concat([toret,tmp],axis=1)

        self.fuzz_X=toret.values

        return toret
        
    def get_scores(self,X,y):
        y_pred=self.predict(X)
        r2=r2_score(y,y_pred)
        max=np.max(y)
        min=np.min(y)
        
        #normalize mean squared error
        mse=mean_squared_error(y,y_pred)/(max-min)

        rmse=np.sqrt(mse)

        return {'r2':r2,'mse':mse,'rmse':rmse}
    
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
            
            
            for j in range(self.n_membership):
                universe=ant.universe
                mf=fuzz.interp_membership(x=ant.universe,xmf=ant[self.NAMES(self.n_membership)[j]].mf,xx=input[i])

              
                if (self.NAMES(self.n_membership)[j]=="Low" and input[i] < np.min(universe)) or (self.NAMES(self.n_membership)[j]=="High" and input[i] > np.max(universe)):
                    mf=1.0
                
                tmp=pd.DataFrame([mf],columns=[self.X_names[i]+'_'+str(self.NAMES(self.n_membership)[j])])
               
                toret=pd.concat([toret,tmp],axis=1)
            
            i+=1
       
        return toret

    def multivariate_memb(self,input):

        """
        Capa de la red cuyo objetivo es generar los valores de multivariable aplicando a los valores difusos de entrda una operación T NORMA

        Argumentos:
            - input: array de valores de entrada de la red fuzzyficadas (salida de la funcion to_fuzzy) 
            
        Return:
            - output: array de valores difussos de funcion multivariable 
        
        """
        # toret=None
        # size=self.n_membership*self.X.shape[1]
        
        start=0
        end=0
        arrays=[]
        n_rules=1
        for value in self.mebm_info:
            n_rules=n_rules*self.mebm_info[value]
            end=end+self.mebm_info[value]
            mf=input[start:end]
            arrays.append(mf)
            start=end

        #result=np.zeros((1,n_rules),dtype=np.float64)
        i=0
        previous=None
        currentProduct=input
        for array in arrays:
            if i!=0:
                currentProduct=previous.reshape(previous.shape[0],1).dot(array.reshape(1,array.shape[0]))
            previous=array
            i+=1
       
        
        """
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

            # TO DO
            next_variable=0
            rules=[]
            textRules=[]
            shift=self.mebm_info[self.X_names[0]]
            for i in range(0,self.mebm_info[self.X_names[0]]):
                
                next_variable=1
                for j in range(0,self.mebm_info[self.X_names[next_variable]]):
                    rules.append(self.multivariate_operation(input[i],input[j+shift]))
                    standard=self.NAMES(shift)[i]
                
                    textRules.append("IF "+self.X_names[next_variable-1]+" is ")

                    

            #print(rules)    
            #print(self.mebm_info[self.X_names[next_variable]])
            #si es la primera iteracion se crean las reglas
            if len(self.rules)==0:
                self.rules.append("IF "+self.X_names[0]+" is LOW AND "+self.X_names[1]+" is LOW THEN")
                self.rules.append("IF "+self.X_names[0]+" is LOW AND "+self.X_names[1]+" is HIGH THEN")
                self.rules.append("IF "+self.X_names[0]+" is HIGH AND "+self.X_names[1]+" is LOW THEN")
                self.rules.append("IF "+self.X_names[0]+" is HIGH AND "+self.X_names[1]+" is HIGH THEN")

            
            r1=self.multivariate_operation(input[0],input[2])
            r2=self.multivariate_operation(input[0],input[3])
            r3=self.multivariate_operation(input[1],input[2])         
            r4=self.multivariate_operation(input[1],input[3])

            
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
            r1=self.multivariate_operation(input[0],input[3])
            r2=self.multivariate_operation(input[0],input[4])
            r3=self.multivariate_operation(input[0],input[5])
            r4=self.multivariate_operation(input[1],input[3])
            r5=self.multivariate_operation(input[1],input[4])
            r6=self.multivariate_operation(input[1],input[5])
            r7=self.multivariate_operation(input[2],input[3])
            r8=self.multivariate_operation(input[2],input[4])
            r9=self.multivariate_operation(input[2],input[5])

            toret=[r1,r2,r3,r4,r5,r6,r7,r8,r9]
        """
        if len(self.rules)==0:
            self._create_rules_template()
        
        #print(f"REAL: {(toret)}")
        #return np.array(toret)
        
        return (currentProduct.reshape(1,-1)[0])

    def _create_rules_template(self):
        rules=[]
        conditions={}
        for variable in self.mebm_info:
            conditions[variable]=[]
            for i in range(self.mebm_info[variable]):
                rule=variable+" is "+self.NAMES(self.mebm_info[variable])[i]
                conditions[variable].append(rule)

        i=0
        for element in conditions:    
           rules=self._get_combinations(conditions[element],rules)
        
        
        self.rules=rules
            
    def _get_combinations(self,list1,list2):
        toret=[]
        if len(list1)==0:
            return list2
        elif len(list2)==0:
            return list1
        
        for i in range(len(list1)):
            for j in range(len(list2)):
                toret.append(list1[i]+" AND "+list2[j])
    
        return toret
    
    def multivariate_operation(self, a, b):
        return self.product_tnorm(a,b) 

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
        
        batch=int(np.ceil(training_size/2))
        god=False
        iterations=epochs*int(np.ceil((training_size/batch)))

        if training_size%batch==0:
            god=True

        
        self.historic_weigths=np.zeros(shape=(iterations,self.n_membership**self.n_variables))
        self.historic_error=np.zeros(shape=(epochs,1))
        self.historic_r2=np.zeros(shape=(epochs,1))

        M=np.zeros(shape=(batch,self.n_membership**self.n_variables))

        counter=0
        first=True
    
        gradient=None
        d=None
        first=True
        iteration=0
        for epoch in range(epochs):
           
            #array de salidas que se van a calcular
            y_calculada = np.zeros(training_size)
            
            end_batch=0
            i_batch=0
            start_batch=0

            for i in range(training_size):
                if i_batch==0:
                    start_batch=i

                x_i = self.fuzz_X[i]   
                y_calculada[i]=self.nn(x_i)
                
                #print(f'calculada:{y_calculada[i]}, real:{self.y[i]}')
                M[i_batch]=np.array(self.layer_3_output).reshape(1,self.layer_3_output.shape[0])

                # se calcula el error con la variable de salida de referencia
                if i_batch==batch-1 or (i==training_size-1):
                    
                    self.historic_weigths[counter]=self.weigths
                    
                    counter+=1

                    if i==training_size-1:
                        i+=1
                    end_batch=i
                    i_batch=0
                    
                    w0=self.weigths.reshape(self.weigths.shape[0],1)
                    
                    y=self.y[start_batch:end_batch+1]

                    result=self.conjugate_gradient(M,y,w0,d=d,gradient=gradient,first=first,learning_rate=learning_rate)
                    self.weigths=result[0].flatten()
                    d=result[1]
                    gradient=result[2]
                    iteration+=1
                    

                else:
                    i_batch+=1

                self.metrics['r2']=r2_score(self.y,y_calculada)
                mse=mean_squared_error(self.y,y_calculada)
                self.metrics['mse']=mse
                self.metrics['rmse']=np.sqrt(mse)
                self.historic_error[epoch]=mse
                self.historic_r2[epoch]=self.metrics['r2']
            
            if self.done:
                break
            #print(f'ITERATION {iteration} : ###  r2 {self.metrics["r2"]}, mse {self.metrics["mse"]}, rmse {self.metrics["rmse"]}')
            
        #invoca funcion que genera las consecuencias de las reglas
        self.rules_consecuences()
        self.trained=True

    def calculate_gradient_mse(self,M,w,y):
        
        """
        Funcion que calcula la derivada de la funcion de coste (MSE) que se utiliza como gradiente

        argumentos:
            - M : matriz de multivariate memberships
            - w : pesos a optimizar
            - y : salida real

        return
            - gradient: gradiente de la funcion de costo
        """
        if M.shape[0]!=y.shape[0]:
            M=M[0:y.shape[0]]
            
        n=M.shape[0]
        grandient=np.zeros(shape=(n,w.shape[0]))
        i=0
        
        for register in M:
            j=0
            weighted_sum=np.dot(register,w)
            
            for rule in register:
                grandient[i][j]=(rule*(weighted_sum-y[i]))
                j+=1
                       
            i+=1
        toret=np.zeros(shape=(w.shape[0],1))

        for i in range(w.shape[0]):
            partial_derivate=grandient[:,i]
            partial_derivate=2*np.sum(partial_derivate)/n
            toret[i]=partial_derivate
            
        return toret
    
    def conjugate_gradient(self,A,y,w0,tol=1.e-10,itmax=50,d=None,gradient=None,first=True,learning_rate=0.001):
        """
        Implementación del algoritmo de descenso de gradiente conjugado

        argumentos:
            - A : matriz de multivariate memberships
            - w0 : pesos iniciales
            - y : salida real

        return
            - wi : pesos actualizados
            - d : direccion de gradiente
            - gradient: gradiente de la funcion de costo
            - norma: última norma calculada
        """
        
        """
        A_t=np.transpose(A)
        M=np.dot(A_t,A)
        y=np.dot(A_t,y)
        """
        if first:
            gradient=self.calculate_gradient_mse(A,w0,y)
            d=np.dot(gradient,np.float16(-1))
        else:
            d=d
            gradient=gradient
    
        norma=0.0
        wi=w0
            
        for i in range(0,itmax):
            alpha=learning_rate
            wi=wi+alpha*d
           
            old_gradient=gradient
            gradient=self.calculate_gradient_mse(A,wi,y)
            norma=np.linalg.norm(gradient)
        
            if norma <= tol: 
                   
                break
            beta=np.dot(np.transpose(gradient),gradient)/np.dot(np.transpose(old_gradient),old_gradient)
            
            #beta=1
            d=np.float16(-1)*gradient+(beta*d)
           
        return wi,d,gradient,norma

    def get_predictions_on_train(self):
        predictions=np.zeros((self.X.shape[0],1))
    
        for i in range(self.X.shape[0]):
            row=self.X[i,:]
            output=self.predict(row.reshape(1,-1))
            predictions[i]=output
           
        self.y_pred=predictions

        return predictions

    def plot_trend(self):
        if self.n_variables==1 and self.trained:
            
            var=self.X[:,0]
            fig, ax = plt.subplots()
            x=np.linspace(start=np.min(var),stop=np.max(var),num=100)
            y_calculada=np.zeros(x.shape[0])
            
            i=0
            for register in x:
                y_calculada[i]=self.predict([register])
                i+=1

            ax.plot(x, y_calculada,label="Calculated value")
            ax.set_xlabel(self.X_names[0])
            ax.set_ylabel(self.y_name)
            ax.set_title('Trend')

            ax.legend()

            plt.show()
                  
    def plot_precisewise(self):
        
        y_calculada=np.zeros(self.X.shape[0])
        i=0
        plt.figure("precisewise line")
        fig, ax = plt.subplots()
        for variable in self.X_names:
            j=0
            #ordeno por la columna
            X=self.X
            
            reshaped_y=self.y.reshape(self.y.shape[0],1)
            X=np.append(X,reshaped_y,axis=1)
            X=X[X[:,i].argsort()]
            y_real=X[:,X.shape[1]-1]
            X=np.delete(X,X.shape[1]-1,1)
            for register in X:
                y_calculada[j]=self.predict(register)
                j+=1
            x=X[:,i]
            
            ax.plot(x, y_calculada,label="salida calculada")
            ax.plot(x, y_real, label="salida real")
            ax.set_xlabel(variable)
            i+=1
            ax.set_ylabel(self.y_name)
            
        ax.set_title('Training outputs')
        ax.legend()
        plt.show()

    def plot_r2_evolution(self):
        r2=self.historic_r2
        x=np.arange(r2.shape[0])
        fig, ax = plt.subplots()
        ax.plot(x,r2,label="R2")
        ax.set_ylim(top=1.0)
        ax.set_xlabel('Iterations')
        ax.set_ylabel('Metrics')
        ax.set_title('Evolution')
        ax.legend()
        plt.show()

    def plot_historic_error(self):
        rmse=self.historic_error
        x=np.arange(rmse.shape[0])
        fig, ax = plt.subplots()
        ax.plot(x, rmse, label="Mean squared error")
        ax.set_xlabel('Iterations')
        ax.set_ylim(bottom=0.0)
        ax.set_ylabel('Metrics')
        ax.set_title('Evolution')
        ax.legend()
        plt.show()

    def plot_historic_weight(self):
        
        vars=[]
        for i in range(0,self.historic_weigths.shape[1]):
            vars.append(self.historic_weigths[:,i])

        x=np.arange(self.historic_weigths.shape[0])
        fig, ax = plt.subplots()
        m=0
        for var in vars:
            
            ax.plot(x, var, label=str('w'+str(m)))
            m+=1
        
        ax.set_xlabel('Iterations')
        ax.set_ylabel('Weight value')
        ax.set_title('Weigth learning')
        ax.legend()
        plt.show()
        
    def nn(self,input):
        """
        Funcion que actua como pipeline de la red, recibe un array de valores fuzzy y atraviesa toda la red para devolver el valor 
        esperado

        Argumentos:
            - input: array de valores fuzzyficados de las variables de entrada

        Return:
            - output: prediccion sobre la variable de salida de la red
        
        """
        #print(f'################################')
        #Multivarite memebership function layer
        #print(f'Input Multifunction:{input}')
        self.layer_2_output=self.multivariate_memb(input)
        #Normalization Layer
        self.layer_3_output=self.normalization_layer(self.layer_2_output) 
        #self.layer_3_output=self.layer_2_output  
        #Activation Layer
        #print(f'Input Activation layer:{self.layer_3_output}')
        self.layer_4_output = self.calculate_output(self.layer_3_output, self.weigths)
        #print(f'Output:{self.layer_4_output}')
        #print(f'################################')
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
                
            
                conf=fuzz.interp_membership(x=np.array(self.consecuence.universe,dtype=np.float64),xmf=self.consecuence[self.NAMES(self.n_membership_output)[j]].mf,xx=weight)
                if (self.NAMES(self.n_membership_output)[j]=="Low" and weight < np.min(self.consecuence.universe)) or (self.NAMES(self.n_membership_output)[j]=="High" and weight > np.max(self.consecuence.universe)) :
                    conf=1.0

                confs.append(conf)
            
            actual=self.rules[i]
            for j in range(self.n_membership_output):
                
                actual=actual+" THEN "+self.y_name+" is "+self.NAMES(self.n_membership_output)[j]+" ("+str(round(confs[j],2))+")"
            
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
        
        rows=input.shape[0]
        cols=input.shape[1]
        toret=[]
        
        if self.trained and cols==self.n_variables:
            for row in range(rows):
                data=input[row,:]
                input_fuzzy=self.to_fuzzy(data)
                output=self.nn(input_fuzzy.values[0])
                toret.append(output)
            return toret
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

        self.consecuence.view()







