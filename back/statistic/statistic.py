"""Module for statistic test"""
import numpy as np
from scipy.stats import chi2,pearsonr,shapiro,kruskal,kstest,f_oneway,mannwhitneyu,ttest_ind
from numpy.typing import ArrayLike
class StatisticTest():
    """
        Class that encapsulates the statistics test
    """
    @staticmethod
    def GROUPING_SAME_VARIABLE():
        """
            Return the list of available methods for one variable grouped
        """
        return ['T Student - (Difference between groups)'
                ,'ANOVA - (Difference between groups)'
                ,'Kruskal Wallis - (Difference between groups)'
                ,'Wilcoxon - (Difference between groups)']
    @staticmethod
    def COMPARING_DIFFERENT_VARIABLES():
        """
            Return the list of available methods for two different variable
        """
        return ['Pearson - (Correlation)']
    @staticmethod
    def SINGLE_VARIABLE():
        """
            Return the list of available methods for one variable
        """
        return ['Shapiro - (Normality)']
    @staticmethod
    def get_tests():
        """
            Return the list of all test
        """
        return ['T Student','ANOVA','Kruskal Wallis','Wilcoxon','Pearson','Shapiro']
    @staticmethod
    def get_placeholder():
        """
            Return the list of all test placeholder
        """
        return ['T Student - (Difference between groups)'
                ,'ANOVA - (Difference between groups)'
                ,'Kruskal Wallis - (Difference between groups)'
                ,'Wilcoxon - (Difference between groups)'
                ,'Pearson - (Correlation)','Shapiro - (Normality)']
    @staticmethod
    def t_student(x:ArrayLike,y:ArrayLike):
        """
            Return the result of T Student test
        """
        return ttest_ind(np.array(x).astype(float),np.array(y).astype(float))
    @staticmethod
    def ANOVA(x:ArrayLike,y:ArrayLike):
        """
            Return the result of ANOVA test
        """
        return f_oneway(x,y)
    @staticmethod
    def chi_squared(x:ArrayLike):
        """
            Return the result of CHI SQUARED test
        """
        return chi2(x)
    @staticmethod
    def wilcoxon(x:ArrayLike,y:ArrayLike):
        """
            Return the result of MANNWHITNEY test
        """
        return mannwhitneyu(np.array(x).astype(float),np.array(y).astype(float))
    @staticmethod
    def kruskal_wallis(x:ArrayLike,y:ArrayLike):
        """
            Return the result of KRUSKAL WALLIS test
        """
        return kruskal(x,y)
    @staticmethod
    def kolmorov_smirnov(x:ArrayLike,y:ArrayLike):
        """
            Return the result of KOLMOROV test
        """
        return kstest(x,y)
    @staticmethod
    def shapiro_wilk(x:ArrayLike):
        """
            Return the result of SHAPIRO test
        """
        return shapiro(x)
    @staticmethod
    def pearson(x:ArrayLike,y:ArrayLike):
        """
            Return the result of Pearson test
        """
        return pearsonr(x,y)
    