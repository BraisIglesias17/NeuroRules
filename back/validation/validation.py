"""Validation module"""
import re
import numpy as np


class Validator():
    """
        Class used for encapsule validation methods for the application
    """

    @staticmethod
    def _check_types(val,valid_types):
        if any(isinstance(val, typ) for typ in valid_types):
            return True
        return False
    @staticmethod
    def check_integer(val):
        """
        Function used to verify if a value is a integer
        Args:
            - val: input value

        returns: true if its integer, false if it is not
        """
        valid_types = [int, np.int32, np.int16]
        return Validator._check_types(val,valid_types)
               
    @staticmethod
    def check_float(val):
        """
        Function used to verify if a value is a float
        Args:
            - val: input value

        returns: true if its float, false if it is not
        """
        valid_types = [float,np.float32,np.float64]
        return Validator._check_types(val,valid_types)
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
    
    @staticmethod
    def check_parse_int(val):
        """
        Function used parse a value to float type
        Args:
            - val: input value

        returns: value as float type
        """
        try:
            np.int32(val)
            return True
        except Exception:
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
    
