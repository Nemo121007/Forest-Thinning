"""Module for adding forest graphics in a PySide6-based GUI application.

This module provides the AddForest class, which allows users to create new forest graphic
entries by selecting an area, breed, condition, and a .tar file. It validates inputs and
interacts with services to persist the graphic data.
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtGui import QPalette, QCloseEvent
from PySide6.QtCore import Signal
from ..Services.AreasService import AreasService
from ..Services.BreedsService import BreedsService
from ..Services.ConditionsService import ConditionsService
from ..Services.GraphicsService import GraphicsService
from ..background_information.SettingView import SettingsView


class AddForest(QWidget):
    """A form for adding forest graphics in a PySide6-based GUI application.

    This class provides a user interface for creating new forest graphic entries. Users
    select an area, breed, and condition from dropdowns and specify a .tar file. The form
    validates inputs, applies styles from SettingsView, and uses GraphicsService to persist
    the data.

    Attributes:
        form_closed (Signal): Emitted when the form is closed.
        manager_areas (AreasService): Service for managing Area elements.
        manager_breeds (BreedsService): Service for managing Breed elements.
        manager_conditions (ConditionsService): Service for managing Condition elements.
        manager_graphics (GraphicsService): Service
        for managing graphic entries.
        area_combo (QComboBox): Dropdown for selecting an area.
        breed_combo (QComboBox): Dropdown for selecting a breed.
        condition_combo (QComboBox): Dropdown for selecting a condition.
        _file_path (Path | None): Path to the selected .tar file, defaults to None.
        _file_container_form (QWidget): Container for the file input field and browse button.
    """

    form_closed = Signal()

    _file_path = None

    def __init__(self) -> None:
        """Initialize the AddForest form with UI elements and services.

        Sets up the window with a title, geometry, and background color from SettingsView.
        Initializes services for areas, breeds, conditions, and graphics. Configures the
        layout with input fields (dropdowns and file selector) and buttons.

        Returns:
            None
        """
        super().__init__()

        self.manager_areas = AreasService()
        self.manager_breeds = BreedsService()
        self.manager_conditions = ConditionsService()
        self.manager_graphics = GraphicsService()

        self.setWindowTitle("Добавить лес")
        self.setGeometry(100, 100, 600, 500)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, SettingsView.main_background_filling_color)
        self.setPalette(palette)

        layout = QVBoxLayout()

        fields = self._get_fields()
        layout.addWidget(fields)

        buttons_panel = self._get_buttons()
        layout.addWidget(buttons_panel)

        self.setLayout(layout)

    def _get_fields(self) -> QWidget:
        """Create and configure the input fields for the form.

        Returns a widget containing dropdowns for area, breed, and condition, styled with
        SettingsView.background_color, and a file selection interface with a read-only text
        field and a browse button.

        Returns:
            QWidget: A widget containing the configured input fields arranged vertically.
        """
        main_widget = QWidget()

        layout = QVBoxLayout(main_widget)

        area_combo = QComboBox()
        area_combo.setStyleSheet(SettingsView.background_color)
        area_combo.addItems(self.manager_areas.get_list_areas())
        self.area_combo = area_combo
        layout.addWidget(area_combo)

        breed_combo = QComboBox()
        breed_combo.setStyleSheet(SettingsView.background_color)
        breed_combo.addItems(self.manager_breeds.get_list_breeds())
        self.breed_combo = breed_combo
        layout.addWidget(breed_combo)

        condition_combo = QComboBox()
        condition_combo.setStyleSheet(SettingsView.background_color)
        condition_combo.addItems(self.manager_conditions.get_list_conditions())
        self.condition_combo = condition_combo
        layout.addWidget(condition_combo)

        file_container = QWidget()
        self._file_container_form = file_container
        file_layout = QHBoxLayout(file_container)
        file_layout.setContentsMargins(0, 0, 0, 0)

        file_path_input = QLineEdit()
        file_path_input.setStyleSheet(SettingsView.edit_form)
        file_path_input.setPlaceholderText("Путь к файлу...")
        file_path_input.setReadOnly(True)
        file_layout.addWidget(file_path_input)

        browse_button = QPushButton("Обзор")
        browse_button.setStyleSheet(SettingsView.background_color_button)
        browse_button.clicked.connect(lambda: self._browse_file(file_path_input))
        file_layout.addWidget(browse_button)

        layout.addWidget(file_container)

        return main_widget

    def _browse_file(self, file_input: QLineEdit):
        """Open a file dialog to select a .tar file and update the input field.

        Updates the file_input field with the selected file path and stores the path
        in _file_path.

        Args:
            file_input (QLineEdit): The text field to display the selected file path.

        Returns:
            None
        """
        file_name, _ = QFileDialog.getOpenFileName(None, "Выберите файл", "", ".tar файлы (*.tar);;Все файлы (*.*)")
        if file_name:
            file_input.setText(file_name)
            self._file_path = Path(file_name)

    def _get_buttons(self) -> QWidget:
        """Create and configure the cancel and add buttons for the form.

        Returns a widget containing a cancel button (closes the form) and an add button
        (triggers _add_graphic), styled with SettingsView.back_button_color and
        SettingsView.background_color_button respectively.

        Returns:
            QWidget: A widget containing the configured buttons arranged horizontally.
        """
        main_widget = QWidget()
        layout = QHBoxLayout(main_widget)

        btn_cancel = QPushButton("Отмена")
        btn_cancel.setFixedHeight(50)
        btn_cancel.setStyleSheet(SettingsView.back_button_color)
        btn_cancel.clicked.connect(lambda: self.close())
        layout.addWidget(btn_cancel)

        btn_add = QPushButton("Добавить")
        btn_add.setFixedHeight(50)
        btn_add.setStyleSheet(SettingsView.background_color_button)
        btn_add.clicked.connect(lambda: self._add_graphic())
        layout.addWidget(btn_add)

        return main_widget

    def _check_parameters(self) -> bool:
        """Validate the form inputs.

        Checks that an area, breed, condition, and file path are selected and that the
        combination of area, breed, and condition does not already exist in GraphicsService.
        Applies red borders (SettingsView.error_border) to invalid fields and gray borders
        (SettingsView.true_border) to valid ones.

        Returns:
            bool: True if all inputs are valid and the graphic does not exist, False otherwise.
        """
        flag_error = True
        if not self._file_path:
            self._file_container_form.setStyleSheet(SettingsView.error_border)
            flag_error = False
        else:
            self._file_container_form.setStyleSheet(SettingsView.true_border)

        if not self.area_combo.currentText():
            self.area_combo.setStyleSheet(SettingsView.error_border)
            flag_error = False
        else:
            self.area_combo.setStyleSheet(SettingsView.true_border)
        if not self.breed_combo.currentText():
            self.breed_combo.setStyleSheet(SettingsView.error_border)
            flag_error = False
        else:
            self.breed_combo.setStyleSheet(SettingsView.true_border)
        if not self.condition_combo.currentText():
            self.condition_combo.setStyleSheet(SettingsView.error_border)
            flag_error = False
        else:
            self.condition_combo.setStyleSheet(SettingsView.true_border)

        if self.manager_graphics.exist_graphic(
            name_area=self.area_combo.currentText(),
            name_breed=self.breed_combo.currentText(),
            name_condition=self.condition_combo.currentText(),
        ):
            self.area_combo.setStyleSheet(SettingsView.error_border)
            self.breed_combo.setStyleSheet(SettingsView.error_border)
            self.condition_combo.setStyleSheet(SettingsView.error_border)
            flag_error = False
        return flag_error

    def _add_graphic(self):
        """Add a new forest graphic entry.

        Validates inputs using _check_parameters. If valid, adds the graphic via
        GraphicsService and closes the form. If invalid, exits early. Displays an error
        message if GraphicsService raises an exception.

        Returns:
            None

        Raises:
            Exception: If an error occurs during the addition process in GraphicsService.
        """
        if not self._check_parameters():
            return
        area = self.area_combo.currentText()
        breed = self.breed_combo.currentText()
        condition = self.condition_combo.currentText()

        try:
            self.manager_graphics.add_graphic(
                name_area=area, name_breed=breed, name_condition=condition, path_file=self._file_path
            )
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при сохранении: {str(e)}")

        self.close()

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
