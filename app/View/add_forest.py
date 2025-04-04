"""Module for adding forest data in a GUI application.

This module defines the AddForest class, which is a QWidget that allows users to add forest data
by selecting various parameters and a file. The class includes methods for creating the GUI elements,
validating user input, and handling file selection.
"""

import shutil
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
    QFileDialog,
)

from PySide6.QtGui import QColor, QPalette, QCloseEvent
from PySide6.QtCore import Signal
from app.background_information.Paths import Paths
from ..background_information.Reference_data import ReferenceData


class AddForest(QWidget):
    """A class representing a form for adding forest data.

    This class inherits from QWidget and provides a user interface for selecting
    various parameters related to forest data, including area, breed, and condition.
    It also allows the user to select a file and submit the form.
    """

    form_closed = Signal()

    _name_edit_field = None
    _code_edit_field = None
    _age_edit_field = None
    _age_save_edit_field = None
    _file_path = None

    def __init__(self) -> None:
        """Initializes the AddForest form.

        Sets up the main window, layout, and UI elements.
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

        fields = self._get_fields()
        layout.addWidget(fields)

        buttons_panel = self._get_buttons()
        layout.addWidget(buttons_panel)

        self.setLayout(layout)

        pass

    def _get_fields(self) -> QWidget:
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
        area_combo.addItems(ReferenceData.get_list_areas())
        self.area_combo = area_combo
        layout.addWidget(area_combo)

        breed_combo = QComboBox()
        breed_combo.addItems(ReferenceData.get_list_breeds())
        self.breed_combo = breed_combo
        layout.addWidget(breed_combo)

        condition_combo = QComboBox()
        condition_combo.addItems(ReferenceData.get_list_type_conditions())
        self.condition_combo = condition_combo
        layout.addWidget(condition_combo)

        # Создаем горизонтальный контейнер для поля ввода и кнопки
        file_container = QWidget()
        self._file_container_from = file_container
        file_layout = QHBoxLayout(file_container)
        file_layout.setContentsMargins(0, 0, 0, 0)

        # Поле для отображения пути к файлу
        file_path_input = QLineEdit()
        file_path_input.setPlaceholderText("Путь к файлу...")
        file_path_input.setReadOnly(True)
        file_layout.addWidget(file_path_input)

        # Кнопка выбора файла
        browse_button = QPushButton("Обзор")
        browse_button.clicked.connect(lambda: self._browse_file(file_path_input))
        file_layout.addWidget(browse_button)

        layout.addWidget(file_container)

        return main_widget

    def _browse_file(self, file_input: QLineEdit):
        file_name, _ = QFileDialog.getOpenFileName(None, "Выберите файл", "", ".tar файлы (*.tar);;Все файлы (*.*)")
        if file_name:
            file_input.setText(file_name)
            self._file_path = Path(file_name)

    def _get_buttons(self) -> QWidget:
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
        btn_add.clicked.connect(lambda: self._add_graphic())
        layout.addWidget(btn_add)

        return main_widget

    def _check_parameters(self) -> bool:
        flag_error = False
        if not self._file_path:
            self._file_container_from.setStyleSheet("border: 1px solid red; border-radius: 5px; padding: 2px;")
            flag_error = True
        else:
            self._file_container_from.setStyleSheet("border: none; border-radius: 5px; padding: 2px;")
        if ReferenceData.get_value_graphic(
            name_area=self.area_combo.currentText(),
            name_breed=self.breed_combo.currentText(),
            name_condition=self.condition_combo.currentText(),
        ):
            self.area_combo.setStyleSheet("border: 1px solid red; border-radius: 5px; padding: 2px;")
            self.breed_combo.setStyleSheet("border: 1px solid red; border-radius: 5px; padding: 2px;")
            self.condition_combo.setStyleSheet("border: 1px solid red; border-radius: 5px; padding: 2px;")
            flag_error = True
        else:
            self.area_combo.setStyleSheet("border: none; border-radius: 5px; padding: 2px;")
            self.breed_combo.setStyleSheet("border: none; border-radius: 5px; padding: 2px;")
            self.condition_combo.setStyleSheet("border: none; border-radius: 5px; padding: 2px;")
        return flag_error

    def _add_graphic(self):
        if self._check_parameters():
            return
        # Получаем выбранные значения
        area = self.area_combo.currentText()
        breed = self.breed_combo.currentText()
        condition = self.condition_combo.currentText()

        # Формируем имя файла
        file_name = (
            f"{ReferenceData.get_value_area(area)}_"
            f"{ReferenceData.get_value_breed(breed)}_"
            f"{ReferenceData.get_value_types_conditions(condition)}.tar"
        )

        if not Paths.DATA_DIRECTORY.exists():
            Paths.DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)

        # Путь для нового файла
        target_path = Paths.DATA_DIRECTORY / file_name

        try:
            shutil.copy(self._file_path, target_path)
        except Exception as e:
            raise RuntimeError(f"Error copy file: {e}")

        ReferenceData.add_graphic(
            name_areas=area,
            name_breed=breed,
            name_condition=condition,
            path_file_data=file_name,
        )

        self.close()

        pass

    def closeEvent(self, event: QCloseEvent) -> None:
        """Closed event handler for the AddForest widget.

        This method is called when the widget is closed. It emits a signal to notify
        other components that the form has been closed.

        Args:
            event: The close event object.
        """
        self.form_closed.emit()
        super().closeEvent(event)
