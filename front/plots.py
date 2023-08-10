import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

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

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    ax.scatter(x, y, z, c='blue', marker='o', label='Datos')

    ax.set_title('Gráfico 3D de Variables')
    ax.set_xlabel(data['x']['name'])
    ax.set_ylabel(data['y']['name'])
    ax.set_zlabel(data['z']['name'])
    ax.legend()
    
    plt.show()

def plot_hist(data,option):
    x=data['x']['data']
    plt.figure(figsize=(8, 6))
    plt.hist(x, bins=option['bins'], color='blue', alpha=0.7)
    plt.title('Histogram')
    plt.xlabel(data['x']['name'])
    plt.ylabel('Frequency')
    #plt.grid(True)
    plt.show()


def plot_regression(data,options):
    x=data['x']['data']
    y=data['y']['data']

    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, label='Data points', color='blue')
    plt.title('Regression Fit Line')
    plt.xlabel(data['x']['name'])
    plt.ylabel(data['y']['name'])
    plt.grid(True)

   
    slope, intercept = np.polyfit(x, y, 1)
    fit_line = slope * x + intercept
    plt.plot(x, fit_line, color='red')
    plt.legend()
    plt.show()

