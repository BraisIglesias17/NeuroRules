from scipy.stats import chi2,pearsonr,wilcoxon,shapiro,kruskal,kstest,t,f_oneway,mannwhitneyu,ttest_ind
import numpy as np

class StatisticTest():

    @staticmethod
    def GROUPING_SAME_VARIABLE():
        return ['T Student - (Difference between groups)','ANOVA - (Difference between groups)','Kruskal Wallis - (Difference between groups)','Wilcoxon - (Difference between groups)']

    @staticmethod
    def COMPARING_DIFFERENT_VARIABLES():
        return ['Pearson - (Correlation)']
    
    @staticmethod
    def SINGLE_VARIABLE():
        return ['Shapiro - (Normality)']
    
    @staticmethod
    def get_tests():
        return ['T Student','ANOVA','Kruskal Wallis','Wilcoxon','Pearson','Shapiro']
    
    @staticmethod
    def get_placeholder():
        return ['T Student - (Difference between groups)','ANOVA - (Difference between groups)','Kruskal Wallis - (Difference between groups)','Wilcoxon - (Difference between groups)','Pearson - (Correlation)','Shapiro - (Normality)']
    
    @staticmethod
    def t_student(x,y):
        
        return ttest_ind(np.array(x).astype(float),np.array(y).astype(float))

    @staticmethod
    def ANOVA(x,y):
        return f_oneway(x,y)
    
    @staticmethod
    def chi_squared(input):
        return chi2(input)
    
    @staticmethod
    def wilcoxon(x,y):
        
        return mannwhitneyu(np.array(x).astype(float),np.array(y).astype(float))
    
    @staticmethod
    def kruskal_wallis(x,y):
        return kruskal(x,y)
    
    @staticmethod
    def kolmorov_smirnov(x,y):
        return kstest(x,y)
    
    @staticmethod
    def shapiro_wilk(x):
        return shapiro(x)
    
    @staticmethod
    def mcNemar():
        return 0.0

    @staticmethod
    def pearson(x,y):
        return pearsonr(x,y)
    
"""
import pandas as pd
data=pd.read_csv("C:/Users/USUARIO/Desktop/TFM/project/invitro_g.csv",sep=",")

x=data['PolymerA']
y=data['1hr']
print(StatisticTest.kruskal_wallis(x,y))
"""




