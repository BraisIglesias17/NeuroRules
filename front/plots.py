import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import seaborn as sns
from sklearn import linear_model
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

def plot_2d(data,options):
    x=data['x']['data']
    y_left=data['y']['data']
    y_right=data['y_right']['data']
    fig, ax1 = plt.subplots()

    if data['y']['name']!="":
        color = 'tab:blue'
        ax1.set_xlabel(data['x']['name'])
        ax1.set_ylabel(data['y']['name'], color=color)
        ax1.scatter(x, y_left, color=color,marker='o')
        ax1.tick_params(axis='y', labelcolor=color)

    
    ax2 = ax1.twinx()
    if data['y_right']['name']!="":
        color = 'tab:red'
        ax2.set_ylabel(data['y_right']['name'], color=color)
        ax2.scatter(x, y_right, color=color,marker='v')
        ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    plt.show()

def plot_3d(data,options):
    x=data['x']['data']
    y=data['y']['data']
    z=data['z']['data']
    #x, y = np.meshgrid(x, y)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    #ax.scatter(x, y, z, c='blue', marker='o', label='Datos')

    # Crear el gráfico de superficie
    surf = ax.plot_trisurf(x, y, z, cmap='plasma')

    fig.colorbar(surf)
    ax.set_title('3D mesh graph')
    ax.set_xlabel(data['x']['name'])
    ax.set_ylabel(data['y']['name'])
    ax.set_zlabel(data['z']['name'])
    #ax.legend()
    
    plt.show()

def plot_countplot(nominal):
    sns.set_theme(style="whitegrid")
    plot=sns.countplot(x=nominal)
    
    for p in plot.patches:
        plot.annotate('{:}'.format(p.get_height()), (p.get_x()+0.33, p.get_height()+0.1))
        
   
    plt.show()

def plot_hist(data,option):
    x=data['x']['data']
    plt.figure(figsize=(8, 6))
    plt.hist(x, bins=option['bins'], color='blue', alpha=0.7,edgecolor="black")
    plt.title('Histogram')
    plt.xlabel(data['x']['name'])
    plt.ylabel('Frequency')
    #plt.grid(True)
    plt.show()


def plot_boxplot(data,option):
    x=data['x']['data']
    """
    plt.boxplot(x)
    plt.title(str(data['x']['name']+" boxplot"))
    """
    sns.boxplot(data=x, orient="v")
    plt.show()

def plot_regression(data,options):
    x=np.array(data['x']['data'])
    y=np.array(data['y']['data'])

    x=x.reshape(-1,1)
    
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
    
    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, label='Data points', color='blue')
    plt.title('Regression Fit Line')
    plt.xlabel(data['x']['name'])
    plt.ylabel(data['y']['name'])
    plt.grid(True)
    regression=linear_model.LinearRegression()
   
    regression.fit(X_train,y_train)
    fit_line=regression.predict(X_test)

    R2=r2_score(X_test,fit_line)

    plt.annotate('R2 = (%.2f)'%(R2), xy=(sum(x)/len(x),max(y)-5),xytext =(0,20),textcoords ='offset points',fontsize=13,ha='center')

    plt.plot(X_test,fit_line, color='red')
    plt.legend()
    plt.show()

def plot_correlation_matrix(dataFrame):
    valid_columns=dataFrame.select_dtypes(include=['number']).columns

    X=dataFrame[valid_columns].corr()

    plt.figure("Correlation matrix",figsize=(8, 6))
    sns.heatmap(X, annot=True, cmap='coolwarm', center=0)
    plt.title("Correlation Matrix")
    plt.show()

def plot_covariance_matrix(dataFrame):
    valid_columns=dataFrame.select_dtypes(include=['number']).columns

    X=dataFrame[valid_columns].cov()

    plt.figure("Covariance matrix",figsize=(8, 6))
    sns.heatmap(X, cmap='coolwarm', robust=True,linewidths=1)
    plt.title("Covariance Matrix")
    plt.show()

def plot_histogram_grouped(data,x,group):
    g = sns.catplot(data=data, kind="bar",x=group, y=x,errorbar="sd", palette="dark", alpha=.6, height=6)
    g.set_axis_labels(group,x)
    g.despine(left=True)
    plt.show()
    #g.legend.set_title("")

def plot_general_group(data,group):
    if group!="":
        g =sns.pairplot(data, hue=group, height=2.5)
    else:
        g =sns.pairplot(data,height=2.5)
    plt.show()
