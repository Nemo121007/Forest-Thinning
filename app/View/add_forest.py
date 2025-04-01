"""A QWidget-based class for adding forest data through a graphical user interface.

This class provides a form with various input fields for forest-related data including
area selection, breed selection, condition selection, and file upload capabilities.

Attributes:
    name_edit_field (QLineEdit): Field for editing forest name
    _code_edit_field (QLineEdit): Field for editing forest code
    _age_edit_field (QLineEdit): Field for editing forest age
    _age_save_edit_field (QLineEdit): Field for editing forest age save data

Methods:
    __init__(): Initializes the AddForest widget with basic layout and components
    _name_form(): Creates and returns the title label widget
    _get_fields(): Creates and returns the main input fields widget
    _browse_file(file_input): Handles file selection through a file dialog
    _get_buttons(): Creates and returns the button panel widget

The window includes:
    - A white background
    - A title section
    - Multiple dropdown menus for area, breed, and condition selection
    - A file upload section with browse capability
    - Action buttons at the bottom
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
    QFileDialog,
)

from PySide6.QtGui import QColor, QPalette


class AddForest(QWidget):
    """A QWidget class for adding forest data through a graphical user interface.

    This class provides a form interface for adding forest-related information, including
    area selection, breed selection, condition selection, and file upload capabilities.

    Attributes:
        _name_edit_field (QLineEdit): Field for editing forest name.
        _code_edit_field (QLineEdit): Field for editing forest code.
        _age_edit_field (QLineEdit): Field for editing forest age.
        _age_save_edit_field (QLineEdit): Field for editing forest age save data.

    Methods:
        _name_form(): Creates and returns the title label widget.
        _get_fields(): Creates and returns the main form fields widget.
        _browse_file(file_input): Handles file selection dialog for Excel files.
        _get_buttons(): Creates and returns the button panel widget.
    """

    _name_edit_field = None
    _code_edit_field = None
    _age_edit_field = None
    _age_save_edit_field = None

    def __init__(self) -> None:
        """Initialize the AddForest window for adding new forest records.

        This window provides a form for entering forest details including name and other fields.
        Sets up the main window properties, background color, and layout structure with:
        - Name input form
        - Forest parameter fields
        - Control buttons panel

        Window Specifications:
            Title: "Добавить лес" (Add Forest)
            Size: 600x500 pixels
            Position: 100,100
            Background: White

        Returns:
            None
        """
        super().__init__()
        self.setWindowTitle("Добавить лес")
        self.setGeometry(100, 100, 600, 500)

        # Главный фон
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("white"))
        self.setPalette(palette)

        # Основная вертикальная компоновка
        layout = QVBoxLayout()

        name_form = AddForest._name_form()
        layout.addWidget(name_form)

        fields = AddForest._get_fields()
        layout.addWidget(fields)

        buttons_panel = AddForest._get_buttons()
        layout.addWidget(buttons_panel)

        self.setLayout(layout)

        pass

    @staticmethod
    def _name_form() -> QWidget:
        """Creates and returns a QWidget containing a label for forest addition.

        Returns:
            QWidget: A QLabel widget with text "Добавить лес" (Add forest).
        """
        label = QLabel("Добавить лес")

        return label

    @staticmethod
    def _get_fields() -> QWidget:
        """Creates and returns a QWidget containing a form with various input fields.

        The form includes:
        - Three QComboBox widgets for area, breed, and condition selection
        - A file selection interface consisting of:
            - A read-only QLineEdit for displaying the selected file path
            - A browse button that triggers file selection dialogue

        Returns:
                QWidget: A widget containing all form elements arranged vertically
        """
        main_widget = QWidget()

        layout = QVBoxLayout(main_widget)

        area_combo = QComboBox()
        area_combo.addItems(["Элемент 1", "Элемент 2", "Элемент 3"])
        layout.addWidget(area_combo)

        breed_combo = QComboBox()
        breed_combo.addItems(["Элемент 1", "Элемент 2", "Элемент 3"])
        layout.addWidget(breed_combo)

        condition_combo = QComboBox()
        condition_combo.addItems(["Элемент 1", "Элемент 2", "Элемент 3"])
        layout.addWidget(condition_combo)

        # Создаем горизонтальный контейнер для поля ввода и кнопки
        file_container = QWidget()
        file_layout = QHBoxLayout(file_container)
        file_layout.setContentsMargins(0, 0, 0, 0)

        # Поле для отображения пути к файлу
        file_path_input = QLineEdit()
        file_path_input.setPlaceholderText("Путь к файлу...")
        file_path_input.setReadOnly(True)
        file_layout.addWidget(file_path_input)

        # Кнопка выбора файла
        browse_button = QPushButton("Обзор")
        browse_button.clicked.connect(lambda: AddForest._browse_file(file_path_input))
        file_layout.addWidget(browse_button)

        layout.addWidget(file_container)

        return main_widget

    @staticmethod
    def _browse_file(file_input: QLineEdit):
        """Opens a file dialog for selecting Excel files and updates the provided QLineEdit with the selected file path.

        Args:
            file_input (QLineEdit): The QLineEdit widget to update with the selected file path.

        Returns:
            None

        Notes:
            - Displays a file dialog filtered for Excel files (.xlsx, .xls) by default
            - Also allows selecting all file types
            - If user cancels selection, original text in QLineEdit remains unchanged
            - Dialog title is in Russian ("Выберите файл")
        """
        file_name, _ = QFileDialog.getOpenFileName(
            None, "Выберите файл", "", "Excel файлы (*.xlsx *.xls);;Все файлы (*.*)"
        )
        if file_name:
            file_input.setText(file_name)

    @staticmethod
    def _get_buttons() -> QWidget:
        """Returns a QWidget containing two buttons for adding and cancelling.

        This method creates and configures a horizontal layout with two buttons:
        - A cancel button
        - An add button
        Both buttons are styled with a green background color (#D5E8D4) and have a fixed height of 50 pixels.

        Returns:
            QWidget: A widget containing the two styled buttons in a horizontal layout
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
