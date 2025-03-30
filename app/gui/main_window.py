import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
from .components.dynamic_table import DynamicTable
from .components.message_editor import MessageEditor
from app.core.whatsapp_bot import configurar_navegador, esperar_inicio_sesion, enviar_mensaje, guardar_registro

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("WhatsApp Automation")
        self.geometry("1200x800")
        
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
        
        self.select_file_btn = ctk.CTkButton(
            top_panel, 
            text="Importar Excel",
            command=self.select_excel_file
        )
        self.select_file_btn.pack(side="left", padx=5)
        
        self.file_label = ctk.CTkLabel(top_panel, text="No se ha seleccionado archivo")
        self.file_label.pack(side="left", padx=5)
        
        # Panel principal
        main_panel = ctk.CTkFrame(self)
        main_panel.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Tabla dinámica
        self.table = DynamicTable(main_panel)
        self.table.pack(fill="both", expand=True, pady=5)
        
        # Editor de mensajes
        self.message_editor = MessageEditor(main_panel)
        self.message_editor.pack(fill="x", pady=5)
        
        # Botón de envío
        self.start_btn = ctk.CTkButton(
            main_panel,
            text="Iniciar Envío",
            command=self.start_process
        )
        self.start_btn.pack(pady=5)
        
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
            
    def start_process(self):
        """Procesa y envía los mensajes"""
        # Obtener datos de la tabla
        data = []
        for item in self.table.table.get_children():
            values = self.table.table.item(item)["values"]
            if any(values):  # Solo procesar filas con datos
                row_dict = dict(zip(self.table.table["columns"], values))
                data.append(row_dict)
        
        if not data:
            messagebox.showerror("Error", "No hay datos para enviar")
            return
            
        message_template = self.message_editor.editor.get("1.0", "end-1c")
        if not message_template.strip():
            messagebox.showerror("Error", "El mensaje está vacío")
            return
        
        # Nuevo diálogo de confirmación
        confirm = messagebox.askyesno(
            "Confirmar Envío",
            "¿Está seguro de los datos ingresados?\n\n" +
            "Mensaje a enviar:\n" +
            f"{message_template}\n\n" +
            f"Total de destinatarios: {len(data)}\n\n" +
            "Si está seguro presione 'Sí' para iniciar el envío\n" +
            "Si necesita hacer cambios presione 'No'",
            icon="warning"
        )
        
        if confirm:
            try:
                driver = configurar_navegador()
                if esperar_inicio_sesion(driver):
                    registros = []
                    for row in data:
                        telefono = str(row["TELEFONO"]).strip()
                        if not telefono.startswith("+"):
                            telefono = f"+{telefono}"
                        
                        try:
                            mensaje = message_template.format(**row)
                            registro = enviar_mensaje(driver, telefono, mensaje)
                            registros.append(registro)
                        except KeyError as e:
                            messagebox.showerror(
                                "Error", 
                                f"Variable {str(e)} no encontrada en los datos"
                            )
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