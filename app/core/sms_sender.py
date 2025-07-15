import os
import requests
from datetime import datetime
from typing import Dict, List

class SMSService:
    def __init__(self):
        self.root_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.logs_path = os.path.join(self.root_path, "logs")
        self.sms_log = os.path.join(self.logs_path, "sms_envios.txt")
        self.api_key = None
        self.configured = False

    def configure(self, api_key: str) -> bool:
        """Configura el servicio SMS con una API key"""
        self.api_key = api_key
        self.configured = True
        return True

    def send_message(self, phone: str, message: str) -> Dict:
        """Envía un mensaje SMS y retorna el resultado"""
        if not self.configured:
            return {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "telefono": phone,
                "estado": "Error",
                "detalle": "Servicio SMS no configurado",
                "confirmado": False
            }

        try:
            # Aquí iría la lógica de envío real usando una API de SMS
            # Por ahora simulamos el envío
            print(f"📤 Simulando envío SMS a {phone}: {message}")
            
            registro = {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "telefono": phone,
                "estado": "Éxito",
                "detalle": "SMS enviado correctamente",
                "confirmado": True
            }
            
            return registro
            
        except Exception as e:
            return {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "telefono": phone,
                "estado": "Error",
                "detalle": str(e),
                "confirmado": False
            }

    def guardar_registro(self, registros: List[Dict]) -> None:
        """Guarda el registro de envíos SMS"""
        with open(self.sms_log, "w", encoding="utf-8") as f:
            f.write("FECHA | TELÉFONO | ESTADO | DETALLE\n")
            f.write("-" * 80 + "\n")
            for r in registros:
                f.write(
                    f"{r['fecha']} | {r['telefono']} | {r['estado']} | "
                    f"{r['detalle']}\n"
                )