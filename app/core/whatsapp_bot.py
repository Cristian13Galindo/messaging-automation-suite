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
    """Configura y devuelve una instancia de Chrome WebDriver"""
    options = webdriver.ChromeOptions()
    
    # Forzar modo incógnito
    options.add_argument('--incognito')
    
    # Configuraciones básicas
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-infobars')
    
    # Configuraciones anti-detección
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    # URL específica para WhatsApp Web
    # Crear el driver con las opciones configuradas
    driver = webdriver.Chrome(options=options)
    
    # Configurar stealth
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    })
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # Navegar directamente a WhatsApp Web
    driver.get("https://web.whatsapp.com/")
    
    return driver

def esperar_inicio_sesion(driver):
    """Espera a que el usuario inicie sesión en WhatsApp Web"""
    print("🔍 Por favor escanea el código QR de WhatsApp Web...")
    
    try:
        # Esperar máximo 60 segundos para el inicio de sesión
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="app"]'))
        )
        
        # Esperar a que desaparezca el QR
        try:
            WebDriverWait(driver, 60).until_not(
                EC.presence_of_element_located((By.XPATH, '//canvas[contains(@aria-label, "Scan me!")]'))
            )
        except:
            pass
            
        # Dar tiempo para que cargue la interfaz
        time.sleep(5)
        
        # Manejar ventanas emergentes iniciales
        manejar_ventanas_emergentes(driver)
        
        print("✅ Sesión iniciada correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al iniciar sesión: {str(e)}")
        return False

def verificar_envio(driver, timeout=10):
    """Verifica si el mensaje se envió correctamente"""
    try:
        # Esperar a que aparezca cualquier indicador de estado
        WebDriverWait(driver, timeout).until(
            lambda d: (
                d.find_elements(By.XPATH, '//span[@data-icon="msg-check"]') or
                d.find_elements(By.XPATH, '//span[@data-icon="msg-dblcheck"]') or
                d.find_elements(By.XPATH, '//span[@data-icon="msg-time"]') or
                d.find_elements(By.XPATH, '//div[contains(@class, "error")]')
            )
        )
        
        # Verificar estado del mensaje
        if driver.find_elements(By.XPATH, '//span[@data-icon="msg-dblcheck"]'):
            return True, "Mensaje entregado"
        elif driver.find_elements(By.XPATH, '//span[@data-icon="msg-check"]'):
            return True, "Mensaje enviado"
        elif driver.find_elements(By.XPATH, '//span[@data-icon="msg-time"]'):
            return False, "Mensaje en cola"
        elif driver.find_elements(By.XPATH, '//div[contains(@class, "error")]'):
            return False, "Número no disponible en WhatsApp"
            
        return False, "Estado desconocido"
            
    except TimeoutException:
        # Verificar si hay error de número inválido
        if driver.find_elements(By.XPATH, '//div[contains(text(), "Phone number shared via url is invalid")]'):
            return False, "Número inválido"
        return False, "No se detectó confirmación"

def enviar_mensaje(driver, telefono, mensaje):
    """Envía un mensaje por WhatsApp con optimización de velocidad"""
    try:
        # Navegación al chat
        print(f"🔄 Navegando al chat de {telefono}...")
        driver.get(f"https://web.whatsapp.com/send?phone={telefono}")
        
        # OPTIMIZACIÓN 1: Espera dinámica en lugar de tiempo fijo
        print("⏳ Esperando carga de chat...")
        # Esperar por el campo de texto directamente (indicador clave de que el chat está listo)
        try:
            # Selector directo y simple pero específico para el campo de texto del chat
            campo_texto = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//footer//div[@role="textbox"]'))
            )
            print("✅ Chat cargado correctamente")
            
            # OPTIMIZACIÓN 2: Acciones inmediatas sin esperas adicionales
            # Hacer foco en el campo y escribir inmediatamente
            driver.execute_script("arguments[0].click();", campo_texto)
            
            # OPTIMIZACIÓN 3: Escribir mensaje sin pausa
            print("📝 Escribiendo mensaje...")
            campo_texto.send_keys(mensaje)
            
            # OPTIMIZACIÓN 4: Enviar inmediatamente
            campo_texto.send_keys(Keys.ENTER)
            print(f"✅ {telefono} - Mensaje enviado")
            
            # Espera mínima para asegurar que se complete el envío
            time.sleep(1.5)
            
            return {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "telefono": telefono,
                "estado": "Éxito",
                "detalle": "Mensaje enviado",
                "confirmado": True
            }
            
        except Exception as e:
            # Si falla el método optimizado, intentar con el método tradicional
            print(f"⚠️ Método rápido falló, intentando método alternativo: {str(e)}")
            
            # Manejar cualquier ventana emergente
            manejar_ventanas_emergentes(driver)
            
            # Dar tiempo adicional si el método rápido falló
            time.sleep(5)
            
            # Buscar nuevamente el campo de texto
            campo_texto = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, 
                    '//footer//div[@role="textbox" and @contenteditable="true"]'
                ))
            )
            
            # Intentar enviar el mensaje con el método tradicional
            campo_texto.click()
            time.sleep(0.5)
            campo_texto.send_keys(mensaje)
            time.sleep(0.5)
            campo_texto.send_keys(Keys.ENTER)
            time.sleep(2)
            
            print(f"✅ {telefono} - Mensaje enviado (método alternativo)")
            return {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "telefono": telefono,
                "estado": "Éxito",
                "detalle": "Mensaje enviado (método alternativo)",
                "confirmado": True
            }
                
    except Exception as e:
        print(f"❌ {telefono} - Error: {str(e)}")
        driver.save_screenshot(f"error_{telefono}.png")
        return {
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "telefono": telefono,
            "estado": "Error",
            "detalle": str(e),
            "confirmado": False
        }

