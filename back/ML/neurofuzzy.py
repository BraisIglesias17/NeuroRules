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

    def NAMES(self,number):
        if number == 2:
            return ['Low','High']
        elif number == 3:
            return ['Low','Medium','High']
        elif number ==4:
            return['Low','Medium_1','Medium_2','High']    
    
    def __init__(self,input,input_names,output,output_name,n_membership_input,n_membership_output,memebership_function="default"):
        
        self.n_variables=input.shape[1]
        self.n_membership=n_membership_input
        self.n_membership_output=n_membership_output


        self.memb_func=memebership_function
        self.X_names=input_names
        self.X=input
        self.y=output
        self.y_name=output_name
        self.fuzz_X=None
        self.weigths=np.zeros(self.n_membership**self.n_variables)

        self.rules=[]
        self.antecedents=[]
        for i in range(0,len(input_names),1):
            self.antecedents.append(ctrl.Antecedent(np.sort(input[:,i]),input_names[i]))
        
        
        self.consecuence=ctrl.Consequent(np.sort(output.flatten()),output_name)
      
        self.consecuence.automf(n_membership_output,names=self.NAMES(self.n_membership_output))
    
        
        
        self.layer_1_output=None
        self.layer_2_output=None
        self.layer_3_output=None
        self.layer_4_output=None

        self.r2=0.0
        
        
    def fuzzyfication(self,C=0.3):
        try:

            X=self.X
            toret=pd.DataFrame()
            clusters=[]
            n_cols = X.shape[1]
    
            # Recorrer la matriz por columnas
            for i in range(n_cols):
                col = X[:, i]
            
                col=np.sort(col)
                control_points=min(col),np.percentile(col,30),np.mean(col),np.percentile(col,60),max(col)
                
                self.antecedents[i].automf(self.n_membership,names=self.NAMES(self.n_membership))

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
        
        toret=pd.DataFrame()
        i=0
        for ant in self.antecedents:   
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
        toret=None
        size=self.n_membership*self.X.shape[1]
        
        if self.n_variables == 1:
            #Combinaciones para una variable variables dos membresias
            r=[]
            length=len(self.rules)
            for i in range(self.n_membership):
                r.append(input[i])
                if length==0:
                    self.rules.append("IF "+self.X_names[0]+" is "+self.NAMES(self.n_membership)[i]+" THEN")
            toret=r
        elif self.n_variables==2 and self.n_membership==2:
            
            if len(self.rules)==0:
                self.rules.append("IF "+self.X_names[0]+" is LOW AND "+self.X_names[1]+" is LOW THEN")
                self.rules.append("IF "+self.X_names[0]+" is LOW AND "+self.X_names[1]+" is HIGH THEN")
                self.rules.append("IF "+self.X_names[0]+" is HIGH AND "+self.X_names[1]+" is LOW THEN")
                self.rules.append("IF "+self.X_names[0]+" is HIGH AND "+self.X_names[1]+" is HIGH THEN")

            #Combinaciones para dos variables dos membresias
            r1=self.product_tnorm(input[0],input[2])
            r2=self.product_tnorm(input[0],input[3])
            r3=self.product_tnorm(input[1],input[2])         
            r4=self.product_tnorm(input[1],input[3])

            toret=[r1,r2,r3,r4]

        elif self.n_variables==2 and self.n_membership == 3:
        
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
        s=np.sum(input)
        if s != 0:
            output=input/np.sum(input)
        else:
            output=input

        return output
    
    def fit(self, learning_rate=0.01,epochs=25):
        self.fuzzyfication()
        training_size = self.fuzz_X.shape[0]
        y_calculada = np.zeros(training_size)
        

        for iteration in range(epochs):
            y_calculada = np.zeros(training_size)
            
            for i in range(training_size):
            
                x_i = self.fuzz_X[i]    
                y_calculada[i]=self.nn(x_i)
                error = y_calculada[i] - self.y[i]
                
                gradients = self.layer_3_output
                self.weigths = self.weigths - learning_rate * error * gradients
            self.r2=r2_score(self.y,y_calculada)
            
        self.rules_consecuences()

        
    def nn(self,input):
       
        self.layer_2_output=self.multivariate_memb(input)
        #Normalization Layer
        
        self.layer_3_output=self.normalization_layer(self.layer_2_output)   
        #Activation Layer
        
        self.layer_4_output = self.calculate_output(self.layer_3_output, self.weigths)
    
        return self.layer_4_output


    def calculate_output(self,x, weights):
        y = np.dot(x, weights)
        return y
    
    def min_tnorm(self,a, b):
        return np.minimum(a, b)
    
    def product_tnorm(self,a, b):
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
        input_fuzzy=self.to_fuzzy(input)
    
        return self.nn(input_fuzzy.values[0])
        
    def get_weigths(self):
        return self.weigths
    
    def get_rules(self):
        return self.rules 

    def plot_membership_functions(self):
        for ant in self.antecedents:
            ant.view()
            
    """
    
    def optimization(self,epochs=25):
        training_size = self.fuzz_X.shape[0]
        
        y_calculada = np.zeros(training_size)

        for m in range(0,epochs):

            for i in range(0,training_size):
                x_i = self.fuzz_X[i]
                    
                mFM=self.multivariate_memb(x_i)
                mFM=self.normalization_layer(mFM)                
                #error = y_calculada[i] - self.y[i]
                #y_calculada[i] = self.calculate_output(mFM, self.weigths)
                
                self.current_X=(mFM)
                self.current_y=(self.y[i])
                
                resultado = minimize(self.calculate_output_to_optimize,self.weigths, method='CG')
                self.weigths=resultado['x']  
            
        self.rules_consecuences()
        
        
    def gradient_descent(self,learning_rate=0.01,epochs=25):
        training_size = self.fuzz_X.shape[0]
        loss=[]
        y_calculada = np.zeros(training_size)
         
        for iteration in range(epochs):
            y_calculada = np.zeros(training_size)  # Inicializar la salida calculada

            for i in range(training_size):
                #print("--------------------------------------------------")
                x_i = self.fuzz_X[i]
                #print(f'OUTPUT OF FUZZY LAYER:{x_i}')
                mFM=self.multivariate_memb(x_i)
                mFM=self.normalization_layer(mFM)
                
                y_calculada[i] = self.calculate_output(mFM, self.weigths)
                #print(f'DESEADA: {self.y[i]} , calculada :{y_calculada[i]}')
                error = y_calculada[i] - self.y[i]
                gradients = mFM
                self.weigths = self.weigths - learning_rate * error * gradients
        
        self.rules_consecuences()
    """    


"""
data=pd.read_csv("invitro_g.txt",sep="\t")
print(data.describe())

X=data[['PolymerA']]
y=data[['8hr']]

model=NeuroFuzzy(input=X.values,output=y.values,n_membership_input=3,n_membership_output=3,output_name="8hr",input_names=["PolymerA"])
model.fit(learning_rate=0.01,epochs=50)
for rule in model.get_rules():
    print(rule)
print(model.predict([33.0,5.0]))
"""

