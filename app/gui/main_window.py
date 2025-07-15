import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
from .components.dynamic_table import DynamicTable
from .components.message_editor import MessageEditor
from .components.country_selector import CountrySelector
from app.core.whatsapp_bot import configurar_navegador, esperar_inicio_sesion, enviar_mensaje, guardar_registro
from app.core.sms_sender import SMSService


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurar rutas
        self.root_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.assets_path = os.path.join(self.root_path, "assets")
        self.logs_path = os.path.join(self.root_path, "logs")
        
        self.title("Messaging Automation Pro")
        self.geometry("1200x800")
        
        # Inicializar variables
        self.df = None
        
        # Configurar tema
        self.configure_theme()
        
        # Crear layout
        self.create_main_layout()
    
    def configure_theme(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
    def create_main_layout(self):
        # Panel superior
        top_panel = ctk.CTkFrame(self)
        top_panel.pack(fill="x", padx=10, pady=5)
        
        # Primera fila: selector de archivo
        file_frame = ctk.CTkFrame(top_panel)
        file_frame.pack(fill="x", pady=5)
        
        self.select_file_btn = ctk.CTkButton(
            file_frame, 
            text="Importar Excel",
            command=self.select_excel_file
        )
        self.select_file_btn.pack(side="left", padx=5)
        
        self.file_label = ctk.CTkLabel(file_frame, text="No se ha seleccionado archivo")
        self.file_label.pack(side="left", padx=5)
        
        # Segunda fila: selector de país
        country_frame = ctk.CTkFrame(top_panel)
        country_frame.pack(fill="x", pady=5)
        
        self.country_selector = CountrySelector(country_frame)
        self.country_selector.pack(side="left", padx=5)
        
        # Panel principal
        main_panel = ctk.CTkFrame(self)
        main_panel.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Tabla dinámica
        self.table = DynamicTable(main_panel)
        self.table.pack(fill="both", expand=True, pady=5)
        
        # Editor de mensajes
        self.message_editor = MessageEditor(main_panel)
        self.message_editor.pack(fill="x", pady=5)
        
        # Frame para botones de envío
        self.buttons_frame = ctk.CTkFrame(main_panel)
        self.buttons_frame.pack(pady=5)
        
        # Botón WhatsApp
        self.whatsapp_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Enviar por WhatsApp 📱",
            command=self.start_whatsapp_process,
            width=200,
            height=40,
            fg_color="#25D366",  # Color verde WhatsApp
            hover_color="#128C7E"
        )
        self.whatsapp_btn.pack(side="left", padx=5)
        
        # Botón SMS
        self.sms_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Enviar por SMS 💬",
            command=self.start_sms_process,
            width=200,
            height=40,
            fg_color="#4A90E2",  # Color azul para SMS
            hover_color="#357ABD"
        )
        self.sms_btn.pack(side="left", padx=5)
        
    def select_excel_file(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if filename:
            try:
                # Cargar datos y actualizar interfaz
                self.df = pd.read_excel(filename)
                self.file_label.configure(text=os.path.basename(filename))
                self.table.load_excel(filename)  # Llamada al método de DynamicTable
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el archivo: {str(e)}")
                print(f"Error detallado: {e}")  # Para debugging

    def get_message_data(self):
        """Obtiene los datos y el mensaje a enviar"""
        data = []
        for item in self.table.table.get_children():
            values = self.table.table.item(item)["values"]
            if any(values):  # Solo procesar filas con datos
                row_dict = dict(zip(self.table.table["columns"], values))
                data.append(row_dict)
        
        if not data:
            messagebox.showerror("Error", "No hay datos para enviar")
            return None, None
            
        message_template = self.message_editor.editor.get("1.0", "end-1c")
        if not message_template.strip():
            messagebox.showerror("Error", "El mensaje está vacío")
            return None, None
            
        return data, message_template
            
    def start_whatsapp_process(self):
        """Inicia el proceso de envío por WhatsApp"""
        data, message_template = self.get_message_data()
        if not data or not message_template:
            return
        
        if messagebox.askyesno(
            "Confirmar Envío por WhatsApp",
            "¿Está seguro de los datos ingresados?\n\n" +
            "Mensaje a enviar:\n" +
            f"{message_template}\n\n" +
            f"Total de destinatarios: {len(data)}\n\n" +
            "Si está seguro presione 'Sí' para iniciar el envío\n" +
            "Si necesita hacer cambios presione 'No'",
            icon="warning"
        ):
            try:
                # Obtener el código de país seleccionado
                country_code = self.country_selector.get_country_code()
                
                driver = configurar_navegador()
                if esperar_inicio_sesion(driver):
                    registros = []  # Asegurarse que 'registros' está definida antes de cualquier excepción
                    
                    for row in data:
                        telefono = str(row["TELEFONO"]).strip()
                        
                        # Eliminar cualquier punto decimal
                        if telefono.endswith('.0'):
                            telefono = telefono[:-2]
                        
                        # Eliminar cualquier carácter no numérico excepto el +
                        telefono = ''.join(c for c in telefono if c.isdigit() or c == '+')
                        
                        # Verificar si ya tiene código de país o agregarle el seleccionado
                        if not telefono.startswith('+'):
                            telefono = f"{country_code}{telefono}"
                        
                        try:
                            mensaje = message_template.format(**row)
                            registro = enviar_mensaje(driver, telefono, mensaje)
                            registros.append(registro)
                        except KeyError as e:
                            messagebox.showerror(
                                "Error", 
                                f"Variable {str(e)} no encontrada en los datos"
                            )
                            driver.quit()  # Cerrar el navegador antes de salir
                            return
                
                exitosos = sum(1 for r in registros if r['confirmado'])
                guardar_registro(registros)
                messagebox.showinfo(
                    "Completado",
                    f"Mensajes enviados: {exitosos}/{len(data)}"
                )
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                if 'driver' in locals():
                    driver.quit()

    def start_sms_process(self):
        """Inicia el proceso de envío por SMS"""
        data, message_template = self.get_message_data()
        if not data or not message_template:
            return
        
        if messagebox.askyesno(
            "Confirmar Envío por SMS",
            "¿Está seguro de los datos ingresados?\n\n" +
            "Mensaje a enviar:\n" +
            f"{message_template}\n\n" +
            f"Total de destinatarios: {len(data)}\n\n" +
            "Si está seguro presione 'Sí' para iniciar el envío\n" +
            "Si necesita hacer cambios presione 'No'",
            icon="warning"
        ):
            try:
                # Para el caso de SMS, también usamos el selector de país
                country_code = self.country_selector.get_country_code()
                
                messagebox.showinfo(
                    "Próximamente",
                    "La función de envío por SMS estará disponible próximamente.\n" +
                    "Por favor, use la opción de WhatsApp por ahora."
                )
            except Exception as e:
                messagebox.showerror("Error", str(e))