"""Module for creating the main application window in a PySide6-based GUI.

This module defines the MainWindow class, which serves as the primary interface for
interacting with area, breed, condition, and graphics data. It includes a header with
action buttons, an info panel with settings, and a main area for plotting graphics and
displaying information blocks.
"""

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QGridLayout,
    QScrollArea,
    QSizePolicy,
    QComboBox,
    QLineEdit,
    QCheckBox,
    QMessageBox,
)
from PySide6.QtGui import QColor, QPalette
from PySide6 import QtGui
from PySide6.QtCore import Qt
import sys
import numpy as np
import pyqtgraph as pg

from .ListGraphicsWindow import ListGraphicsWindow
from ..Services.AreasService import AreasService
from ..Services.BreedsService import BreedsService
from ..Services.ConditionsService import ConditionsService
from ..Services.GraphicsService import GraphicsService
from ..Services.PredictModelServices import PredictModelService
from ..background_information.TypeLine import TypeLine
from ..background_information.TypeSettings import TypeSettings
from ..background_information.Settings import Settings
from ..background_information.General_functions import cast_coordinates_point
from ..background_information.SettingView import SettingsView


class MainWindow(QWidget):
    """The main application window for managing and visualizing graphics data.

    Provides a PySide6-based GUI with a header for actions (e.g., open, save, settings),
    an info panel for selecting area, breed, and condition, and a main area with a plot
    widget for graphics and scrollable information blocks. Supports mouse interactions
    (double-click for thinning events, right-click for bearing points) and uses styles
    from SettingsView and constants from Settings. Interacts with services to manage
    data and predictions.

    Attributes:
        manager_areas (AreasService): Service for managing area data.
        manager_breeds (BreedsService): Service for managing breed data.
        manager_conditions (ConditionsService): Service for managing condition data.
        manager_graphic (GraphicsService): Service for managing graphics data.
        predict_model (PredictModelService): Service for prediction model operations.
        name_area (str): Current area name selected in the UI.
        name_breed (str): Current breed name selected in the UI.
        name_condition (str): Current condition name selected in the UI.
        name_graphic (str): Name of the current graphic (not used in code).
        name_graphic_code (str): Code of the current graphic.
        list_areas (list[str]): List of available area names.
        list_breeds (list[str]): List of available breed names.
        list_conditions (list[str]): List of available condition names.
        flag_save_forest (bool): Flag indicating if protective forest mode is active.
        x_min (float): Minimum x-value for plotting.
        x_max (float): Maximum x-value for plotting.
        y_min (float): Minimum y-value for plotting.
        y_max (float): Maximum y-value for plotting.
        list_value_x (list[float]): List of x-values for plotting.
        list_value_y_min_logging (list[float]): Y-values for minimum logging line.
        list_value_y_max_logging (list[float]): Y-values for maximum logging line.
        list_value_y_min_economic (list[float]): Y-values for minimum economic line.
        form_combo_area (QComboBox): Combo box for selecting areas.
        form_combo_breed (QComboBox): Combo box for selecting breeds.
        form_combo_condition (QComboBox): Combo box for selecting conditions.
        form_scroll_area (QScrollArea): Scroll area for information blocks.
        start_point_edit_field (QLineEdit): Input field for start age (not used in logic).
        area_point_edit_field (QLineEdit): Input field for area (not used in logic).
        save_check_box (QCheckBox): Checkbox for protective forest mode.
        graphic (QWidget): Widget containing the plot.
        graphic_layout (QVBoxLayout): Layout for the plot widget.
        age_thinning (float): Age thinning value for the current breed.
        age_thinning_save (float): Age thinning save value for the current breed.
        start_point (tuple[float, float]): Start point coordinates for bearing line.
        list_value_y_bearing_line (list[float]): Y-values for bearing line.
        list_value_track_thinning (list[float]): Data for thinning prediction line.
        list_record_planned_thinning (list[dict[str, float]]): List of planned thinning records.
        predict_line_item (pg.PlotDataItem): Plot item for the thinning prediction line.
    """

    def __init__(self):
        """Initialize the MainWindow.

        Sets up the window title, geometry, background color from SettingsView, and UI
        components (header, info panel, main content). Initializes services, attributes
        (e.g., start_point, predict_line_item), and calls replace_graphic to load initial
        data and plot.

        Returns:
            None
        """
        super().__init__()

        self.manager_areas = AreasService()
        self.manager_breeds = BreedsService()
        self.manager_conditions = ConditionsService()
        self.manager_graphic = GraphicsService()
        self.predict_model = PredictModelService()

        self.name_area: str = None
        self.name_breed: str = None
        self.age_thinning: float = None
        self.age_thinning_save: float = None
        self.name_condition: str = None
        self.name_graphic: str = None
        self.name_graphic_code: str = None
        self.list_areas: list[str] = None
        self.list_breeds: list[str] = None
        self.list_conditions: list[str] = None
        self.flag_save_forest: bool = False
        self.x_min: float = None
        self.x_max: float = None
        self.y_min: float = None
        self.y_max: float = None
        self.start_point: tuple[float, float] = None
        self.list_value_x: list[float] = None
        self.list_value_y_min_logging: list[float] = None
        self.list_value_y_max_logging: list[float] = None
        self.list_value_y_min_economic: list[float] = None

        self.list_value_y_bearing_line: list[float] = None
        self.list_value_track_thinning: list[float] = None
        self.list_record_planned_thinning: list[dict[str, float]] = None

        self.predict_line_item = None  # Атрибут для хранения линии прогнозируемой рубки

        self.setWindowTitle("Прототип экрана")
        self.setGeometry(0, 0, 1024, 768)  # Окно

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(SettingsView.main_background_filling_color))
        self.setPalette(palette)

        layout = QVBoxLayout()

        header = self.create_header()
        layout.addWidget(header)

        info = self.create_info()
        layout.addWidget(info)

        content = self.create_main_part()
        layout.addWidget(content)

        self.setLayout(layout)

        self.replace_graphic()

    def create_header(self) -> QWidget:
        """Create the header panel with action buttons.

        Constructs a header with buttons for opening, saving, saving as, accessing graphics
        lists, and settings, styled with SettingsView.background_color_button. Note that
        'Open', 'Save', 'Save As', and 'Settings' buttons are not connected to actions.

        Returns:
            QWidget: The header widget containing buttons.
        """
        header = QWidget()
        header.setFixedHeight(30)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(5, 0, 5, 0)

        # Добавляем кнопки слева
        btn_open = QPushButton("Открыть")
        btn_open.setFixedWidth(150)
        btn_open.setStyleSheet(SettingsView.background_color_button)
        btn_save = QPushButton("Сохранить")
        btn_save.setFixedWidth(150)
        btn_save.setStyleSheet(SettingsView.background_color_button)
        btn_save_as = QPushButton("Сохранить как")
        btn_save_as.setFixedWidth(150)
        btn_save_as.setStyleSheet(SettingsView.background_color_button)

        header_layout.addWidget(btn_open)
        header_layout.addWidget(btn_save)
        header_layout.addWidget(btn_save_as)

        # Добавляем растягивающийся элемент
        header_layout.addStretch()

        # Добавляем кнопки справа
        btn_list_graphics = QPushButton("Список графиков")
        btn_list_graphics.setFixedWidth(150)
        btn_list_graphics.setStyleSheet(SettingsView.background_color_button)
        btn_list_graphics.clicked.connect(self.open_list_graphics)

        btn_settings = QPushButton("Настройки")
        btn_settings.setFixedWidth(150)
        btn_settings.setStyleSheet(SettingsView.background_color_button)
        header_layout.addWidget(btn_list_graphics)
        header_layout.addWidget(btn_settings)

        return header

    def open_list_graphics(self) -> None:
        """Open the list graphics window.

        Creates and displays a ListGraphicsWindow, styled with SettingsView, for viewing
        available graphics. Connects the form_closed signal to replace_graphic to refresh
        the plot upon closing.

        Returns:
            None
        """
        self.list_graphics_window = ListGraphicsWindow()
        self.list_graphics_window.form_closed.connect(lambda: self.replace_graphic())
        self.list_graphics_window.show()

    def create_info(self) -> QWidget:
        """Create the info panel with parameter selection.

        Constructs a panel with combo boxes for selecting area, breed, condition, and a
        checkbox for protective forest status, styled with SettingsView.background_color
        and SettingsView.checkbox_style. Includes input fields for forestry details
        (e.g., 'Лесничество', 'Квартал') that are not used in the current logic.

        Returns:
            QWidget: The info panel widget containing parameter controls.
        """
        info = QWidget()
        info.setFixedHeight(110)

        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(5, 5, 5, 5)

        main_setting_widget = QWidget()
        main_setting_widget.setFixedWidth(331)

        main_setting = QGridLayout()

        # Виджет для лесного района
        forest_widget = QVBoxLayout()
        forest_area = QLabel("Лесной район")
        forest_combo = QComboBox()
        forest_combo.setStyleSheet(SettingsView.background_color)
        self.form_combo_area = forest_combo
        forest_combo.currentTextChanged.connect(
            lambda: self.replace_graphic(
                type_changed_parameter=TypeSettings.AREA, new_value_parameter=forest_combo.currentText()
            )
        )
        forest_widget.addWidget(forest_area)
        forest_widget.addWidget(forest_combo)
        main_setting.addLayout(forest_widget, 0, 0)

        # Виджет для основной породы
        breed_widget = QVBoxLayout()
        main_breed = QLabel("Основная порода")
        breed_combo = QComboBox()
        breed_combo.setStyleSheet(SettingsView.background_color)
        self.form_combo_breed = breed_combo
        breed_combo.currentTextChanged.connect(
            lambda: self.replace_graphic(
                type_changed_parameter=TypeSettings.BREED, new_value_parameter=breed_combo.currentText()
            )
        )
        breed_widget.addWidget(main_breed)
        breed_widget.addWidget(breed_combo)
        main_setting.addLayout(breed_widget, 0, 1)

        # Виджет для типа условий
        conditions_widget = QVBoxLayout()
        type_conditions = QLabel("Тип условий")
        conditions_combo = QComboBox()
        conditions_combo.setStyleSheet(SettingsView.background_color)
        self.form_combo_condition = conditions_combo
        conditions_combo.currentTextChanged.connect(
            lambda: self.replace_graphic(
                type_changed_parameter=TypeSettings.CONDITION, new_value_parameter=conditions_combo.currentText()
            )
        )
        conditions_widget.addWidget(type_conditions)
        conditions_widget.addWidget(conditions_combo)
        main_setting.addLayout(conditions_widget, 1, 0)

        # Виджет для защитного леса
        save_widget = QVBoxLayout()
        save_forest = QLabel("Защитный лес")
        save_check_box = QCheckBox()
        save_check_box.setStyleSheet(SettingsView.checkbox_style)
        save_check_box.setChecked(self.flag_save_forest)
        self.save_check_box = save_check_box
        save_check_box.stateChanged.connect(lambda: self.change_save_forest())
        save_widget.addWidget(save_forest)
        save_widget.addWidget(save_check_box)
        main_setting.addLayout(save_widget, 1, 1)

        main_setting_widget.setLayout(main_setting)

        current_settings_widget = QWidget()
        current_settings_widget.setFixedWidth(331)

        current_settings = QGridLayout()
        current_settings.setContentsMargins(5, 0, 5, 0)
        current_settings.setSpacing(5)

        start_parameter_label = QLabel("Начальные параметры")
        start_parameter_label.setStyleSheet(SettingsView.background_color)
        current_settings.addWidget(start_parameter_label, 0, 0)

        start_parameter_widget = QLabel("Возраст")
        start_parameter_widget.setStyleSheet(SettingsView.background_color)
        current_settings.addWidget(start_parameter_widget, 1, 0)

        start_parameter_edit_field = QLineEdit()
        start_parameter_edit_field.setStyleSheet(SettingsView.background_color)
        self.start_point_edit_field = start_parameter_edit_field
        current_settings.addWidget(start_parameter_edit_field, 1, 1)

        area_parameter_widget = QLabel("Площадь")
        area_parameter_widget.setStyleSheet(SettingsView.background_color)
        current_settings.addWidget(area_parameter_widget, 2, 0)

        area_parameter_edit_field = QLineEdit()
        area_parameter_edit_field.setStyleSheet(SettingsView.background_color)
        self.area_point_edit_field = area_parameter_edit_field
        current_settings.addWidget(area_parameter_edit_field, 2, 1)

        auto_mode = QPushButton("Автоматический режим")
        auto_mode.setStyleSheet(SettingsView.background_color_button)
        auto_mode.clicked.connect(lambda: self.replace_predict())
        current_settings.addWidget(auto_mode, 3, 0)

        current_settings_widget.setLayout(current_settings)

        result_info_widget = QWidget()
        result_info_widget.setFixedWidth(331)

        result_info = QGridLayout()
        result_info.setContentsMargins(5, 0, 5, 0)
        result_info.setSpacing(5)

        name_forestry_label = QLabel("Лесничество")
        name_forestry_label.setStyleSheet(SettingsView.background_color)
        result_info.addWidget(name_forestry_label, 0, 0)

        name_forestry_edit_field = QLineEdit()
        name_forestry_edit_field.setStyleSheet(SettingsView.background_color)
        result_info.addWidget(name_forestry_edit_field, 0, 1)

        name_district_forestry_label = QLabel("Участковое лесничество")
        name_district_forestry_label.setStyleSheet(SettingsView.background_color)
        result_info.addWidget(name_district_forestry_label, 1, 0)

        name_district_forestry_edit_field = QLineEdit()
        name_district_forestry_edit_field.setStyleSheet(SettingsView.background_color)
        result_info.addWidget(name_district_forestry_edit_field, 1, 1)

        name_quarter_label = QLabel("Квартал")
        name_quarter_label.setStyleSheet(SettingsView.background_color)
        result_info.addWidget(name_quarter_label, 2, 0)

        name_quarter_edit_field = QLineEdit()
        name_quarter_edit_field.setStyleSheet(SettingsView.background_color)
        result_info.addWidget(name_quarter_edit_field, 2, 1)

        name_selected_label = QLabel("Выдел")
        name_selected_label.setStyleSheet(SettingsView.background_color)
        result_info.addWidget(name_selected_label, 3, 0)

        name_selected_edit_field = QLineEdit()
        name_selected_edit_field.setStyleSheet(SettingsView.background_color)
        result_info.addWidget(name_selected_edit_field, 3, 1)

        result_info_widget.setLayout(result_info)

        # Добавляем макеты в горизонтальный layout
        info_layout.addWidget(main_setting_widget)
        info_layout.addWidget(current_settings_widget)
        info_layout.addWidget(result_info_widget)

        # Устанавливаем горизонтальный layout для info
        info.setLayout(info_layout)

        return info

    def create_main_part(self) -> QWidget:
        """Create the main content area with plot and info blocks.

        Constructs a horizontal layout with a plot widget on the left (for graphics) and
        a scrollable area on the right (form_scroll_area, styled with SettingsView.background_color)
        for information blocks. The scroll area is initially empty.

        Returns:
            QWidget: The main content widget.
        """
        main = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(5, 0, 5, 0)

        self.graphic = QWidget()
        self.graphic.setMinimumWidth(600)
        self.graphic.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.graphic)

        # Создаем контейнер для блоков информации с прокруткой
        blocks_container = QWidget()
        blocks_container.setFixedWidth(350)
        blocks_info_layout = QVBoxLayout(blocks_container)

        # Создаем виджет с прокруткой
        scroll_area = QScrollArea()
        self.form_scroll_area = scroll_area
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(SettingsView.background_color)

        # Создаем контейнер для блоков информации
        blocks_widget = QWidget()
        blocks_layout = QVBoxLayout(blocks_widget)
        blocks_layout.setContentsMargins(5, 5, 5, 5)

        # Устанавливаем виджет с блоками в область прокрутки
        scroll_area.setWidget(blocks_widget)
        blocks_info_layout.addWidget(scroll_area)

        main_layout.addWidget(blocks_container)
        main.setLayout(main_layout)

        return main

    def _create_info_block(
        self,
        index: float,
        info_block: dict[str, float],
    ) -> QWidget:
        """Create an information block for thinning event data.

        Constructs a QWidget styled with SettingsView.item_block, displaying details of a
        thinning event, including felling date, reserve values before and after thinning,
        and fullness values. Includes a cancel button styled with SettingsView.cancel_button
        to delete the thinning event by index. Intensity fields ('Инт.зап', 'Инт.об') are
        displayed but not calculated in the current implementation.

        Args:
            index (float): The index of the thinning event in the list of planned thinnings.
            info_block (dict[str, float]): A dictionary containing thinning event data with
                keys 'x' (felling date), 'reserve_before', 'reserve_after', 'past_value'
                (fullness before), and 'new_value' (fullness after).

        Returns:
            QWidget: The information block widget with labels and a cancel button.
        """
        main_info_block = QWidget()
        main_info_block.setStyleSheet(SettingsView.item_block)
        main_info_block.setContentsMargins(5, 0, 5, 0)
        main_info_block.setFixedWidth(300)
        main_info_block.setFixedHeight(150)

        main_info_block_layout = QGridLayout(main_info_block)
        main_info_block_layout.setContentsMargins(5, 0, 5, 0)
        main_info_block_layout.setSpacing(5)

        date_fell_label = QLabel("Дата рубки")
        date_fell_label.setFixedHeight(20)
        date_fell_label.setFixedWidth(90)
        main_info_block_layout.addWidget(date_fell_label, 0, 0)

        date_fell_value = QLineEdit("Date")
        date_fell_value.setFixedHeight(20)
        date_fell_value.setFixedWidth(45)
        main_info_block_layout.addWidget(date_fell_value, 0, 1)
        date_fell = info_block.get("x")
        if date_fell is not None:
            date_fell_value.setText(f"{date_fell:.0f}")
        date_fell_value.textChanged.connect(
            lambda: self.update_info_block(index=index, info_block=info_block, date_thinning=date_fell_value.text())
        )

        # Запас до рубки (Мд)
        reserve_before_label = QLabel("Мд")
        reserve_before_label.setFixedHeight(20)
        reserve_before_label.setFixedWidth(90)
        main_info_block_layout.addWidget(reserve_before_label, 1, 0)

        reserve_before_value = QLabel("float")
        reserve_before_value.setFixedHeight(20)
        reserve_before_value.setFixedWidth(45)
        main_info_block_layout.addWidget(reserve_before_value, 1, 1)
        reserve_before = info_block.get("reserve_before")
        if reserve_before is not None:
            reserve_before_value.setText(f"{reserve_before:.1f}")

        # Запас после рубки (Мп)
        reserve_after_label = QLabel("Мп")
        reserve_after_label.setFixedHeight(20)
        reserve_after_label.setFixedWidth(90)
        main_info_block_layout.addWidget(reserve_after_label, 1, 2)

        reserve_after_value = QLabel("float")
        reserve_after_value.setFixedHeight(20)
        reserve_after_value.setFixedWidth(45)
        main_info_block_layout.addWidget(reserve_after_value, 1, 3)
        reserve_after = info_block.get("reserve_after")
        if reserve_after is not None:
            reserve_after_value.setText(f"{reserve_after:.1f}")

        # Абсолютная полнота до рубки (Gад)
        value_before_label = QLabel("Gад")
        value_before_label.setFixedHeight(20)
        value_before_label.setFixedWidth(90)
        main_info_block_layout.addWidget(value_before_label, 2, 0)

        value_before_value = QLabel("float")
        value_before_value.setFixedHeight(20)
        value_before_value.setFixedWidth(45)
        main_info_block_layout.addWidget(value_before_value, 2, 1)
        fullness_before = info_block.get("past_value")
        if fullness_before is not None:
            value_before_value.setText(f"{fullness_before:.1f}")

        # Абсолютная полнота после рубки (Gап)
        value_after_label = QLabel("Gап")
        value_after_label.setFixedHeight(20)
        value_after_label.setFixedWidth(90)
        main_info_block_layout.addWidget(value_after_label, 2, 2)

        value_after_value = QLabel("float")
        value_after_value.setFixedHeight(20)
        value_after_value.setFixedWidth(45)
        main_info_block_layout.addWidget(value_after_value, 2, 3)
        fullness_after = info_block.get("new_value")
        if fullness_after is not None:
            value_after_value.setText(f"{fullness_after:.0f}")

        # Интенсивность по запасу, %
        intensity_by_reserve_label = QLabel("Инт.зап, %")
        intensity_by_reserve_label.setFixedHeight(20)
        intensity_by_reserve_label.setFixedWidth(90)
        main_info_block_layout.addWidget(intensity_by_reserve_label, 3, 0)

        intensity_by_reserve_value = QLabel("float")
        intensity_by_reserve_value.setFixedHeight(20)
        intensity_by_reserve_value.setFixedWidth(45)
        main_info_block_layout.addWidget(intensity_by_reserve_value, 3, 1)
        # if reserve_before and reserve_after:
        #     intensity_by_reserve_value.setText(f"{((reserve_before - reserve_after) / reserve_before * 100):.0f}")

        # Интенсивность по полноте, %
        intensity_by_volume_label = QLabel("Инт. об, %")
        intensity_by_volume_label.setFixedHeight(20)
        intensity_by_volume_label.setFixedWidth(90)
        main_info_block_layout.addWidget(intensity_by_volume_label, 3, 2)

        intensity_by_volume_value = QLabel("float")
        intensity_by_volume_value.setFixedHeight(20)
        intensity_by_volume_value.setFixedWidth(45)
        main_info_block_layout.addWidget(intensity_by_volume_value, 3, 3)
        # if reserve_before and reserve_after:
        #     intensity_by_volume_value.setText(f"{((reserve_before - reserve_after) / reserve_before * 100):.0f}")

        # Кнопки управления
        btn_cancel = QPushButton()
        btn_cancel.setStyleSheet(SettingsView.cancel_button)
        btn_cancel.setFixedWidth(25)
        btn_cancel.clicked.connect(lambda: self.delete_thinning(index=index))
        main_info_block_layout.addWidget(btn_cancel, 0, 4)

        main_info_block.setLayout(main_info_block_layout)

        return main_info_block

    def update_info_block(
        self,
        index: int,
        info_block: dict[str, float],
        date_thinning: str = None,
        height: str = None,
    ):
        """Update a thinning event information block and refresh the plot.

        Updates the thinning event data in info_block with a new date_thinning if provided
        and valid (positive integer within the allowed range between adjacent events).
        Calls PredictModelService to rewrite the thinning event, refreshes thinning data,
        and updates the plot via _update_graphic. Ignores the height parameter.

        Args:
            index (int): The index of the thinning event in the list of planned thinnings.
            info_block (dict[str, float]): The dictionary containing thinning event data with
                keys 'x', 'past_value', 'new_value', and optionally 'reserve_before', 'reserve_after'.
            date_thinning (str, optional): The new felling date as a string (converted to int).
                Defaults to None.
            height (str, optional): Ignored in the current implementation. Defaults to None.

        Returns:
            None
        """
        if date_thinning == "":
            return
        if date_thinning is not None and date_thinning.isdigit():
            date_thinning = int(date_thinning)
            if date_thinning == 0:
                return
            if index == 0:
                left_date = 0
            else:
                left_date = self.list_record_planned_thinning[index - 1].get("x")
            if index == len(self.list_record_planned_thinning) - 1:
                right_date = self.age_thinning
            else:
                right_date = self.list_record_planned_thinning[index + 1].get("x")
            if date_thinning > left_date and date_thinning < right_date:
                info_block["x"] = date_thinning
            else:
                return
        if height is not None:
            pass
        self.predict_model.rewrite_item_record_planed_thinning(index=index, item=info_block)
        self.list_record_planned_thinning = self.predict_model.get_list_record_planned_thinning()
        self.list_value_track_thinning = self.predict_model.get_list_value_track_thinning()
        self._update_graphic()

    def _update_graphic(self) -> None:
        """Update the plot widget with prediction data and handle double-click events.

        Creates or updates a pyqtgraph PlotWidget styled with SettingsView, displaying
        minimum logging, maximum logging, economic minimum, and bearing lines, with a
        filled area between economic minimum and maximum logging lines. Adds a vertical
        thinning age line based on flag_save_forest. Handles double-click events on the
        predict line using Settings.DETENTION_BUFFER. Clears the old plot before adding
        the new one and updates UI blocks via create_blocks_with_thinning_data.

        Returns:
            None
        """
        if not hasattr(self, "graphic_layout"):
            self.graphic_layout = QVBoxLayout(self.graphic)

        # Создаем PlotWidget
        plot_widget = pg.PlotWidget()
        plot_widget.setBackground(SettingsView.main_background_filling_color)

        # Обработчик двойного клика
        # Получаем данные линии
        if self.list_value_track_thinning:
            line_x = np.array(self.list_value_track_thinning.get("x"))
            line_y = np.array(self.list_value_track_thinning.get("y"))

            # Переопределяем метод mouseDoubleClickEvent для plot_widget
            plot_widget.mouseDoubleClickEvent = lambda event: self.mouseDoubleClickEvent(
                plot_widget=plot_widget, line_x=line_x, line_y=line_y, event=event
            )

        # Обработчик ПКМ
        plot_widget.mousePressEvent = lambda event: self._handle_right_click(plot_widget=plot_widget, event=event)

        # Устанавливаем фиксированные пределы осей
        increase_x = (self.x_max - self.x_min) * Settings.INCREASE_GRAPHIC
        increase_y = (self.y_max - self.y_min) * Settings.INCREASE_GRAPHIC

        plot_widget.setXRange(self.x_min - increase_x, self.x_max + increase_x, padding=0)
        plot_widget.setYRange(self.y_min - increase_y, self.y_max + increase_y, padding=0)

        # Отключаем автоматическое масштабирование
        plot_widget.setAutoVisible(y=False)
        plot_widget.enableAutoRange(enable=False)

        # Ограничиваем возможность прокрутки
        plot_widget.setLimits(
            xMin=self.x_min - increase_y,
            xMax=self.x_max + increase_x,
            yMin=self.y_min - increase_y,
            yMax=self.y_max + increase_y,
        )

        # Линии графика
        plot_widget.plot(
            self.list_value_x,
            self.list_value_y_min_logging,
            pen=pg.mkPen(color=SettingsView.main_line_color, width=2),
            name=f"Line {TypeLine.MIN_LEVEL_LOGGING.value}",
        )

        plot_widget.plot(
            self.list_value_x,
            self.list_value_y_max_logging,
            pen=pg.mkPen(color=SettingsView.main_line_color, width=2),
            name=f"Line {TypeLine.ECONOMIC_MAX_LINE.value}",
        )

        plot_widget.plot(
            self.list_value_x,
            self.list_value_y_min_economic,
            pen=pg.mkPen(color=SettingsView.main_line_color, width=2),
            name=f"Line {TypeLine.ECONOMIC_MIN_LINE.value}",
        )
        # scatter_before = pg.ScatterPlotItem(
        #     pos=list(zip(self.list_value_x, self.list_value_y_min_economic)),
        #     size=10,
        #     pen=pg.mkPen(None),
        #     brush=pg.mkBrush(0, 255, 0),  # Зеленый цвет
        #     symbol="o",
        # )
        # plot_widget.addItem(scatter_before)

        # Заливка между линиями
        polygon = pg.FillBetweenItem(
            curve1=pg.PlotDataItem(self.list_value_x, self.list_value_y_min_economic),
            curve2=pg.PlotDataItem(self.list_value_x, self.list_value_y_max_logging),
            brush=pg.mkBrush(color=SettingsView.fill_color_graph),
        )
        plot_widget.addItem(polygon)

        # Линия возраста рубки
        if self.flag_save_forest:
            target_value = self.age_thinning_save
        else:
            target_value = self.age_thinning
        plot_widget.plot(
            [target_value, target_value],
            [self.y_min, self.y_max],
            pen=pg.mkPen(SettingsView.line_age_thinning, width=2),
            name="Line thinning forest",
        )

        if self.start_point:
            scatter = pg.ScatterPlotItem(
                pos=[(self.start_point[0], self.start_point[1])],
                size=10,
                pen=pg.mkPen(None),
                brush=pg.mkBrush(color=SettingsView.line_bearing_color),
                symbol="o",
            )
            plot_widget.addItem(scatter)

        # Линия несущей способности
        if self.list_value_y_bearing_line:
            plot_widget.plot(
                self.list_value_x,
                self.list_value_y_bearing_line,
                pen=pg.mkPen(color=SettingsView.line_bearing_color, width=2),
                name="Bearing line",
            )
            # scatter_before = pg.ScatterPlotItem(
            #     pos=list(zip(self.list_value_x, self.list_value_y_bearing_line)),
            #     size=10,
            #     pen=pg.mkPen(None),
            #     brush=pg.mkBrush(0, 255, 0),  # Зеленый цвет
            #     symbol="o",
            # )
            # plot_widget.addItem(scatter_before)

        # Линия прогнозируемой рубки (сохраняем объект)
        if self.list_value_track_thinning:
            self.predict_line_item = plot_widget.plot(
                self.list_value_track_thinning.get("x"),
                self.list_value_track_thinning.get("y"),
                pen=pg.mkPen("r", width=2),
                name="Predict line thinning",
            )
            # scatter_before = pg.ScatterPlotItem(
            #     pos=list(zip(self.list_value_track_thinning.get("x"), self.list_value_track_thinning.get("y"))),
            #     size=10,
            #     pen=pg.mkPen(None),
            #     brush=pg.mkBrush(0, 255, 0),  # Зеленый цвет
            #     symbol="o",
            # )
            # plot_widget.addItem(scatter_before)

        # Легенда и подписи осей
        plot_widget.addLegend()
        plot_widget.setLabel("left", "Полнота")
        plot_widget.setLabel("bottom", "Возраст, лет")

        # Заменяем старый график новым
        if self.graphic_layout.count() > 0:
            self.graphic_layout.itemAt(0).widget().setParent(None)

        self.graphic_layout.addWidget(plot_widget)

        self.create_blocks_with_thinning_data()

    def _handle_right_click(self, plot_widget: pg.PlotWidget, event: QtGui.QMouseEvent) -> None:
        """Handle right-click events on the plot to add a bearing point.

        Processes right-click events to add a bearing point at the clicked position after
        user confirmation via QMessageBox. Uses cast_coordinates_point to round coordinates
        and checks y-value against PredictModelService's min/max logging lines. Updates the
        bearing line and refreshes the plot via _update_graphic.

        Args:
            plot_widget (pg.PlotWidget): The plot widget where the event occurred.
            event (QtGui.QMouseEvent): The mouse event object.

        Returns:
            None
        """
        if event.button() == Qt.RightButton:
            pos = event.pos()
            scene_pos = plot_widget.plotItem.vb.mapSceneToView(pos)
            x, y = scene_pos.x(), scene_pos.y()

            # Округляем x до ближайшего кратного STEP_PLOTTING_GRAPH
            x, y = cast_coordinates_point(x=x, y=y)

            min_y = self.predict_model.get_predict_value(type_line=TypeLine.MIN_LEVEL_LOGGING, x=x)
            max_y = self.predict_model.get_predict_value(type_line=TypeLine.MAX_LEVEL_LOGGING, x=x)
            if y < min_y and y > max_y:
                return

            reply = QMessageBox.question(
                self,
                "Подтверждение действия",
                f"Добавить опорную точку?\nВозраст={x:.0f}, Полнота={y:.1f}",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                self.predict_model.set_bearing_parameter(bearing_point=(x, y))
                self.predict_model.initialize_bearing_line()
                self.list_value_y_bearing_line = self.predict_model.get_bearing_line()
            self.start_point = (x, y)
            self.start_point_edit_field.setText(str(x))
            self.area_point_edit_field.setText(str(y))

            self._update_graphic()
            event.accept()
        else:
            super(plot_widget.__class__, plot_widget).mousePressEvent(event)

    def mouseDoubleClickEvent(
        self, plot_widget: pg.PlotWidget, line_x: np.array, line_y: np.array, event: QtGui.QMouseEvent
    ) -> None:
        """Handle double-click events on the predict line to add or correct thinning events.

        Processes double-click events within Settings.DETENTION_BUFFER of the thinning
        prediction line to add a new thinning event or correct an existing one. Uses
        cast_coordinates_point to round coordinates, updates thinning data via
        PredictModelService, and refreshes the plot via _update_graphic.

        Args:
            plot_widget (pg.PlotWidget): The plot widget where the event occurred.
            line_x (np.array): The x-coordinates of the thinning prediction line.
            line_y (np.array): The y-coordinates of the thinning prediction line.
            event (QtGui.QMouseEvent): The mouse event object.

        Returns:
            None
        """
        if event.button() == Qt.LeftButton:  # Проверяем левую кнопку мыши
            pos = event.pos()  # Позиция клика в пикселях
            scene_pos = plot_widget.plotItem.vb.mapSceneToView(pos)  # Преобразование в координаты графика
            click_x, click_y = scene_pos.x(), scene_pos.y()

            # Проверяем, попадает ли клик в буферную зону линии
            if self.predict_line_item:
                # Находим ближайшую точку на линии
                distances = np.sqrt((line_x - click_x) ** 2 + (line_y - click_y) ** 2)
                min_distance = np.min(distances)

                # Проверяем, находится ли клик в пределах буфера
                if min_distance <= Settings.DETENTION_BUFFER:
                    x, y = cast_coordinates_point(x=click_x, y=click_y)
                    list_date_thinning = []
                    for item in self.list_record_planned_thinning:
                        list_date_thinning.append(item.get("x"))
                    if x in list_date_thinning:
                        print(str("Двойной клик корректировки рубки:" + f"Возраст={x:.0f}, Полнота={y:.1f}"))
                        self.predict_model.correct_thinning(date_thinning=x, value_thinning=y)
                        self.list_record_planned_thinning = self.predict_model.get_list_record_planned_thinning()
                        self.list_value_track_thinning = self.predict_model.get_list_value_track_thinning()
                    else:
                        print(str("Двойной клик рубки:" + f"Возраст={x:.0f}, Полнота={y:.1f}"))
                        self.predict_model.add_thinning(date_thinning=x, value_thinning=y)
                        self.list_record_planned_thinning = self.predict_model.get_list_record_planned_thinning()
                        self.list_value_track_thinning = self.predict_model.get_list_value_track_thinning()
                    self._update_graphic()
                    event.accept()  # Подтверждаем обработку события
                else:
                    event.ignore()  # Игнорируем, если клик вне буфера
            else:
                event.ignore()  # Игнорируем, если линия не существует
        else:
            super(plot_widget.__class__, plot_widget).mouseDoubleClickEvent(event)

    def delete_thinning(self, index: int) -> None:
        """Delete a thinning event by index and update the plot.

        Removes the thinning event at the specified index from the prediction model,
        refreshes the list of planned thinnings and the thinning track, and updates the plot.

        Args:
            index (int): The index of the thinning event to delete.

        Returns:
            None
        """
        self.predict_model.delete_thinning(index=index)
        self.list_record_planned_thinning = self.predict_model.get_list_record_planned_thinning()
        self.list_value_track_thinning = self.predict_model.get_list_value_track_thinning()
        self._update_graphic()

    def change_save_forest(self):
        """Update the protective forest mode and refresh the plot.

        Sets the protective forest flag based on the save_check_box state, updates
        PredictModelService, checks the graph for protective forest constraints, refreshes
        thinning data, and updates the plot via _update_graphic.

        Returns:
            None
        """
        flag_save_forest = self.save_check_box.isChecked()
        self.flag_save_forest = flag_save_forest
        self.predict_model.set_flag_save_forest(flag_save_forest=flag_save_forest)
        self.predict_model.check_graph_save_forest()
        self.list_record_planned_thinning = self.predict_model.get_list_record_planned_thinning()
        self.list_value_track_thinning = self.predict_model.get_list_value_track_thinning()
        self._update_graphic()

    def replace_graphic(self, type_changed_parameter: TypeSettings = None, new_value_parameter: str = None) -> None:
        """Replace the current graphic with updated area, breed, or condition.

        Updates combo box selections via changed_combo_boxes, resets graphic attributes
        (e.g., x_min, predict_line_item), reinitializes PredictModelService with the
        current area, breed, condition, and forest mode, loads plotting data styled with
        SettingsView, and updates the plot via _update_graphic.

        Args:
            type_changed_parameter (TypeSettings, optional): The type of parameter changed (AREA, BREED, CONDITION).
                Defaults to None.
            new_value_parameter (str, optional): The new value for the changed parameter. Defaults to None.

        Returns:
            None

        Raises:
            ValueError: If only one of type_changed_parameter or new_value_parameter is provided.
        """
        if (type_changed_parameter is not None and new_value_parameter is None) or (
            type_changed_parameter is None and new_value_parameter is not None
        ):
            raise ValueError("Both parameters must be provided or both must be None.")

        self.changed_combo_boxes(type_changed_parameter=type_changed_parameter, new_value_parameter=new_value_parameter)

        self.flag_save_forest: bool = False
        self.save_check_box.setChecked(self.flag_save_forest)
        self.x_min: float = None
        self.x_max: float = None
        self.y_min: float = None
        self.y_max: float = None
        self.start_point: tuple[float, float] = None
        self.list_value_x: list[float] = None
        self.list_value_y_min_logging: list[float] = None
        self.list_value_y_max_logging: list[float] = None
        self.list_value_y_min_economic: list[float] = None
        self.list_value_y_bearing_line: list[float] = None
        self.list_value_track_thinning: list[float] = None
        self.list_record_planned_thinning: list[dict[str, float]] = None
        self.predict_line_item = None

        if self.name_area is None:
            return

        self.age_thinning = self.manager_breeds.get_age_thinning_breed(name=self.name_breed)
        self.age_thinning_save = self.manager_breeds.get_age_thinning_save_breed(name=self.name_breed)

        self.predict_model.initialize_predict_model(
            area=self.name_area,
            breed=self.name_breed,
            condition=self.name_condition,
            flag_save_forest=self.flag_save_forest,
        )
        self.predict_model.load_model()
        self.x_min, self.x_max, self.y_min, self.y_max = self.predict_model.get_min_max_value()
        self.predict_model.initialize_base_line_graph(x_start=self.x_min, x_end=self.x_max)

        base_lines = self.predict_model.get_base_lines_graph()
        self.list_value_x = base_lines.get("list_value_x")
        self.list_value_y_min_logging = base_lines.get("list_value_y_min_logging")
        self.list_value_y_max_logging = base_lines.get("list_value_y_max_logging")
        self.list_value_y_min_economic = base_lines.get("list_value_y_min_economic")

        self._update_graphic()

    def changed_combo_boxes(self, type_changed_parameter: TypeSettings = None, new_value_parameter: str = None) -> None:
        """Update combo box selections based on a changed parameter.

        Updates area, breed, and condition selections in form_combo_area, form_combo_breed,
        and form_combo_condition using services to filter allowed values. Blocks signals
        to prevent recursive updates and sets current selections to valid values.

        Args:
            type_changed_parameter (TypeSettings, optional): The type of parameter changed (AREA, BREED, CONDITION).
                Defaults to None (uses AREA).
            new_value_parameter (str, optional): The new value for the changed parameter. Defaults to None.

        Returns:
            None
        """
        if type_changed_parameter is None:
            type_changed_parameter = TypeSettings.AREA

        if type_changed_parameter == TypeSettings.AREA:
            self.list_areas = self.manager_areas.get_list_allowed_areas()
            if new_value_parameter is not None:
                self.name_area = new_value_parameter
            else:
                if len(self.list_areas) == 0:
                    return
                self.name_area = self.list_areas[0]

            self.list_breeds = self.manager_breeds.get_list_allowed_breeds(area=self.name_area)
            self.name_breed = self.list_breeds[0]

            self.list_conditions = self.manager_conditions.get_list_allowed_condition(
                area=self.name_area, breed=self.name_breed
            )
            self.name_condition = self.list_conditions[0]
        elif type_changed_parameter == TypeSettings.BREED:
            self.name_breed = new_value_parameter
            self.list_breeds = self.manager_breeds.get_list_allowed_breeds()

            self.list_areas = self.manager_areas.get_list_allowed_areas(breed=self.name_breed)
            self.name_area = self.list_areas[0]

            self.list_conditions = self.manager_conditions.get_list_allowed_condition(
                area=self.name_area, breed=self.name_breed
            )
            self.name_condition = self.list_conditions[0]
        elif type_changed_parameter == TypeSettings.CONDITION:
            self.name_condition = new_value_parameter
            self.list_conditions = self.manager_conditions.get_list_allowed_condition()

            self.list_areas = self.manager_areas.get_list_allowed_areas(condition=self.name_condition)
            self.name_area = self.list_areas[0]

            self.list_breeds = self.manager_breeds.get_list_allowed_breeds(
                area=self.name_area, condition=self.name_condition
            )
            self.name_breed = self.list_breeds[0]

        self.form_combo_area.blockSignals(True)
        self.form_combo_breed.blockSignals(True)
        self.form_combo_condition.blockSignals(True)

        self.form_combo_area.clear()
        self.form_combo_area.addItems(self.list_areas)
        self.form_combo_area.setCurrentText(self.name_area)
        self.form_combo_breed.clear()
        self.form_combo_breed.addItems(self.list_breeds)
        self.form_combo_breed.setCurrentText(self.name_breed)
        self.form_combo_condition.clear()
        self.form_combo_condition.addItems(self.list_conditions)
        self.form_combo_condition.setCurrentText(self.name_condition)

        self.form_combo_area.blockSignals(False)
        self.form_combo_breed.blockSignals(False)
        self.form_combo_condition.blockSignals(False)

    def replace_predict(self, start_parameter: str = None, flag_save_forest: bool = None) -> None:
        """Update prediction data and refresh the plot.

        Runs a thinning simulation and initializes the thinning track if a bearing line
        exists, then updates thinning data and plot via _update_graphic. Calls
        create_blocks_with_thinning_data to refresh UI blocks. Ignores start_parameter
        and flag_save_forest parameters in the current implementation.

        Args:
            start_parameter (str, optional): Ignored in the current implementation. Defaults to None.
            flag_save_forest (bool, optional): Ignored in the current implementation. Defaults to None.

        Returns:
            None
        """
        if self.list_value_y_bearing_line:
            self.predict_model.simulation_thinning()
            self.predict_model.initialize_track_thinning()
            self.list_value_track_thinning = self.predict_model.get_list_value_track_thinning()
            self.list_record_planned_thinning = self.predict_model.get_list_record_planned_thinning()
        self._update_graphic()

        self.create_blocks_with_thinning_data()

    def create_blocks_with_thinning_data(self) -> None:
        """Create UI information blocks for thinning simulation data.

        Clears existing blocks in form_scroll_area and generates new information blocks
        styled with SettingsView.info_block for each thinning event in
        list_record_planned_thinning using _create_info_block, displaying felling dates
        and reserve values.

        Returns:
            None
        """
        scroll_area = self.form_scroll_area
        blocks_widget = scroll_area.widget()
        blocks_layout = blocks_widget.layout()

        # Очищаем существующие блоки
        while blocks_layout.count():
            item = blocks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Создаем новые блоки с данными
        if self.list_record_planned_thinning:
            for index, record in enumerate(self.list_record_planned_thinning):
                info_block = self._create_info_block(index=index, info_block=record)
                info_block.setObjectName("info_block")
                info_block.setStyleSheet(SettingsView.info_block)
                blocks_layout.addWidget(info_block)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
