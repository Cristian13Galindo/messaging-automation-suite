import os
from datetime import datetime

class SMSService:
    def __init__(self):
        self.root_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.logs_path = os.path.join(self.root_path, "logs")
        self.configured = False
    
    def configure(self):
        """Configura el servicio SMS"""
        pass
    
    def send_message(self, phone, message):
        """Envía un mensaje SMS"""
        pass