""" Module for defining the responses 
format for the communication between components in the program"""

class Status():
    """
    Class that defines some status for response
    """
    OK=1
    VALIDATION_ERROR=2
    GENERAL_ERROR=3
    IO_ERROR=4
    EXISTING_TASK=6
    EXISTING_TASK_UNSAVED=7
    CANCEL=5
    EXISTING_TASK_NO_EXECUTED=8
    UNEXISTING_TASK=9

class Response():
    """
        Function that represent a communication between back and front
    """
    def __init__(self,data: any=None,status: Status=None):
        self.response={}
        self.response['data']=data
        self.response['status']=status
    def get_response(self):
        """
        Function that returns the current response
        """
        return self.response
    