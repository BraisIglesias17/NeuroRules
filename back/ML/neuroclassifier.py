from sklearn.tree import DecisionTreeClassifier,plot_tree,export_text
from sklearn.tree import _tree
import numpy as np
import matplotlib.pyplot as plt
from numpy.typing import ArrayLike

class NeuroClassifier():

    def __init__(self,names: list[str],classes: list[str],params: {}):
        
        
        self.tree=DecisionTreeClassifier(max_depth=len(names),**params)
        self.class_names=classes
        self.names=names
    
    def fit(self,X: ArrayLike,y: ArrayLike):
        self.tree.fit(X,y)

    def get_rules(self):
        return self._get_rules()
    
    def get_params(self):
        return self.tree.get_params()

    def set_params(self,params:{}):
        self.tree.set_params(params)

    def plot_tree(self):
        fig = plt.figure(figsize=(8,8))
        _ = plot_tree(self.tree, 
                        feature_names=self.names,  
                        class_names=self.class_names,
                        filled=True)
        plt.show()

    def predict(self,X: ArrayLike):
        return self.tree.predict(X)

    def _get_rules(self):
        tree_ = self.tree.tree_
        feature_name = [ self.names[i] if i != _tree.TREE_UNDEFINED else "undefined!" for i in tree_.feature ]
        paths = []
        path = []
        
        def recurse(node, path, paths):
            
            if tree_.feature[node] != _tree.TREE_UNDEFINED:
                name = feature_name[node]
                threshold = tree_.threshold[node]
                p1, p2 = list(path), list(path)
                p1 += [f"({name} <= {np.round(threshold, 3)})"]
                recurse(tree_.children_left[node], p1, paths)
                p2 += [f"({name} > {np.round(threshold, 3)})"]
                recurse(tree_.children_right[node], p2, paths)
            else:
                path += [(tree_.value[node], tree_.n_node_samples[node])]
                paths += [path]
                
        recurse(0, path, paths)

        samples_count = [p[-1][1] for p in paths]
        ii = list(np.argsort(samples_count))
        paths = [paths[i] for i in reversed(ii)]
        
        rules = []
        for path in paths:
            rule = "IF "
            
            for p in path[:-1]:
                if rule != "IF ":
                    rule += " AND "
                rule += str(p)
            rule += " THEN "
            if self.class_names is None:
                rule += "response: "+str(np.round(path[-1][0][0][0],3))
            else:
                classes = path[-1][0][0]
                l = np.argmax(classes)
                rule += f" {self.class_names[l]} ({np.round(classes[l]/np.sum(classes),2)})"
            rules += [rule]
            
        return rules
