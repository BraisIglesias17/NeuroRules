import json

class Status():
    OK=1
    VALIDATION_ERROR=2
    GENERAL_ERROR=3
    IO_ERROR=4
    EXISTING_TASK=6
    EXISTING_TASK_UNSAVED=7
    CANCEL=5
    EXISTING_TASK_NO_EXECUTED=8

class Response():

    def __init__(self,data=None,status=None):
        self.response={}
        self.response['data']=data
        self.response['status']=status


    def getResponse(self):
        return self.response