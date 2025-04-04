"""The main module of the Forest-Thinning application.

This module contains the application entry point and initializes the main GUI window.
Uses PySide6 to create a graphical interface.
"""

import sys
from PySide6.QtWidgets import QApplication
from app.View.main_screen import MainWindow  # noqa: F401
from app.View.list_graphics_window import ListGraphicsWindow
from app.View.create_form import CreateForm  # noqa: F401
from app.View.add_forest import AddForest  # noqa: F401

if __name__ == "__main__":
    # app = QApplication(sys.argv)
    # window = MainWindow()
    # window.show()
    # sys.exit(app.exec())

    app = QApplication(sys.argv)
    window = ListGraphicsWindow()
    window.show()
    sys.exit(app.exec())

    # app = QApplication(sys.argv)
    # window = CreateForm()
    # window.show()
    # sys.exit(app.exec())

    # app = QApplication(sys.argv)
    # window = AddForest()
    # window.show()
    # sys.exit(app.exec())
