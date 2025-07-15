import customtkinter as ctk
from tkinter import StringVar

class CountrySelector(ctk.CTkFrame):
    """Selector de país con búsqueda para códigos telefónicos"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Inicializar atributos
        self.dropdown_visible = False  # Añadir esta línea
        self.dropdown = None
    
        # Cargar datos de países
        self.countries = self.load_countries()
        
        # Variables
        self.selected_country = StringVar(value="Colombia (+57)")
        self.selected_code = "+57"  # Valor por defecto
        
        # Crear interfaz
        self.create_widgets()
        
    def load_countries(self):
        """Carga lista de países con sus códigos"""
        # Lista básica de países populares con sus códigos
        return [
            {"name": "Argentina", "code": "+54"},
            {"name": "Bolivia", "code": "+591"},
            {"name": "Brasil", "code": "+55"},
            {"name": "Chile", "code": "+56"},
            {"name": "Colombia", "code": "+57"},
            {"name": "Costa Rica", "code": "+506"},
            {"name": "Cuba", "code": "+53"},
            {"name": "Ecuador", "code": "+593"},
            {"name": "El Salvador", "code": "+503"},
            {"name": "España", "code": "+34"},
            {"name": "Estados Unidos", "code": "+1"},
            {"name": "Guatemala", "code": "+502"},
            {"name": "Honduras", "code": "+504"},
            {"name": "México", "code": "+52"},
            {"name": "Nicaragua", "code": "+505"},
            {"name": "Panamá", "code": "+507"},
            {"name": "Paraguay", "code": "+595"},
            {"name": "Perú", "code": "+51"},
            {"name": "Portugal", "code": "+351"},
            {"name": "República Dominicana", "code": "+1"},
            {"name": "Uruguay", "code": "+598"},
            {"name": "Venezuela", "code": "+58"}
        ]
    
    def create_widgets(self):
        """Crea los widgets del selector"""
        # Etiqueta
        self.label = ctk.CTkLabel(self, text="País:")
        self.label.pack(side="left", padx=(0, 5))
        
        # Campo de búsqueda/selección
        self.search_var = StringVar()
        self.search_var.trace("w", self.update_dropdown)
        
        self.search_entry = ctk.CTkEntry(self, textvariable=self.search_var, width=150)
        self.search_entry.insert(0, "Colombia")  # Valor por defecto
        self.search_entry.pack(side="left")
        
        # Botón de dropdown
        self.dropdown_btn = ctk.CTkButton(
            self, text="▼", width=20, command=self.toggle_dropdown
        )
        self.dropdown_btn.pack(side="left")
        
        # Dropdown oculto inicialmente
        self.dropdown_visible = False
        self.dropdown = None
        
    def toggle_dropdown(self):
        """Muestra/oculta el dropdown"""
        if self.dropdown_visible:
            self.hide_dropdown()
        else:
            self.show_dropdown()
    
    def show_dropdown(self):
        """Muestra el dropdown con países filtrados"""
        # Crear ventana dropdown
        self.dropdown = ctk.CTkToplevel(self)
        self.dropdown.geometry(f"{300}x{250}+{self.winfo_rootx()}+{self.winfo_rooty() + 30}")
        self.dropdown.overrideredirect(True)
        self.dropdown.attributes("-topmost", True)
        
        # Lista de países
        self.country_frame = ctk.CTkScrollableFrame(self.dropdown, width=280, height=230)
        self.country_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Filtrar y mostrar países
        self.update_country_list()
        
        self.dropdown_visible = True
        
    def update_country_list(self):
        """Actualiza la lista de países según el filtro"""
        search_text = self.search_var.get().lower()
        
        # Limpiar lista actual
        for widget in self.country_frame.winfo_children():
            widget.destroy()
        
        # Añadir países filtrados
        for country in self.countries:
            if search_text in country["name"].lower():
                btn = ctk.CTkButton(
                    self.country_frame,
                    text=f"{country['name']} ({country['code']})",
                    anchor="w",
                    command=lambda c=country: self.select_country(c)
                )
                btn.pack(fill="x", pady=1)
    
    def update_dropdown(self, *args):
        """Actualiza el dropdown al cambiar el texto de búsqueda"""
        if self.dropdown_visible:
            self.update_country_list()
    
    def select_country(self, country):
        """Selecciona un país del dropdown"""
        self.selected_country.set(f"{country['name']} ({country['code']})")
        self.selected_code = country["code"]
        self.search_var.set(country["name"])
        self.hide_dropdown()
    
    def hide_dropdown(self):
        """Oculta el dropdown"""
        if self.dropdown_visible and self.dropdown is not None:
            self.dropdown.destroy()
            self.dropdown_visible = False
    
    def get_country_code(self):
        """Retorna el código del país seleccionado"""
        return self.selected_code