""" Logger module"""
import logging
from datetime import datetime
import warnings

class Trace():
    
    WARNING=logging.WARNING
    ERROR=logging.ERROR
    INFO=logging.INFO
    """
    Singleton class to register logs
    """
    instance = None
    log_history=[]
    _initialized=False
    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(Trace, cls).__new__(cls)
            cls.instance._initialized = False
            cls.instance.log_history = []
        return cls.instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        warnings.showwarning=self._log_warning
        self.logger = logging.getLogger("trace")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def _log_warning(self,message, category, filename, lineno, file=None, line=None):
        self.log(message=str(message).split(' - ')[0],level=logging.WARNING)

    def log(self, message: str,level=logging.INFO):
        """
        Register a log history
        Args:
            - message: message of the log
            - level: level of the log (INFO,WARNING,ERROR)
        """
        entry={'time':datetime.now().strftime('%H:%M:%S')
               ,'level':logging.getLevelName(level)
               ,'message':message}
        self.log_history.append(entry)
        self.log_history = self.log_history[-50:]
        self.logger.log(level,message)

    def get_log_history(self):
        """
        Return de log history
        """
        return self.log_history
    