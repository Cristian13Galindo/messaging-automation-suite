import os
from app.gui.main_window import MainWindow
from app.core.whatsapp_bot import verificar_dependencias

def main():
    """Punto de entrada principal de la aplicación"""
    if verificar_dependencias():
        try:
            app = MainWindow()
            app.mainloop()
        except Exception as e:
            print(f"Error iniciando la aplicación: {str(e)}")
    else:
        print("No se puede iniciar la aplicación debido a dependencias faltantes")

if __name__ == "__main__":
    main()