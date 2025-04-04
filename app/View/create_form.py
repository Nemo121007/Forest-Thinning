"""A Qt widget class for creating a form to add region information.

    This class provides a form interface with input fields for region details such as name,
    code, cutting age, and protective forest cutting age. It includes a main layout with
    three sections: a title label, input fields, and action buttons.

Attributes:
    _name_edit_field (QLineEdit): Field for entering region name.
    _code_edit_field (QLineEdit): Field for entering region code.
    _age_edit_field (QLineEdit): Field for entering cutting age.
    _age_save_edit_field (QLineEdit): Field for entering protective forest cutting age.

Methods:
    _name_form(): Creates and returns the title label widget.
    _get_fields(): Creates and returns the input fields widget.
    _get_buttons(): Creates and returns the action buttons widget.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
)
from PySide6.QtGui import QColor, QPalette, QCloseEvent
from PySide6.QtCore import Signal
from ..background_information.Type_settings import TypeSettings
from ..background_information.Type_action import TypeAction
from ..background_information.Reference_data import ReferenceData
from ..background_information.General_functions import validate_name, validate_float


class CreateForm(QWidget):
    """A class representing a form for creating regions in a PyQt-based GUI application.

    This form provides input fields for region details such as name, code, and cutting ages,
    along with buttons for form submission and cancellation.

    Attributes:
        _name_edit_field (QLineEdit): Field for entering region name
        _code_edit_field (QLineEdit): Field for entering region code
        _age_edit_field (QLineEdit): Field for entering cutting age
        _age_save_edit_field (QLineEdit): Field for entering protective forest cutting age

    Methods:
        _name_form(): Creates and returns the form title label
        _get_fields(): Creates and returns the widget containing all input fields
        _get_buttons(): Creates and returns the widget containing action buttons

    The form layout consists of:
        - A title label "Регионы" (Regions)
        - Input fields for region details
        - Two buttons for form actions (styled with green background).
    """

    form_closed = Signal()  # Добавляем сигнал

    _name_edit_field = None
    _code_edit_field = None
    _age_edit_field = None
    _age_save_edit_field = None

    def __init__(self, type_action: TypeAction, type_settings: TypeSettings, name_element: str = None) -> None:
        """Initialize a new CreateForm window.

        This constructor sets up the main window for adding a new region. It initializes
        the window properties including title, geometry and background color. The window
        contains three main sections:
        - Name form
        - Input fields
        - Button panel
        The layout is organized vertically using QVBoxLayout.

        Returns:
            None
        """
        super().__init__()

        self.type_action = type_action
        self.type_settings = type_settings
        self.name_element = name_element
        if type_action == TypeAction.UPDATE:
            self.old_name_element = name_element
            if type_settings == TypeSettings.AREA:
                self.file_name_element = ReferenceData.get_value_area(name=name_element)
                self.age_thinning = ReferenceData.get_age_thinning_area(name=name_element)
                self.age_thinning_save = ReferenceData.get_age_thinning_save_area(name=name_element)
            elif type_settings == TypeSettings.BREED:
                self.file_name_element = ReferenceData.get_value_breed(name=name_element)
            elif type_settings == TypeSettings.CONDITION:
                self.file_name_element = ReferenceData.get_value_types_conditions(name=name_element)
            self.setWindowTitle(f"Изменение {self.name_element}")
        elif type_action == TypeAction.CREATE:
            self.setWindowTitle(f"Добавление {type_settings.value}")
            self.file_name_element = None
            self.age_thinning = None
            self.age_thinning_save = None
        else:
            raise ValueError("Unidentified type operation")
        self.setGeometry(100, 100, 600, 500)

        # Главный фон
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("white"))
        self.setPalette(palette)

        # Основная вертикальная компоновка
        layout = QVBoxLayout()

        fields = self._get_fields()
        layout.addWidget(fields)

        buttons_panel = self._get_buttons()
        layout.addWidget(buttons_panel)

        self.setLayout(layout)

        pass

    def _get_fields(self) -> QWidget:
        """Creates and returns a widget containing form fields for region information.

        The form includes the following fields:
        - Name input field for region name
        - Code input field for region code
        - Age input field for logging age (conditional)
        - Protected forest age input field (conditional)
        All fields are styled with a gray border and rounded corners.

        Returns:
            QWidget: A widget containing the vertically arranged input fields
        """
        main_widget = QWidget()

        layout = QVBoxLayout(main_widget)

        name_input = QLineEdit()
        self.form_name = name_input
        name_input.setPlaceholderText(f"Название {self.type_settings.value}")  # Подсказка в поле
        if self.type_action == TypeAction.UPDATE:
            name_input.setText(self.name_element)
        name_input.setStyleSheet("border: 1px solid gray; border-radius: 5px; padding: 2px;")
        layout.addWidget(name_input)

        code_input = QLineEdit()
        self.form_code_name = code_input
        code_input.setPlaceholderText(f"Код {self.type_settings.value}")  # Подсказка в поле
        if self.type_action == TypeAction.UPDATE:
            code_input.setText(self.file_name_element)
        code_input.setStyleSheet("border: 1px solid gray; border-radius: 5px; padding: 2px;")
        layout.addWidget(code_input)

        if self.type_settings == TypeSettings.AREA:
            age_input = QLineEdit()
            self.form_age_input = age_input
            age_input.setPlaceholderText("Возраст рубки")  # Подсказка в поле
            if self.type_action == TypeAction.UPDATE:
                age_input.setText(str(self.age_thinning))
            age_input.setStyleSheet("border: 1px solid gray; border-radius: 5px; padding: 2px;")
            layout.addWidget(age_input)
            CreateForm._age_edit_field = age_input

            age_save_input = QLineEdit()
            self.form_age_save_input = age_save_input
            age_save_input.setPlaceholderText("Возраст рубки защитного леса")  # Подсказка в поле
            if self.type_action == TypeAction.UPDATE:
                age_save_input.setText(str(self.age_thinning_save))
            age_save_input.setStyleSheet("border: 1px solid gray; border-radius: 5px; padding: 2px;")
            layout.addWidget(age_save_input)
            CreateForm._age_save_edit_field = age_save_input

        return main_widget

    def _get_buttons(self) -> QWidget:
        """Creates and returns a widget containing two buttons for form actions.

        The widget contains two buttons arranged horizontally:
        - A cancel button
        - An add button
        Both buttons are styled with a light green background color and centered text.

        Returns:
            QWidget: A widget containing the horizontally arranged buttons
        """
        main_widget = QWidget()

        layout = QHBoxLayout(main_widget)

        btn_cancel = QPushButton("")
        btn_cancel.setFixedHeight(50)
        btn_cancel.setStyleSheet("background-color: #F8CECC; text-align: center;")
        btn_cancel.clicked.connect(lambda: self.close())
        layout.addWidget(btn_cancel)

        btn_add = QPushButton("")
        btn_add.setFixedHeight(50)
        btn_add.setStyleSheet("background-color: #D5E8D4; text-align: center;")
        btn_add.clicked.connect(lambda: self._save_element())
        layout.addWidget(btn_add)

        return main_widget

    def _save_element(self):
        # TODO: Валидация
        flag_error = False

        if (
            self.type_settings == TypeSettings.AREA
            and self.type_action == TypeAction.CREATE
            and ReferenceData.get_value_area(name=self.form_name.text()) is not None
        ):
            self.form_name.setStyleSheet("border: 1px solid red; border-radius: 5px; padding: 2px;")
            flag_error = True
        elif (
            self.type_settings == TypeSettings.BREED
            and self.type_action == TypeAction.CREATE
            and ReferenceData.get_value_breed(name=self.form_name.text()) is not None
        ):
            self.form_name.setStyleSheet("border: 1px solid red; border-radius: 5px; padding: 2px;")
            flag_error = True
        elif (
            self.type_settings == TypeSettings.CONDITION
            and self.type_action == TypeAction.CREATE
            and ReferenceData.get_value_types_conditions(name=self.form_name.text()) is not None
        ):
            self.form_name.setStyleSheet("border: 1px solid red; border-radius: 5px; padding: 2px;")
            flag_error = True
        elif not validate_name(self.form_name.text()):
            self.form_name.setStyleSheet("border: 1px solid red; border-radius: 5px; padding: 2px;")
            flag_error = True
        else:
            self.form_name.setStyleSheet("border: none; border-radius: 5px; padding: 2px;")

        if not validate_name(self.form_code_name.text()):
            self.form_code_name.setStyleSheet("border: 1px solid red; border-radius: 5px; padding: 2px;")
            flag_error = True
        else:
            self.form_code_name.setStyleSheet("border: none; border-radius: 5px; padding: 2px;")
        if self.type_settings == TypeSettings.AREA and validate_float(self.form_age_input.text()) is None:
            self.form_age_input.setStyleSheet("border: 1px solid red; border-radius: 5px; padding: 2px;")
            flag_error = True
        elif self.type_settings == TypeSettings.AREA:
            self.form_age_input.setStyleSheet("border: none; border-radius: 5px; padding: 2px;")
        if self.type_settings == TypeSettings.AREA and validate_float(self.form_age_save_input.text()) is None:
            self.form_age_save_input.setStyleSheet("border: 1px solid red; border-radius: 5px; padding: 2px;")
            flag_error = True
        elif self.type_settings == TypeSettings.AREA:
            self.form_age_save_input.setStyleSheet("border: none; border-radius: 5px; padding: 2px;")

        if flag_error:
            return
        else:
            name = self.form_name.text()
            file_name = self.form_code_name.text()
            age_thinning = float(self.form_age_input.text().replace(",", "."))
            age_thinning_save = float(self.form_age_save_input.text().replace(",", "."))

        if self.type_settings == TypeSettings.AREA:
            if self.type_action == TypeAction.CREATE:
                ReferenceData.add_area(
                    area_file_name=file_name,
                    name_area=name,
                    age_thinning=age_thinning,
                    age_thinning_save=age_thinning_save,
                )
            elif self.type_action == TypeAction.UPDATE:
                ReferenceData.update_area(
                    old_name_area=self.old_name_element,
                    area_file_name=file_name,
                    name_area=name,
                    age_thinning=age_thinning,
                    age_thinning_save=age_thinning_save,
                )
        elif self.type_settings == TypeSettings.BREED:
            if self.type_action == TypeAction.CREATE:
                ReferenceData.add_breeds(breed_file_name=name, name_breed=file_name)
            elif self.type_action == TypeAction.UPDATE:
                ReferenceData.update_breeds(
                    old_name_breed=self.old_name_element, breed_file_name=name, name_breed=file_name
                )
        elif self.type_settings == TypeSettings.CONDITION:
            if self.type_action == TypeAction.CREATE:
                ReferenceData.add_type_conditions(condition_file_name=name, name_type_conditions=file_name)
            elif self.type_action == TypeAction.UPDATE:
                ReferenceData.update_type_conditions(
                    old_name_type_condition=self.old_name_element,
                    condition_file_name=name,
                    name_type_conditions=file_name,
                )
        else:
            raise TypeError("Invalid operation")

        self.close()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Override the close event to emit a signal when the form is closed.

        This method is called when the window is closed, and it emits the form_closed signal
        to notify other components that the form has been closed.

        Args:
            event (QCloseEvent): The close event object
        """
        self.form_closed.emit()
        super().closeEvent(event)
