from abc import ABC, abstractmethod
import pickle

class Model(ABC):
 
    @abstractmethod
    def train(self,input,target):
        pass

    @abstractmethod
    def predict(self,input):
        pass 

    @abstractmethod
    def report(self):
        pass

    @abstractmethod
    def save(self,filename):
        pass

    @abstractmethod
    def set_params(self,dict):
        pass




class ModelImplementation(Model):
    
    def __init__(self,filename=None):

        if(not filename == None):
             self.model=pickle.load(open(filename, 'rb'))
             
    def train(self,input,target):
        self.model.fit(input,target)
  
    def predict(self,input):
        return self.model.predict(input)

    def set_params(self, dict):
        self.model.set_params(dict)
        
    def get_info(self):
        print(self.model)

    def report(self):
        return self.model.score

    def save(self, filename):
        try:
            pickle.dump(self.model, open(filename, 'wb'))
            return True
        except Exception as exc:
            return False
        

        
