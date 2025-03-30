import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from datetime import datetime

# Configuración
ARCHIVO_EXCEL = "clientes.xlsx"
ARCHIVO_ERRORES = "registro_envios.txt"
MENSAJE_BASE = """
¡Señora consultora {nombre} {apellido}! 
Su factura Esika está vencida. Por favor realice hoy su pago de ${deuda:,.0f}. 
Pague con su cédula: {cedula}.
¡Gracias!
"""

def configurar_navegador():
    """Configura Chrome en modo incógnito"""
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def esperar_inicio_sesion(driver):
    """Espera hasta que se complete el login"""
    print("\n🔍 Por favor escanea el código QR de WhatsApp Web...")
    driver.get("https://web.whatsapp.com")
    
    try:
        WebDriverWait(driver, 120).until(
            lambda d: d.find_elements(By.XPATH, '//div[@role="textbox"]') or 
                     d.find_elements(By.XPATH, '//canvas[@aria-label="Escanea el código QR"]')
        )
        
        if driver.find_elements(By.XPATH, '//div[@role="textbox"]'):
            print("✅ Sesión iniciada correctamente")
            return True
        
        print("👀 QR detectado, esperando escaneo...")
        input("Presiona Enter después de escanear el QR...")
        
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[@role="textbox"]'))
        )
        return True
        
    except TimeoutException:
        print("❌ Tiempo de espera agotado")
        return False

def verificar_envio(driver, timeout=10):
    """Verifica si el mensaje se envió correctamente"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.find_elements(By.XPATH, '//span[@data-icon="msg-check"]') or
                     d.find_elements(By.XPATH, '//span[@data-icon="msg-time"]')
        )
        
        if driver.find_elements(By.XPATH, '//span[@data-icon="msg-check"]'):
            return True, "Envío confirmado"
        elif driver.find_elements(By.XPATH, '//span[@data-icon="msg-time"]'):
            return False, "En cola (no confirmado)"
        return False, "Estado desconocido"
            
    except TimeoutException:
        return False, "No se detectó confirmación"

def enviar_mensaje(driver, telefono, mensaje):
    """Envía mensajes al campo correcto con registro detallado"""
    try:
        # 1. Navegación al chat
        driver.get(f"https://web.whatsapp.com/send?phone={telefono}")
        time.sleep(5)
        
        # 2. Localización del campo de mensaje
        msg_box = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        )
        
        # 3. Envío seguro
        msg_box.click()
        msg_box.clear()
        for line in mensaje.split('\n'):
            msg_box.send_keys(line)
            msg_box.send_keys(Keys.SHIFT + Keys.ENTER)
        msg_box.send_keys(Keys.ENTER)
        time.sleep(3)
        
        # 4. Verificación y registro
        status, detalle = verificar_envio(driver)
        registro = {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "telefono": telefono,
            "estado": "Éxito" if status else "Fallo",
            "detalle": detalle,
            "confirmado": status
        }
        
        print(f"{'✅' if status else '❌'} {telefono} - {detalle}")
        return registro
            
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"❌ {telefono} - {error_msg}")
        return {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "telefono": telefono,
            "estado": "Error",
            "detalle": error_msg,
            "confirmado": False
        }

def guardar_registro(registros):
    """Guarda los resultados en un archivo estructurado"""
    with open(ARCHIVO_ERRORES, "w", encoding="utf-8") as f:
        f.write("FECHA | TELÉFONO | ESTADO | DETALLE\n")
        f.write("-----------------------------------\n")
        for r in registros:
            f.write(f"{r['fecha']} | {r['telefono']} | {r['estado']} | {r['detalle']}\n")

def verificar_dependencias():
    """Verifica que todas las dependencias necesarias estén instaladas"""
    try:
        import selenium
        import pandas
        import webdriver_manager
        import openpyxl
        import customtkinter
        print("✅ Todas las dependencias están instaladas correctamente")
        return True
    except ImportError as e:
        print(f"❌ Error: Falta instalar algunas dependencias: {str(e)}")
        print("📝 Por favor, ejecuta: pip install -r requirements.txt")
        return False


def main():
    verificar_dependencias()
    print("🚀 Iniciando automatización de WhatsApp")
    driver = configurar_navegador()
    registros = []
    
    try:
        if esperar_inicio_sesion(driver):
            datos = pd.read_excel(ARCHIVO_EXCEL, engine='openpyxl', dtype={"Telefono": str})
            
            for _, fila in datos.iterrows():
                telefono = fila["Telefono"].strip()
                if not telefono.startswith("+"):
                    telefono = f"+{telefono}"
                
                mensaje = MENSAJE_BASE.format(
                    nombre=fila["Nombre"],
                    apellido=fila.get("Apellido", ""),
                    deuda=fila["Deuda"],
                    cedula=fila["Cedula"]
                )
                
                print(f"\n📤 Procesando: {fila['Nombre']} ({telefono})...")
                registro = enviar_mensaje(driver, telefono, mensaje)
                registros.append(registro)
                
                time.sleep(10)  # Pausa anti-bloqueo
            
            # Generar reporte
            exitosos = sum(1 for r in registros if r['confirmado'])
            guardar_registro(registros)
            print(f"\n📊 Resultado final: {exitosos}/{len(datos)} enviados exitosamente")
            print(f"📄 Registro completo guardado en: {ARCHIVO_ERRORES}")
    
    finally:
        driver.quit()
        print("\n🏁 Proceso completado")

if __name__ == "__main__":
    main()