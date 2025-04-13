"""Module for creating a base form for managing elements in a PySide6-based GUI application.

This module defines the ElementForm class, a base widget for creating and editing elements
of type Area, Breed, or Condition. It provides a customizable form with fields and buttons,
serving as a foundation for derived classes like UpdateForm.
"""

from typing import Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLineEdit
from PySide6.QtGui import QColor, QPalette, QCloseEvent
from PySide6.QtCore import Signal
from ..background_information.Type_settings import TypeSettings


class ElementForm(QWidget):
    """A base form widget for managing elements in a PySide6-based GUI application.

    This class provides a generic form interface with fields for name, code, and optional
    breed-specific inputs (age thinning and age thinning save). It includes save and cancel
    buttons and emits a signal when closed. Subclasses must implement the _save_element method.

    Attributes:
        form_closed (Signal): Emitted when the form is closed.
        type_settings (TypeSettings): The type of element (AREA, BREED, or CONDITION).
        form_name (QLineEdit): Input field for the element's name.
        form_code_name (QLineEdit): Input field for the element's code.
        form_age_input (QLineEdit, optional): Input field for breed age thinning (BREED only).
        form_age_save_input (QLineEdit, optional): Input field for breed age thinning save (BREED only).
    """

    form_closed = Signal()

    def __init__(self, type_settings: TypeSettings, **kwargs: Any):
        """Initialize the ElementForm with specified type settings.

        Sets up the form's geometry, background, and UI components based on the provided
        type settings.

        Args:
            type_settings (TypeSettings): The type of element (AREA, BREED, or CONDITION).
            **kwargs: Additional keyword arguments passed to the parent QWidget constructor.
        """
        super().__init__()
        self.type_settings = type_settings
        self.setGeometry(100, 100, 600, 500)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("white"))
        self.setPalette(palette)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the form's user interface.

        Creates a vertical layout containing the input fields and button panel.

        Returns:
            None
        """
        layout = QVBoxLayout()
        fields = self._get_fields()
        layout.addWidget(fields)
        buttons_panel = self._get_buttons()
        layout.addWidget(buttons_panel)
        self.setLayout(layout)

    def _get_fields(self) -> QWidget:
        """Create and configure the input fields for the form.

        Returns a widget containing input fields for name, code, and breed-specific fields
        (age thinning and age thinning save) if applicable.

        Returns:
            QWidget: A widget containing the configured input fields.
        """
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)

        self.form_name = QLineEdit()
        self.form_name.setPlaceholderText(f"Название {self.type_settings.value}")
        self.form_name.setStyleSheet("border: 1px solid gray; border-radius: 5px; padding: 2px;")
        layout.addWidget(self.form_name)

        self.form_code_name = QLineEdit()
        self.form_code_name.setPlaceholderText(f"Код {self.type_settings.value}")
        self.form_code_name.setStyleSheet("border: 1px solid gray; border-radius: 5px; padding: 2px;")
        layout.addWidget(self.form_code_name)

        if self.type_settings == TypeSettings.BREED:
            self.form_age_input = QLineEdit()
            self.form_age_input.setPlaceholderText("Возраст рубки")
            self.form_age_input.setStyleSheet("border: 1px solid gray; border-radius: 5px; padding: 2px;")
            layout.addWidget(self.form_age_input)

            self.form_age_save_input = QLineEdit()
            self.form_age_save_input.setPlaceholderText("Возраст рубки защитного леса")
            self.form_age_save_input.setStyleSheet("border: 1px solid gray; border-radius: 5px; padding: 2px;")
            layout.addWidget(self.form_age_save_input)

        return main_widget

    def _get_buttons(self) -> QWidget:
        """Create and configure the save and cancel buttons for the form.

        Returns a widget containing a cancel button (closes the form) and a save button
        (triggers _save_element).

        Returns:
            QWidget: A widget containing the configured buttons.
        """
        main_widget = QWidget()
        layout = QHBoxLayout(main_widget)

        btn_cancel = QPushButton("Отмена")
        btn_cancel.setFixedHeight(50)
        btn_cancel.setStyleSheet("background-color: #F8CECC; text-align: center;")
        btn_cancel.clicked.connect(self.close)
        layout.addWidget(btn_cancel)

        btn_save = QPushButton("Сохранить")
        btn_save.setFixedHeight(50)
        btn_save.setStyleSheet("background-color: #D5E8D4; text-align: center;")
        btn_save.clicked.connect(self._save_element)
        layout.addWidget(btn_save)

        return main_widget

    def _save_element(self):
        """Save the element data.

        This method must be implemented by subclasses to handle the saving logic.

        Raises:
            NotImplementedError: Always raised, as this method is abstract.
        """
        raise NotImplementedError("Subclasses must implement _save_element")

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle the form close event.

        Emits the form_closed signal and calls the parent class's closeEvent method.

        Args:
            event (QCloseEvent): The close event triggered when the form is closed.

        Returns:
            None
        """
        self.form_closed.emit()
        super().closeEvent(event)
