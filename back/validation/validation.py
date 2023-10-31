import numpy as np
import re

class Validator():

    @staticmethod
    def check_integer(val):
        try:
            cast=int(val)
            if isinstance(cast,(int,np.int32,np.int16)):
                return True
            return False
        except Exception as exc:
            return False        
    
                    
    @staticmethod
    def check_float(val):
        
        if type(val) is float or (type(val) is np.float32) or (type(val) is np.float64):
            return True
        else:
            return False
    
    def check_parse_float(val):
        toret=False
        try:
            np.float32(val)
            toret=True
        except:
            toret=False
        finally:
            return toret

    @staticmethod
    def check_string(val):
        return True
    
    @staticmethod
    def validate_name(val):
        
        if val=="" or val==None:
            return False
        
        if re.match(r'^[a-zA-Z0-9_/]*$', val):
            return True
        else:
            return False
        