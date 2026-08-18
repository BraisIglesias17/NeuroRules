""" Module that contains the building plots methods. """

import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
import seaborn as sns
from sklearn import linear_model
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

def plot_2d(data):
    """
    Function for ploting 2D graphs
    Args: data - dictionanty of the variables to show with name and data for each
    """
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

    if data['y_right']['name']!="":
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel(data['y_right']['name'], color=color)
        ax2.scatter(x, y_right, color=color,marker='v')
        ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()
    plt.show()


def plot_3d(data):
    """
    Function for ploting 3D graphs
    Args: data - dictionanty of the variables to show with name and data for each
    """
    x=data['x']['data']
    y=data['y']['data']
    z=data['z']['data']
    fig = plt.figure("3D Graph",figsize=(10, 8))
    triang = mtri.Triangulation(x, y)
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_trisurf(triang, z, cmap='jet')
    #surf = ax.plot_trisurf(x, y, z, cmap='jet')
    fig.colorbar(surf)
    ax.set_title('3D mesh graph')
    ax.set_xlabel(data['x']['name'])
    ax.set_ylabel(data['y']['name'])
    ax.set_zlabel(data['z']['name'])
    plt.show()

def plot_countplot(nominal):
    """
    Function for ploting a countplot for nominal variables
    Args: nominal - nominal variable
    """
    sns.set_theme(style="whitegrid")
    plot=sns.countplot(x=nominal)
    for p in plot.patches:
        plot.annotate(r'{:}'.format(p.get_height()), (p.get_x()+0.33, p.get_height()+0.1))
    plt.show()

def plot_hist(data,option):
    """
    Function for ploting histograms
    Args: data - dictionanty of the variables to show with name and data for each
    """
    x=data['x']['data']
    plt.figure("Histogram",figsize=(8, 6))
    #plt.hist(x, bins=option['bins'], color='blue', alpha=0.7,edgecolor="black")
    sns.histplot(x,kde=True)
    plt.title('Histogram')
    plt.xlabel(data['x']['name'])
    plt.ylabel('Frequency')
    plt.show()


def plot_boxplot(data):
    """
    Function for ploting box plot
    Args: data - dictionanty of the variables to show with name and data for each
    """
    x=data['x']['data']
    plt.figure("Boxplot")
    sns.boxplot(data=x, orient="v")
    plt.show()

def plot_regression(data):
    """
    Function for ploting the fitted regression line between two variables
    Args: data - dictionanty of the variables to show with name and data for each
    """
    x=np.array(data['x']['data'])
    y=np.array(data['y']['data'])

    x=x.reshape(-1,1)
    
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
    
    plt.figure("Fitted regression line",figsize=(8, 6))
    plt.scatter(x, y, label='Data points', color='blue')
    plt.title('Regression Fit Line')
    plt.xlabel(data['x']['name'])
    plt.ylabel(data['y']['name'])
    plt.grid(True)
    regression=linear_model.LinearRegression()
   
    regression.fit(X_train,y_train)
    fit_line=regression.predict(X_test)

    R2=r2_score(X_test,fit_line)

    plt.annotate('R2 = (%.2f)'%(R2), xy=(sum(x)/len(x),max(y)-5),xytext =(2,2),textcoords ='offset points',fontsize=13,ha='center')

    plt.plot(X_test,fit_line, color='red')
    plt.legend()
    plt.show()

def plot_correlation_matrix(dataFrame):
    """
    Function for ploting correlation matrix
    Args: dataFrame with the data wanted to represent
    """
    valid_columns=dataFrame.select_dtypes(include=['number']).columns
    X=dataFrame[valid_columns].corr()
    plt.figure("Correlation matrix",figsize=(8, 6))
    sns.heatmap(X, annot=True, cmap='coolwarm', center=0)
    plt.title("Correlation Matrix")
    plt.show()

def plot_covariance_matrix(dataFrame):
    """
    Function for ploting covariance matrix
    Args: dataFrame with the data wanted to represent
    """
    valid_columns=dataFrame.select_dtypes(include=['number']).columns
    X=dataFrame[valid_columns].cov()
    plt.figure("Covariance matrix",figsize=(8, 6))
    sns.heatmap(X, cmap='coolwarm', robust=True,linewidths=1)
    plt.title("Covariance Matrix")
    plt.show()

def plot_histogram_grouped(data,x,group):
    """
    Function for ploting histogram grouped by a nomnial variable
    Args: data - whole dataset 
        x - concrete variable to display
        group - nominal variable to group by
    """
    g = sns.catplot(data=data, kind="bar",x=group, 
                    y=x,errorbar="sd", palette="dark", 
                    alpha=.6, height=6)
    g.set_axis_labels(group,x)
    g.despine(left=True)
    plt.show()

def plot_histogram(data,x):
    """
    Function for ploting histogram of a variable
    Args: data - whole dataset 
        x - concrete variable to display
    """
    g = sns.histplot(data=data, x=x, kde=True)
    plt.show()

def plot_general_group(data,group):
    """
    Function for ploting the pair plot between variables 
    Args: data - variables wanted to represent
          group - variable to group by, it can be empty
    """
    if group!="":
        sns.pairplot(data, hue=group, height=2.5)
    else:
        sns.pairplot(data,height=2.5)
    plt.show()

def plot_barplot(data,xtitle,ytitle,title=""):
    """
    Function that encapsulates the function of the barplot creation and displays it.
    Args: dict - dictionary with variable labels as keys and data as values
          xtitle - X axis wanted title
          ytitle - Y axis wanted title
    """
    plot_barplot_object(data,xtitle,ytitle,title=title).show()

def plot_barplot_object(data,xtitle,ytitle,title=""):
    """
    Function that generates the bar plot object
    Args:  dict - dictionary with variable labels as keys and data as values
          xtitle - X axis wanted title
          ytitle - Y axis wanted title
    """
    plt.close('all')
    plt.figure(title)
    labels = list(data.keys())
    values = list(data.values())
    plt.bar(labels, values,color=plt.cm.Paired(range(len(labels))))
    plt.axhline(y=0, color='black', linestyle='-',linewidth=0.5)
    plt.xlabel(xtitle)
    plt.ylabel(ytitle)
    plt.title(title)
    for i in range(len(labels)):
        plt.text(labels[i], values[i], str(np.round(values[i],4)), ha='center', va='bottom')
    return plt
