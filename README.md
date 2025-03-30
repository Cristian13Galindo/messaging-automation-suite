# Messaging-Automation-Pro

[![Python](https://img.shields.io/badge/Python-3.12-blue)](#)
[![Selenium](https://img.shields.io/badge/Selenium-4.16.0-green)](#)
[![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2.1-purple)](#)
[![Pandas](https://img.shields.io/badge/Pandas-2.1.4-yellow)](#)
[![VSCode](https://img.shields.io/badge/VS%20Code-2024-blue)](#)

Aplicación de escritorio para la automatización de envío de mensajes personalizados a través de diferentes plataformas de mensajería, desarrollada con Python y una interfaz gráfica moderna.

## Tecnologías Utilizadas

- **Backend:**
   - Python 3.12
   - Selenium WebDriver
   - Pandas para manejo de datos
   - WebDriver Manager

- **Frontend:**
   - CustomTkinter
   - Tkinter
   - TTK

## Características

- Automatización de mensajes para múltiples plataformas:
   - WhatsApp Web
   - SMS (próximamente)
   - Otros servicios de mensajería (en desarrollo)
- Carga de datos desde Excel
- Vista previa en tiempo real
- Registro detallado de envíos
- Interfaz gráfica moderna y amigable

## Instrucciones de Instalación

1. Clone el repositorio:
```bash
git clone (https://github.com/Cristian13Galindo/messaging-automation-suite.git)
```

2. Instale las dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecute la aplicación:
```bash
python main.py
```

## Estructura del Proyecto

```
messaging-automation-pro/
│
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   └── whatsapp_bot.py
│   │
│   ├── gui/
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── dynamic_table.py
│   │   │   └── message_editor.py
│   │   ├── __init__.py
│   │   └── main_window.py
│   │
│   └── utils/
│       └── __init__.py
│
├── data/
│   └── clientes.xlsx
│
├── logs/
│   ├── numeros_fallidos.txt
│   └── registro_envios.txt
│
├── main.py
└── requirements.txt
```

## Requisitos del Sistema

- Python 3.12 o superior
- Google Chrome
- Conexión a Internet
- Windows 10/11

## Desarrollador

- Camilo Galindo

## Notas Importantes

- La aplicación requiere un navegador Chrome instalado
- Es necesario escanear el código QR de WhatsApp Web para el primer uso
- Se recomienda tener una conexión estable a Internet

## Próximas Características

- Integración con SMS
- Programación de envíos
- Plantillas de mensajes
- Reportes estadísticos
- Soporte para más plataformas de mensajería
