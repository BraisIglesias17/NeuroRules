"""Validation module"""
import re
import numpy as np


class Validator():
    """
        Class used for encapsule validation methods for the application
    """
    @staticmethod
    def check_integer(val):
        """
        Function used to verify if a value is a integer
        Args:
            - val: input value

        returns: true if its integer, false if it is not
        """
        try:
            cast=int(val)
            if isinstance(cast,type([int,np.int32,np.int16])) and val==cast:
                return True
            return False
        except Exception:
            return False        
    @staticmethod
    def check_float(val):
        """
        Function used to verify if a value is a float
        Args:
            - val: input value

        returns: true if its float, false if it is not
        """
        return isinstance(val,type([float,np.float32,val,np.float64]))
    @staticmethod
    def check_parse_float(val):
        """
        Function used parse a value to float type
        Args:
            - val: input value

        returns: value as float type
        """
        try:
            np.float32(val)
            return True
        except Exception:
            return False
        return False
    @staticmethod
    def check_string(val):
        """
        Function used to validate strings
        """
        print(val)
        return True
    @staticmethod
    def validate_name(val):
        """
            Function that validates a name that can only contains characters, numbers and _

            Args: - name tu validate 

            Return: true if name is valid, false in other case
        """
        if val=="" or val is None:
            return False
        return re.match(r'^[a-zA-Z0-9_/]*$', val)
    