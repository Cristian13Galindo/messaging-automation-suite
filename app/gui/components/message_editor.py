import customtkinter as ctk
import re

class MessageEditor(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Instrucciones
        instructions = """
        Instrucciones:
        1. Use MAYÚSCULAS para variables: {NOMBRE}, {TELEFONO}
        2. El texto normal va en minúsculas
        3. Ejemplo: "Hola {NOMBRE}, tu cita es el {DIA}"
        """
        self.instructions = ctk.CTkLabel(self, text=instructions, justify="left")
        self.instructions.pack(fill="x", padx=5, pady=5)
        
        # Editor
        self.editor = ctk.CTkTextbox(self, height=150)
        self.editor.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Preview
        preview_frame = ctk.CTkFrame(self)
        preview_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(preview_frame, text="Vista Previa:").pack(anchor="w")
        self.preview = ctk.CTkTextbox(preview_frame, height=100)
        self.preview.pack(fill="x", pady=5)
        self.preview.configure(state="disabled")
        
        # Bind para actualizar preview
        self.editor.bind("<KeyRelease>", self.update_preview)
        
    def update_preview(self, event=None):
        """Actualiza la vista previa con datos reales de la primera fila"""
        message = self.editor.get("1.0", "end-1c")
        
        try:
            # Obtener datos de la primera fila de la tabla
            main_window = self.winfo_toplevel()
            if hasattr(main_window, 'table'):
                first_item = main_window.table.table.get_children()[0]
                if first_item:
                    values = main_window.table.table.item(first_item)["values"]
                    columns = main_window.table.table["columns"]
                    
                    # Crear diccionario con los datos
                    preview_data = dict(zip(columns, values))
                    
                    # Generar vista previa con datos reales
                    preview_text = message.format(**preview_data)
                    
                    self.preview.configure(state="normal")
                    self.preview.delete("1.0", "end")
                    self.preview.insert("1.0", preview_text)
                    self.preview.configure(state="disabled")
                else:
                    self.preview.configure(state="normal")
                    self.preview.delete("1.0", "end")
                    self.preview.insert("1.0", "No hay datos para previsualizar")
                    self.preview.configure(state="disabled")
            
        except Exception as e:
            self.preview.configure(state="normal")
            self.preview.delete("1.0", "end")
            self.preview.insert("1.0", f"Error en formato: {str(e)}")
            self.preview.configure(state="disabled")