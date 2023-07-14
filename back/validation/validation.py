import numpy as np

class Validator():

    @staticmethod
    def check_integer(val):
        if type(val) is int or (type(val) is np.int32) or (type(val) is np.int16):
            return True
        else:
            try:
                float(val)
            except Exception as exc:
                return False    
            try:
                int(val)
                return True
            except Exception as exc:
                return False  
            
    
                    
    @staticmethod
    def check_float(val):
        
        if type(val) is float or (type(val) is np.float32) or (type(val) is np.float64):
            return True
        else:
            try:
                float(val)
                return True
            except Exception as exc:
                return False
    
    @staticmethod
    def check_string(val):
        return True