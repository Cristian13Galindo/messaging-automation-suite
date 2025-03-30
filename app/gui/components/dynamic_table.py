import pandas as pd
import customtkinter as ctk
from tkinter import ttk

class DynamicTable(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Tabla
        self.table = ttk.Treeview(self, selectmode="extended")
        self.table.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbars
        self.y_scroll = ttk.Scrollbar(self, orient="vertical", command=self.table.yview)
        self.y_scroll.pack(side="right", fill="y")
        
        self.x_scroll = ttk.Scrollbar(self, orient="horizontal", command=self.table.xview)
        self.x_scroll.pack(side="bottom", fill="x")
        
        self.table.configure(
            yscrollcommand=self.y_scroll.set,
            xscrollcommand=self.x_scroll.set
        )
        
        # Inicializar con columna TELEFONO y fila vacía
        self.table["columns"] = ("TELEFONO",)
        self.table.column("#0", width=0, stretch=False)
        self.table.column("TELEFONO", anchor="w", width=120)
        self.table.heading("TELEFONO", text="TELEFONO")
        self.add_empty_row()
        
        # Botones de control
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.pack(fill="x", padx=5, pady=5)
        
        self.add_column_btn = ctk.CTkButton(
            self.control_frame,
            text="+ Agregar Columna",
            command=self.add_column
        )
        self.add_column_btn.pack(side="left", padx=5)
        
        self.add_row_btn = ctk.CTkButton(
            self.control_frame,
            text="+ Agregar Fila",
            command=self.add_empty_row
        )
        self.add_row_btn.pack(side="left", padx=5)

    def load_excel(self, filename):
        """Carga datos desde Excel y muestra vista previa"""
        try:
            # Cargar datos
            df = pd.read_excel(filename)
            
            # Convertir nombres de columnas a mayúsculas
            df.columns = df.columns.str.upper()
            
            # Configurar columnas
            self.table["columns"] = tuple(df.columns)
            self.table.column("#0", width=0, stretch=False)  # Ocultar primera columna
            
            # Configurar cada columna
            for col in df.columns:
                self.table.column(col, anchor="w", width=120)
                self.table.heading(col, text=col)
                
            # Limpiar datos existentes
            for item in self.table.get_children():
                self.table.delete(item)
                
            # Insertar nuevos datos
            for _, row in df.iterrows():
                values = tuple(str(val) for val in row.values)  # Convertir todos los valores a string
                self.table.insert("", "end", values=values)
            
            print(f"Datos cargados: {len(df)} filas")  # Para debugging
            
        except Exception as e:
            print(f"Error en load_excel: {str(e)}")  # Para debugging
            raise  # Re-lanzar la excepción para manejo superior

    def add_empty_row(self):
        """Agrega una fila vacía al final"""
        values = [""] * len(self.table["columns"])
        self.table.insert("", "end", values=values)

    def add_column(self):
        """Agregar nueva columna"""
        dialog = ctk.CTkInputDialog(
            title="Nueva Columna",
            text="Nombre de la columna:"
        )
        column_name = dialog.get_input()
        if column_name:
            columns = list(self.table["columns"])
            columns.append(column_name.upper())
            self.table["columns"] = columns
            
            # Reconfigurar todas las columnas
            for col in columns:
                self.table.column(col, anchor="w", width=120)
                self.table.heading(col, text=col)
                
            # Actualizar filas existentes con valor vacío para nueva columna
            for item in self.table.get_children():
                values = list(self.table.item(item)["values"])
                values.append("")
                self.table.item(item, values=values)