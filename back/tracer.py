import logging
from datetime import datetime


class Trace():
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Trace, cls).__new__(cls)
            cls._instance._initialized = False
            cls._instance._log_history = []
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        # Configuración del logger
        self.logger = logging.getLogger("trace")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log(self, message,level=logging.INFO):

        entry={'time':datetime.now().strftime('%H:%M:%S'),'level':logging.getLevelName(level),'message':message}
        self._log_history.append(entry)
        self._log_history = self._log_history[-50:]
        self.logger.log(level,message)

    def get_log_history(self):
        
        return self._log_history

