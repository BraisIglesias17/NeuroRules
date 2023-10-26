import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error,r2_score
from neurofuzzy import NeuroFuzzy
import numpy as np
from scipy.stats import chi2,pearsonr,wilcoxon,shapiro,kruskal,kstest,t,f_oneway,mannwhitneyu

"""
example_high=np.arange(51,103)
example_low=np.arange(start=206,stop=154,step=-1)
example_nominal=["si" if num %2 ==0 else "no" for  num in example_high]
example_binary=[0 if num %2 !=0 else 1 for  num in example_high]
example_nominal[2]="ah"
df=pd.DataFrame({'x':example_high,'y':example_low,'nominal':example_nominal,'z':example_high,'binary':example_binary})

data=pd.read_csv("C:/Users/USUARIO/Downloads/p.csv",sep=",")
data=df
"""
data=pd.read_csv("C:/Users/USUARIO/Desktop/TFM/project/invitro_g.csv",sep=",")

print(f"row: {data[['%moisture','PolymerB','lubricant','8hr']].values[3,:]}")
#data=data[0:4]


y_variable='8hr'
y=data[y_variable].values

#scaler=MinMaxScaler(feature_range=(-1,1))
#y=scaler.fit_transform(np.array(y).reshape(-1,1))

print(" -------- CORRELATIONS ----------")

for col in data.columns:
    if col!=y_variable:
        p=(pearsonr(data[col].values,y).pvalue)
        if p<0.1:
            print(f' {col}')



#x_names=['% Tween','% RFB']
#y_variable='SIZE (nm)'
x_names=['PolymerA','%moisture']
X=(data[x_names])
types=data[x_names].dtypes



submodel1=NeuroFuzzy(input=X.values,types=types,output=y,n_membership_input=3,n_membership_output=2,output_name=y_variable,input_names=x_names)
submodel1.fit()
outputs1=submodel1.get_predictions_on_train()

x_names=['PolymerB','lubricant']
X=(data[x_names])
types=data[x_names].dtypes
submodel2=NeuroFuzzy(input=X.values,types=types,output=y,n_membership_input=3,n_membership_output=2,output_name=y_variable,input_names=x_names)
submodel2.fit()
outputs2=submodel2.get_predictions_on_train()


#p2=submodel2.predict(np.array([[19.2,2.8]]))[0]
#p1=submodel1.predict(np.array([[3.85]]))[0]

output=np.zeros((outputs1.shape[0],2))
ensemble=np.zeros((outputs1.shape[0],1))
for i in range(outputs1.shape[0]):
    output[i][0]=outputs1[i]
    output[i][1]=outputs2[i]
    ensemble[i]=(outputs1[i]+outputs2[i])/2


lr=LinearRegression()
lr.fit(output,y)

print(lr.score(output,y))

#print(f"submodel2 output:{p2}")
#print(f"submodel1 output:{p1}")
#print(f"COMBINED OUTPUT: {output}")
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch
from torch.utils.data import DataLoader, Dataset,TensorDataset

batch_size = 12
shuffle = True



# Datos de entrada (4 valores)
X = torch.from_numpy(output).clone().detach().to(torch.float32)
X.requires_grad_(True)


# Valor de salida deseado
y_true = torch.tensor(y, dtype=torch.float32,requires_grad=False)
y_true = y_true.view(-1, 1)

data_set=TensorDataset(X,y_true)
data_loader = DataLoader(data_set, batch_size=batch_size, shuffle=shuffle)

class Neuron(nn.Module):
    def __init__(self):
        super(Neuron, self).__init__()
        self.linear = nn.Linear(2, 1)  # Una neurona con 2 entradas y 1 salida

    def forward(self, x):
        return self.linear(x)
    
model = Neuron()

optimizer = optim.SGD(model.parameters(), lr=0.01)  # Optimizador de descenso de gradiente estocástico
criterion = nn.MSELoss()  # Error cuadrático medio como función de pérdida


num_epochs =4  # Número de épocas de entrenamiento

model.train()
for epoch in range(num_epochs):
    
    for batch in enumerate(data_loader,0):
        inputs = batch[1][0]
        outputs=batch[1][1]
        
        optimizer.zero_grad()
        y_pred = model(inputs)    
    
        loss = criterion(y_pred, outputs)
        
        loss.backward()
        optimizer.step()
        
    

# Imprime los pesos optimizados
print("Pesos optimizados:")
print("Pesos:", model.linear.weight.data)
#print("Bias:", model.linear.bias.data)

# Coloca el modelo en modo de evaluación
model.eval()

# Realiza la predicción
with torch.no_grad():
    prediction = model(torch.tensor([[69.94,65.3]], dtype=torch.float32))

# Imprime la predicción
print("Predicción:", prediction.item())
"""


#print(r2_score(ensemble.flatten(),y))
#print(model.get_weigths())

#for rule in model.get_rules():
#    print(rule)


#model.plot_trend()
#model.plot_membership_functions()
#model.plot_r2_evolution()
#model.plot_historic_error()
#model.plot_historic_weight()
#model.plot_precisewise()
#print(model.metrics)
#print(model.predict([70]))