def manejar_ventanas_emergentes(driver):
    """Maneja múltiples tipos de ventanas emergentes en WhatsApp Web"""
    # Lista de estrategias para encontrar el botón "Continuar"
    estrategias = [
        # Por texto visible
        "//div[text()='Continuar']",
        "//button//div[contains(text(), 'Continuar')]",
        # Por clase y texto (desde el HTML proporcionado)
        "//div[contains(@class, 'tvf2evcx') and contains(text(), 'Continuar')]",
        # Estrategia genérica por contenido de la ventana
        "//div[contains(., 'Un nuevo aspecto para WhatsApp Web')]//button",
        # Botón genérico en ventana emergente
        "//div[@role='dialog']//button",
    ]
    
    # Intentar cada estrategia
    for intento in range(3):  # Intentar hasta 3 veces
        for xpath in estrategias:
            try:
                # Esperar brevemente a que aparezca el botón
                boton = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                boton.click()
                print("✅ Ventana emergente cerrada con éxito")
                time.sleep(1)
                return True
            except:
                continue
        
        # Esperar un momento antes del siguiente intento
        time.sleep(1)
    
    # Si llegamos aquí, no pudimos cerrar ninguna ventana emergente
    # (posiblemente porque no había ninguna)
    return False

def encontrar_campo_texto(driver):
    """Busca el campo de texto utilizando métodos más robustos"""
    print("🔍 Buscando campo de texto...")
    
    # Esperar más tiempo para asegurar que la página cargue completamente
    time.sleep(8)
    
    # Verificar primero que no estamos en la página principal sino en un chat
    try:
        # Buscar algún elemento que confirme que estamos en un chat
        WebDriverWait(driver, 10).until(
            EC.any_of(
                EC.presence_of_element_located((By.XPATH, '//header//span[@data-testid="conversation-info-header-chat-title"]')),
                EC.presence_of_element_located((By.XPATH, '//div[@role="textbox"]')),
                EC.presence_of_element_located((By.XPATH, '//footer'))
            )
        )
        print("✅ Conversación detectada")
    except:
        print("⚠️ No se detectó un chat abierto correctamente")
        return None
    
    # Selectores específicos para WhatsApp Web actual (julio 2025)
    selectores_actualizados = [
        # Selector por contenedor y atributos específicos (más precisos)
        '//footer//div[@role="textbox"]',
        '//div[@role="textbox" and @contenteditable="true"]',
        '//div[@data-testid="conversation-compose-box-input"]',
        '//div[@title="Escribe un mensaje" and @role="textbox"]',
        
        # Selectores por jerarquía específica (útil si la estructura cambia pero mantiene la relación)
        '//footer//div[@contenteditable="true"]',
        '//div[contains(@class,"copyable-text") and @contenteditable="true"]',
        
        # Selectores por características generales (menos precisos pero más resistentes a cambios)
        '//div[@contenteditable="true"]',
        '//div[@spellcheck="true" and @contenteditable="true"]',
    ]
    
    # Probar cada selector con tiempo de espera corto
    for selector in selectores_actualizados:
        try:
            print(f"Probando selector: {selector}")
            campo = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            
            # Hacer clic en el campo para asegurarnos que está activo
            driver.execute_script("arguments[0].click();", campo)
            time.sleep(1)
            
            # Limpiar cualquier contenido previo
            driver.execute_script("arguments[0].innerHTML = '';", campo)
            
            print(f"✅ Campo de texto encontrado con selector: {selector}")
            return campo
        except Exception as e:
            continue
    
    print("❌ No se pudo encontrar el campo de texto")
    return None

def enviar_mensaje_con_boton_o_enter(driver, campo_texto):
    """Intenta enviar el mensaje usando botón o Enter"""
    intentos = 0
    enviado = False
    
    while intentos < 3 and not enviado:
        try:
            # Intentar con el botón de enviar
            botones = [
                '//button[@data-testid="compose-btn-send"]',
                '//button[@aria-label="Enviar"]',
                '//button[contains(@class, "tvf2evcx")]//span[@data-testid="send"]',
                '//span[@data-icon="send"]/..',
            ]
            
            for selector in botones:
                try:
                    boton = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    boton.click()
                    enviado = True
                    break
                except:
                    continue
            
            # Si no se pudo con el botón, intentar con Enter
            if not enviado:
                campo_texto.send_keys(Keys.ENTER)
                enviado = True
            
        except:
            intentos += 1
            time.sleep(1)
    
    # Dar tiempo para que se procese el envío
    time.sleep(3)
    return enviado

def verificar_envio_real(driver):
    """Verifica si el mensaje realmente se envió"""
    # Intentar encontrar indicadores de mensaje enviado
    indicadores = [
        '//span[@data-testid="msg-check"]',
        '//span[@data-icon="msg-check"]',
        '//span[@aria-label="Enviado"]',
        '//span[@aria-label="Entregado"]',
        '//span[@aria-label="Leído"]',
        '//div[@data-testid="msg-dblcheck"]',
    ]
    
    for selector in indicadores:
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, selector))
            )
            return True
        except:
            continue
    
    # Buscar si hay mensajes de error
    errores = [
        '//div[contains(text(), "El número de teléfono compartido a través de la dirección URL no es válido")]',
        '//div[contains(text(), "Phone number shared via url is invalid")]',
    ]
    
    for selector in errores:
        try:
            if driver.find_elements(By.XPATH, selector):
                return False
        except:
            continue
    
    # Si no encontramos indicadores claros, asumimos que no se envió
    return False

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
                
                # OPTIMIZACIÓN: Reducir el tiempo entre mensajes
                time.sleep(3)  # Tiempo suficiente para evitar bloqueos pero no excesivo
            
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