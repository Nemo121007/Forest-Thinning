"""Module to start the application."""

from PySide6.QtWidgets import QApplication
import sys

from app.View.main_screen import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
