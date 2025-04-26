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


class MainWindow(QWidget):
    """The main application window for managing and visualizing graphics data.

    Provides a PySide6-based GUI with a header for actions (e.g., open, save, settings),
    an info panel for selecting area, breed, and condition, and a main area with a plot
    widget for graphics and scrollable information blocks. Interacts with services to
    manage data and predictions.

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
        graphic (QWidget): Widget containing the plot.
        graphic_layout (QVBoxLayout): Layout for the plot widget.
    """

    def __init__(self):
        """Initialize the MainWindow.

        Sets up the window title, geometry, background, and UI components (header, info
        panel, main content). Initializes services and loads initial parameters.

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
        palette.setColor(QPalette.Window, QColor("white"))
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

        Constructs a header with buttons for opening, saving, and accessing graphics lists
        and settings, styled with a yellow background.

        Returns:
            QWidget: The header widget containing buttons.
        """
        header = QWidget()
        header.setFixedHeight(30)
        header.setStyleSheet("background-color: #FFF2CC;")

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(5, 0, 5, 0)

        # Добавляем кнопки слева
        btn_open = QPushButton("Открыть")
        btn_open.setFixedWidth(150)
        btn_open.setStyleSheet("background-color: #D5E8D4;")
        btn_save = QPushButton("Сохранить")
        btn_save.setFixedWidth(150)
        btn_save.setStyleSheet("background-color: #D5E8D4;")
        btn_save_as = QPushButton("Сохранить как")
        btn_save_as.setFixedWidth(150)
        btn_save_as.setStyleSheet("background-color: #D5E8D4;")

        header_layout.addWidget(btn_open)
        header_layout.addWidget(btn_save)
        header_layout.addWidget(btn_save_as)

        # Добавляем растягивающийся элемент
        header_layout.addStretch()

        # Добавляем кнопки справа
        btn_list_graphics = QPushButton("Список графиков")
        btn_list_graphics.setFixedWidth(150)
        btn_list_graphics.setStyleSheet("background-color: #D5E8D4;")
        btn_list_graphics.clicked.connect(self.open_list_graphics)

        btn_settings = QPushButton("Настройки")
        btn_settings.setFixedWidth(150)
        btn_settings.setStyleSheet("background-color: #D5E8D4;")
        header_layout.addWidget(btn_list_graphics)
        header_layout.addWidget(btn_settings)

        return header

    def open_list_graphics(self) -> None:
        """Open the list graphics window.

        Creates and displays a ListGraphicsWindow for viewing available graphics.

        Returns:
            None
        """
        self.list_graphics_window = ListGraphicsWindow()
        self.list_graphics_window.form_closed.connect(lambda: self.replace_graphic())
        self.list_graphics_window.show()

    def create_info(self) -> QWidget:
        """Create the info panel with parameter selection.

        Constructs a panel with combo boxes for selecting area, breed, condition, and
        protective forest status, plus placeholders for current settings and results,
        styled with a blue background.

        Returns:
            QWidget: The info panel widget containing parameter controls.
        """
        info = QWidget()
        info.setFixedHeight(110)
        info.setStyleSheet("background-color: #DAE8FC; text-align: center;")

        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(5, 0, 5, 0)

        main_setting_widget = QWidget()
        main_setting_widget.setFixedWidth(331)

        main_setting = QGridLayout()
        main_setting.setContentsMargins(5, 0, 5, 0)
        main_setting.setSpacing(5)

        # Виджет для лесного района
        forest_widget = QVBoxLayout()
        forest_area = QLabel("Лесной район")
        forest_combo = QComboBox()
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
        save_check_box.setChecked(self.flag_save_forest)
        self.save_check_box = save_check_box
        save_check_box.stateChanged.connect(lambda: self.replace_predict(flag_safe_forest=save_check_box.isChecked()))
        save_widget.addWidget(save_forest)
        save_widget.addWidget(save_check_box)
        main_setting.addLayout(save_widget, 1, 1)

        main_setting_widget.setLayout(main_setting)

        current_settings_widget = QWidget()
        current_settings_widget.setFixedWidth(331)

        current_settings = QGridLayout()
        current_settings.setContentsMargins(5, 0, 5, 0)
        current_settings.setSpacing(5)

        start_parameter_layout_widget = QWidget()
        start_parameter_layout = QVBoxLayout(start_parameter_layout_widget)
        start_parameter_widget = QLabel("Возраст")
        start_parameter_edit_field = QLineEdit()
        self.start_point_edit_field = start_parameter_edit_field
        start_parameter_layout.addWidget(start_parameter_widget)
        start_parameter_layout.addWidget(start_parameter_edit_field)
        current_settings.addWidget(start_parameter_layout_widget, 0, 0)

        auto_mode = QPushButton("Автоматический режим")
        auto_mode.clicked.connect(lambda: self.replace_predict())
        current_settings.addWidget(auto_mode, 0, 1)
        start_value = QLabel("Начальная полнота")
        current_settings.addWidget(start_value, 1, 0)

        current_settings_widget.setLayout(current_settings)

        result_info_widget = QWidget()
        result_info_widget.setFixedWidth(331)

        result_info = QGridLayout()
        result_info.setContentsMargins(5, 0, 5, 0)
        result_info.setSpacing(5)

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
        a scrollable area on the right containing information blocks, plus a button to add
        new blocks.

        Returns:
            QWidget: The main content widget.
        """
        main = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(5, 0, 5, 0)

        self.graphic = QWidget()
        self.graphic.setStyleSheet("background-color: #DAE8FC; text-align: center;")
        self.graphic.setMinimumWidth(600)
        self.graphic.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self.graphic)

        # Создаем контейнер для блоков информации с прокруткой
        blocks_container = QWidget()
        blocks_container.setFixedWidth(350)
        blocks_info_layout = QVBoxLayout(blocks_container)
        blocks_info_layout.setContentsMargins(5, 0, 5, 0)

        # Создаем виджет с прокруткой
        scroll_area = QScrollArea()
        self.form_scroll_area = scroll_area
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: #ffffff;")

        # Создаем контейнер для блоков информации
        blocks_widget = QWidget()
        blocks_layout = QVBoxLayout(blocks_widget)
        blocks_layout.setContentsMargins(5, 5, 5, 5)
        blocks_layout.setSpacing(5)

        # Устанавливаем виджет с блоками в область прокрутки
        scroll_area.setWidget(blocks_widget)
        blocks_info_layout.addWidget(scroll_area)

        btn_block_info = QPushButton("Добавить блок")
        btn_block_info.setFixedHeight(50)
        btn_block_info.setStyleSheet("background-color: #D5E8D4; text-align: center;")
        blocks_info_layout.addWidget(btn_block_info)

        main_layout.addWidget(blocks_container)
        main.setLayout(main_layout)

        return main

    def _create_info_block(
        self,
        date_growth: float = None,
        date_fell: float = None,
        reserve_before: float = None,
        reserve_after: float = None,
    ) -> QWidget:
        """Create an information block for thinning data.

        Constructs a QWidget displaying thinning event details, including growth and felling
        dates, reserve values before and after thinning, and intensity metrics. Includes a
        cancel button to delete the thinning event.

        Args:
            date_growth (float, optional): The growth date (x-value). Defaults to None.
            date_fell (float, optional): The felling date (x-value). Defaults to None.
            reserve_before (float, optional): The reserve value before thinning. Defaults to None.
            reserve_after (float, optional): The reserve value after thinning. Defaults to None.

        Returns:
            QWidget: The information block widget with labels and a cancel button.
        """
        main_info_block = QWidget()
        main_info_block.setStyleSheet("background-color: #DAE8FC;")
        main_info_block.setContentsMargins(5, 0, 5, 0)
        main_info_block.setFixedWidth(300)

        main_info_block_layout = QGridLayout(main_info_block)
        main_info_block_layout.setContentsMargins(5, 0, 5, 0)
        main_info_block_layout.setSpacing(5)

        date_growth_label = QLabel("Дата роста")
        date_growth_label.setFixedHeight(20)
        date_growth_label.setFixedWidth(90)
        main_info_block_layout.addWidget(date_growth_label, 0, 0)

        date_growth_value = QLabel("Date")
        date_growth_value.setFixedHeight(20)
        date_growth_value.setFixedWidth(45)
        main_info_block_layout.addWidget(date_growth_value, 0, 1)
        if date_growth is not None:
            date_growth_value.setText(f"{date_growth:.2f}")

        date_fell_label = QLabel("Дата рубки")
        date_fell_label.setFixedHeight(20)
        date_fell_label.setFixedWidth(90)
        main_info_block_layout.addWidget(date_fell_label, 0, 2)

        date_fell_value = QLabel("Date")
        date_fell_value.setFixedHeight(20)
        date_fell_value.setFixedWidth(45)
        main_info_block_layout.addWidget(date_fell_value, 0, 3)
        if date_fell is not None:
            date_fell_value.setText(f"{date_fell:.2f}")

        # Запас до рубки (Мд)
        reserve_before_label = QLabel("Мд")
        reserve_before_label.setFixedHeight(20)
        reserve_before_label.setFixedWidth(90)
        main_info_block_layout.addWidget(reserve_before_label, 1, 0)

        reserve_before_value = QLabel("float")
        reserve_before_value.setFixedHeight(20)
        reserve_before_value.setFixedWidth(45)
        main_info_block_layout.addWidget(reserve_before_value, 1, 1)
        if reserve_before is not None:
            reserve_before_value.setText(f"{reserve_before:.2f}")

        # Запас после рубки (Мп)
        reserve_after_label = QLabel("Мп")
        reserve_after_label.setFixedHeight(20)
        reserve_after_label.setFixedWidth(90)
        main_info_block_layout.addWidget(reserve_after_label, 1, 2)

        reserve_after_value = QLabel("float")
        reserve_after_value.setFixedHeight(20)
        reserve_after_value.setFixedWidth(45)
        main_info_block_layout.addWidget(reserve_after_value, 1, 3)
        if reserve_after is not None:
            reserve_after_value.setText(f"{reserve_after:.2f}")

        # Абсолютная полнота до рубки (Gад)
        value_before_label = QLabel("Gад")
        value_before_label.setFixedHeight(20)
        value_before_label.setFixedWidth(90)
        main_info_block_layout.addWidget(value_before_label, 2, 0)

        value_before_value = QLabel("float")
        value_before_value.setFixedHeight(20)
        value_before_value.setFixedWidth(45)
        main_info_block_layout.addWidget(value_before_value, 2, 1)
        if reserve_before is not None:
            value_before_value.setText(f"{reserve_before:.2f}")

        # Абсолютная полнота после рубки (Gап)
        value_after_label = QLabel("Gап")
        value_after_label.setFixedHeight(20)
        value_after_label.setFixedWidth(90)
        main_info_block_layout.addWidget(value_after_label, 2, 2)

        value_after_value = QLabel("float")
        value_after_value.setFixedHeight(20)
        value_after_value.setFixedWidth(45)
        main_info_block_layout.addWidget(value_after_value, 2, 3)
        if reserve_after is not None:
            value_after_value.setText(f"{reserve_after:.2f}")

        # Интенсивность по запасу, %
        intensity_by_reserve_label = QLabel("Инт.зап, %")
        intensity_by_reserve_label.setFixedHeight(20)
        intensity_by_reserve_label.setFixedWidth(90)
        main_info_block_layout.addWidget(intensity_by_reserve_label, 3, 0)

        intensity_by_reserve_value = QLabel("float")
        intensity_by_reserve_value.setFixedHeight(20)
        intensity_by_reserve_value.setFixedWidth(45)
        main_info_block_layout.addWidget(intensity_by_reserve_value, 3, 1)
        if reserve_before and reserve_after:
            intensity_by_reserve_value.setText(f"{((reserve_before - reserve_after) / reserve_before * 100):.0f}")

        # Интенсивность по полноте, %
        intensity_by_volume_label = QLabel("Инт. об, %")
        intensity_by_volume_label.setFixedHeight(20)
        intensity_by_volume_label.setFixedWidth(90)
        main_info_block_layout.addWidget(intensity_by_volume_label, 3, 2)

        intensity_by_volume_value = QLabel("float")
        intensity_by_volume_value.setFixedHeight(20)
        intensity_by_volume_value.setFixedWidth(45)
        main_info_block_layout.addWidget(intensity_by_volume_value, 3, 3)
        if reserve_before and reserve_after:
            intensity_by_volume_value.setText(f"{((reserve_before - reserve_after) / reserve_before * 100):.0f}")

        # Кнопки управления
        btn_cancel = QPushButton()
        btn_cancel.setStyleSheet("background-color: #F8CECC; text-align: center;")
        btn_cancel.setFixedWidth(25)
        btn_cancel.clicked.connect(lambda: self.predict_model.delete_thinning(date_thinning=date_fell))
        main_info_block_layout.addWidget(btn_cancel, 0, 4)

        main_info_block.setLayout(main_info_block_layout)

        return main_info_block

    def _update_graphic(self) -> None:
        """Update the plot widget with prediction data and handle double-click events on the predict line.

        Creates or updates a pyqtgraph PlotWidget to display minimum logging, maximum
        logging, and economic minimum lines, with a filled area between economic minimum
        and maximum logging lines. Sets axis labels and limits based on model data.
        Adds double-click event handling for the predict line thinning with an increased
        detection area using a buffer zone. Updates UI blocks with thinning data.

        Returns:
            None
        """
        if not hasattr(self, "graphic_layout"):
            self.graphic_layout = QVBoxLayout(self.graphic)

        # Создаем PlotWidget
        plot_widget = pg.PlotWidget()
        plot_widget.setBackground("w")

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
            pen=pg.mkPen((0, 0, 255, 255), width=2),
            name=f"Line {TypeLine.MIN_LEVEL_LOGGING.value}",
        )

        plot_widget.plot(
            self.list_value_x,
            self.list_value_y_max_logging,
            pen=pg.mkPen((0, 0, 255, 255), width=2),
            name=f"Line {TypeLine.ECONOMIC_MAX_LINE.value}",
        )

        plot_widget.plot(
            self.list_value_x,
            self.list_value_y_min_economic,
            pen=pg.mkPen((255, 0, 255, 255), width=2),
            name=f"Line {TypeLine.ECONOMIC_MIN_LINE.value}",
        )
        # scatter_before = pg.ScatterPlotItem(
        #     pos=list(zip(self.list_value_x, self.list_value_y_min_economic)),
        #     size=10,
        #     pen=pg.mkPen(None),
        #     brush=pg.mkBrush(0, 255, 0),  # Зеленый цвет
        #     symbol='o'
        # )
        # plot_widget.addItem(scatter_before)

        # Заливка между линиями
        polygon = pg.FillBetweenItem(
            curve1=pg.PlotDataItem(self.list_value_x, self.list_value_y_min_economic),
            curve2=pg.PlotDataItem(self.list_value_x, self.list_value_y_max_logging),
            brush=pg.mkBrush(color=(0, 0, 0, 15)),
        )
        plot_widget.addItem(polygon)

        # Повторяем линию минимального уровня рубки (для видимости)
        plot_widget.plot(
            self.list_value_x,
            self.list_value_y_min_logging,
            pen=pg.mkPen((0, 0, 255, 255), width=2),
            name=f"Line {TypeLine.MIN_LEVEL_LOGGING.value}",
        )

        # Линия возраста рубки
        if self.flag_save_forest:
            target_value = self.age_thinning_save
        else:
            target_value = self.age_thinning
        plot_widget.plot(
            [target_value, target_value],
            [self.y_min, self.y_max],
            pen=pg.mkPen((0, 0, 0, 255), width=2),
            name="Line thinning forest",
        )

        if self.start_point:
            scatter = pg.ScatterPlotItem(
                pos=[(self.start_point[0], self.start_point[1])],
                size=10,
                pen=pg.mkPen(None),
                brush=pg.mkBrush(0, 255, 0),
                symbol="o",
            )
            plot_widget.addItem(scatter)

        # Линия несущей способности
        if self.list_value_y_bearing_line:
            plot_widget.plot(
                self.list_value_x,
                self.list_value_y_bearing_line,
                pen=pg.mkPen((0, 255, 0, 255), width=2),
                name="Bearing line",
            )
            # scatter_before = pg.ScatterPlotItem(
            #     pos=list(zip(self.list_value_x, self.list_value_y_bearing_line)),
            #     size=10,
            #     pen=pg.mkPen(None),
            #     brush=pg.mkBrush(0, 255, 0),  # Зеленый цвет
            #     symbol='o'
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
            #     symbol='o'
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
        user confirmation, updates the bearing line, and refreshes the plot. Ignores clicks
        outside the valid y-range defined by minimum and maximum logging lines.

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

            self._update_graphic()
            event.accept()
        else:
            super(plot_widget.__class__, plot_widget).mousePressEvent(event)

    def mouseDoubleClickEvent(
        self, plot_widget: pg.PlotWidget, line_x: np.array, line_y: np.array, event: QtGui.QMouseEvent
    ) -> None:
        """Handle double-click events on the predict line to add or correct thinning events.

        Processes double-click events on the thinning prediction line to add a new thinning
        event or correct an existing one if the click is within the detection buffer. Updates
        the thinning data and refreshes the plot.

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
                    print(str("Двойной клик на линии прогнозируемой рубки:" + f"Возраст={x:.0f}, Полнота={y:.1f}"))
                    list_date_thinning = []
                    for item in self.list_record_planned_thinning:
                        list_date_thinning.append(item.get("x"))
                    if x in list_date_thinning:
                        self.predict_model.correct_thinning(date_thinning=x, value_thinning=y)
                        self.list_record_planned_thinning = self.predict_model.get_list_record_planned_thinning()
                        self.list_value_track_thinning = self.predict_model.get_list_value_track_thinning()
                    else:
                        self.predict_model.add_thinning(date_thinning=x)
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

    def replace_graphic(self, type_changed_parameter: TypeSettings = None, new_value_parameter: str = None) -> None:
        """Replace the current graphic with updated area, breed, or condition.

        Updates combo box selections, reinitializes the prediction model with the current
        area, breed, condition, and forest mode, loads the model, retrieves plotting data,
        and updates the prediction and plot.

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

        Updates the area, breed, and condition selections in the UI combo boxes based on the
        changed parameter type (area, breed, or condition) and its new value, ensuring valid
        combinations from the services. Refreshes combo box contents without triggering signals.

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
        """Update prediction data with new bearing parameter or forest mode.

        Updates the bearing parameter (if provided) and protective forest flag, initializes
        the bearing line, runs a thinning simulation, and refreshes the plot. If start_parameter
        is not provided, uses the existing bearing parameter from the model.

        Args:
            start_parameter (str, optional): The new bearing parameter value (converted to float).
                If None, uses the model's current bearing parameter. Defaults to None.
            flag_save_forest (bool, optional): Indicates protective forest mode. If None, retains
                the current mode. Defaults to None.

        Returns:
            None

        Raises:
            ValueError: If start_parameter is provided but cannot be converted to a float.
        """
        if flag_save_forest is not None:
            self.flag_save_forest = flag_save_forest
            self.predict_model.set_flag_save_forest(flag_save_forest=flag_save_forest)
        if self.list_value_y_bearing_line:
            self.predict_model.simulation_thinning()
            self.predict_model.initialize_track_thinning()
            self.list_value_track_thinning = self.predict_model.get_list_value_track_thinning()
            self.list_record_planned_thinning = self.predict_model.get_list_record_planned_thinning()
        self._update_graphic()

        self.create_blocks_with_thinning_data()

    def create_blocks_with_thinning_data(self) -> None:
        """Create UI information blocks for thinning simulation data.

        Clears existing blocks in the scroll area and generates new information blocks for
        each thinning event in the simulation, displaying growth and felling dates, and
        reserve values before and after thinning.

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

        past_x = 0
        # Создаем новые блоки с данными
        if self.list_record_planned_thinning:
            for record in self.list_record_planned_thinning:
                new_x, past_value, new_value = record.get("x"), record.get("past_value"), record.get("new_value")

                info_block = self._create_info_block(
                    date_growth=past_x, date_fell=new_x, reserve_before=past_value, reserve_after=new_value
                )
                blocks_layout.addWidget(info_block)

                past_x = new_x


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
