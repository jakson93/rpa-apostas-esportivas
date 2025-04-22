"""
Módulo para inicialização da interface gráfica.

Este módulo contém funções para iniciar a interface gráfica
do sistema de automação de apostas esportivas.
"""
import sys
from PyQt5.QtWidgets import QApplication
from .main_window import MainWindow


def start_gui():
    """
    Inicia a interface gráfica da aplicação.
    
    Returns:
        int: Código de saída da aplicação.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(start_gui())
