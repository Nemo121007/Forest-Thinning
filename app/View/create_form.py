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
    QLabel,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
)
from PySide6.QtGui import QColor, QPalette


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

    _name_edit_field = None
    _code_edit_field = None
    _age_edit_field = None
    _age_save_edit_field = None

    def __init__(self) -> None:
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
        self.setWindowTitle("Добавление региона")
        self.setGeometry(100, 100, 600, 500)

        # Главный фон
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("white"))
        self.setPalette(palette)

        # Основная вертикальная компоновка
        layout = QVBoxLayout()

        name_form = CreateForm._name_form()
        layout.addWidget(name_form)

        fields = CreateForm._get_fields()
        layout.addWidget(fields)

        buttons_panel = CreateForm._get_buttons()
        layout.addWidget(buttons_panel)

        self.setLayout(layout)

        pass

    @staticmethod
    def _name_form() -> QWidget:
        """Creates and returns a QWidget containing a label for regions.

        Returns:
            QWidget: A QLabel widget displaying "Регионы" (Regions).
        """
        label = QLabel("Регионы")

        return label

    @staticmethod
    def _get_fields() -> QWidget:
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
        name_input.setPlaceholderText("Название региона")  # Подсказка в поле
        name_input.setStyleSheet("border: 1px solid gray; border-radius: 5px; padding: 2px;")
        layout.addWidget(name_input)
        CreateForm._name_edit_field = name_input

        code_input = QLineEdit()
        code_input.setPlaceholderText("Код региона")  # Подсказка в поле
        code_input.setStyleSheet("border: 1px solid gray; border-radius: 5px; padding: 2px;")
        layout.addWidget(code_input)
        CreateForm._code_edit_field = code_input

        # TODO: повесить условие
        if True:
            age_input = QLineEdit()
            age_input.setPlaceholderText("Возраст рубки")  # Подсказка в поле
            age_input.setStyleSheet("border: 1px solid gray; border-radius: 5px; padding: 2px;")
            layout.addWidget(age_input)
            CreateForm._age_edit_field = age_input

            age_save_input = QLineEdit()
            age_save_input.setPlaceholderText("Возраст рубки защитного леса")  # Подсказка в поле
            age_save_input.setStyleSheet("border: 1px solid gray; border-radius: 5px; padding: 2px;")
            layout.addWidget(age_save_input)
            CreateForm._age_save_edit_field = age_save_input

        return main_widget

    @staticmethod
    def _get_buttons() -> QWidget:
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
        btn_cancel.setStyleSheet("background-color: #D5E8D4; text-align: center;")
        layout.addWidget(btn_cancel)

        btn_add = QPushButton("")
        btn_add.setFixedHeight(50)
        btn_add.setStyleSheet("background-color: #D5E8D4; text-align: center;")
        layout.addWidget(btn_add)

        return main_widget
