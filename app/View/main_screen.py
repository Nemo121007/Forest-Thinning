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
)
from PySide6.QtGui import QColor, QPalette
import sys
import pyqtgraph as pg

from .list_graphics_window import ListGraphicsWindow
from ..Services.AreasService import AreasService
from ..Services.BreedsService import BreedsService
from ..Services.ConditionsService import ConditionsService
from ..Services.GraphicsService import GraphicsService
from ..Services.PredictModelServices import PredictModelService
from ..background_information.Type_line import Type_line


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
        self.list_value_x: list[float] = None
        self.list_value_y_min_logging: list[float] = None
        self.list_value_y_max_logging: list[float] = None
        self.list_value_y_min_economic: list[float] = None

        self.list_value_y_bearing_line: list[float] = None
        self.list_value_track_thinning: list[float] = None
        self.list_record_planned_thinning: list[dict[str, float]] = None

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

        self.set_list_parameter()

        self._update_graphic()

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
        forest_widget.addWidget(forest_area)
        forest_widget.addWidget(forest_combo)
        main_setting.addLayout(forest_widget, 0, 0)

        # Виджет для основной породы
        breed_widget = QVBoxLayout()
        main_breed = QLabel("Основная порода")
        breed_combo = QComboBox()
        self.form_combo_breed = breed_combo
        breed_widget.addWidget(main_breed)
        breed_widget.addWidget(breed_combo)
        main_setting.addLayout(breed_widget, 0, 1)

        # Виджет для типа условий
        conditions_widget = QVBoxLayout()
        type_conditions = QLabel("Тип условий")
        conditions_combo = QComboBox()
        self.form_combo_condition = conditions_combo
        conditions_widget.addWidget(type_conditions)
        conditions_widget.addWidget(conditions_combo)
        main_setting.addLayout(conditions_widget, 1, 0)

        # Виджет для защитного леса
        save_widget = QVBoxLayout()
        save_forest = QLabel("Защитный лес")
        save_combo = QComboBox()
        save_widget.addWidget(save_forest)
        save_widget.addWidget(save_combo)
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
        self.start_parameter_edit_field = start_parameter_edit_field
        start_parameter_layout.addWidget(start_parameter_widget)
        start_parameter_layout.addWidget(start_parameter_edit_field)
        current_settings.addWidget(start_parameter_layout_widget, 0, 0)

        auto_mode = QPushButton("Автоматический режим")
        auto_mode.clicked.connect(lambda: self.update_graphic(start_parameter=self.start_parameter_edit_field.text()))
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

    def set_list_parameter(self) -> None:
        """Populate combo boxes with area, breed, and condition data.

        Retrieves lists of areas, breeds, and conditions from services, populates the
        respective combo boxes, and sets the current selections. Loads the initial
        graphic code and prediction model.

        Returns:
            None
        """
        self.list_areas = self.manager_areas.get_list_areas()
        self.list_breeds = self.manager_breeds.get_list_breeds()
        self.list_conditions = self.manager_conditions.get_list_conditions()
        self.form_combo_area.addItems(self.list_areas)
        self.form_combo_breed.addItems(self.list_breeds)
        self.form_combo_condition.addItems(self.list_conditions)
        self.name_area = self.form_combo_area.currentText()
        self.name_breed = self.form_combo_breed.currentText()
        self.name_condition = self.form_combo_condition.currentText()
        self.name_graphic_code = self.manager_graphic.get_value_graphic(
            name_area=self.name_area, name_breed=self.name_breed, name_condition=self.name_condition
        )
        self.load_predict_model()

    def update_graphic(self, start_parameter: str) -> None:
        """Update the graphic data with a new bearing parameter.

        Sets the bearing parameter in the prediction model, initializes the bearing line,
        retrieves the bearing line data, runs a thinning simulation, and updates the plot
        with the new data.

        Args:
            start_parameter (str): The starting parameter value (converted to float) for the bearing line.

        Returns:
            None

        Raises:
            ValueError: If the start_parameter cannot be converted to a float.
        """
        start_parameter = float(start_parameter)
        self.predict_model.set_bearing_parameter(bearing_parameter=start_parameter)
        self.predict_model.initialize_bearing_line()
        self.list_value_y_bearing_line = self.predict_model.get_bearing_line()
        self.list_value_y_track_thinning, self.list_record_planned_thinning = self.predict_model.simulation_thinning()
        self._update_graphic()

    def load_predict_model(self) -> None:
        """Load the prediction model and update plotting data.

        Initializes the prediction model with the current area, breed, condition, and
        protective forest flag, loads the model, and retrieves data for plotting
        (x/y ranges and prediction lines).

        Returns:
            None
        """
        self.predict_model.initialize_predict_model(
            area=self.name_area,
            breed=self.name_breed,
            condition=self.name_condition,
            flag_save_forest=self.flag_save_forest,
        )
        self.predict_model.load_model()
        self.x_min, self.x_max, self.y_min, self.y_max = self.predict_model.get_min_max_value()
        self.predict_model.initialize_base_line_graph(x_start=self.x_min, x_end=self.x_max)
        (
            self.list_value_x,
            self.list_value_y_min_logging,
            self.list_value_y_max_logging,
            self.list_value_y_min_economic,
        ) = self.predict_model.get_base_lines_graph()
        self.list_value_y_bearing_line = self.predict_model.get_bearing_line()
        self.list_value_y_track_thinning, self.list_record_planned_thinning = self.predict_model.simulation_thinning()

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
        blocks_container.setFixedWidth(250)
        blocks_info_layout = QVBoxLayout(blocks_container)
        blocks_info_layout.setContentsMargins(5, 0, 5, 0)

        # Создаем виджет с прокруткой
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: #ffffff;")

        # Создаем контейнер для блоков информации
        blocks_widget = QWidget()
        blocks_layout = QVBoxLayout(blocks_widget)
        blocks_layout.setContentsMargins(5, 5, 5, 5)
        blocks_layout.setSpacing(5)

        # Добавляем несколько информационных блоков для примера
        for _ in range(10):  # Создаем 5 блоков
            info_block = self._create_info_block()
            blocks_layout.addWidget(info_block)

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

    def _create_info_block(self) -> QWidget:
        """Create an information block for growth and logging data.

        Constructs a grid layout with labels for growth date, felling date, reserve, volume,
        and intensity metrics, styled with a blue background.

        Returns:
            QWidget: The information block widget.
        """
        main_info_block = QWidget()
        main_info_block.setStyleSheet("background-color: #DAE8FC;")
        main_info_block.setContentsMargins(5, 0, 5, 0)
        main_info_block.setFixedWidth(250)

        main_info_block_layout = QGridLayout(main_info_block)
        main_info_block_layout.setContentsMargins(5, 0, 5, 0)
        main_info_block_layout.setSpacing(5)

        date_growth = QLabel("Дата роста")
        date_growth.setFixedHeight(20)
        date_growth.setFixedWidth(90)
        main_info_block_layout.addWidget(date_growth, 0, 0)

        date_fell = QLabel("Дата рубки")
        date_fell.setFixedHeight(20)
        date_fell.setFixedWidth(90)
        main_info_block_layout.addWidget(date_fell, 0, 1)

        reserve_before = QLabel("Запас до")
        reserve_before.setFixedHeight(20)
        reserve_before.setFixedWidth(90)
        main_info_block_layout.addWidget(reserve_before, 1, 0)

        reserve_after = QLabel("Запас после")
        reserve_after.setFixedHeight(20)
        reserve_after.setFixedWidth(90)
        main_info_block_layout.addWidget(reserve_after, 1, 1)

        value_before = QLabel("Объём до")
        value_before.setFixedHeight(20)
        value_before.setFixedWidth(90)
        main_info_block_layout.addWidget(value_before, 2, 0)

        value_after = QLabel("Объём после")
        value_after.setFixedHeight(20)
        value_after.setFixedWidth(90)
        main_info_block_layout.addWidget(value_after, 2, 1)

        intensity_by_reserve = QLabel("Интенсивность по запасу")
        intensity_by_reserve.setFixedHeight(20)
        intensity_by_reserve.setFixedWidth(90)
        main_info_block_layout.addWidget(intensity_by_reserve, 3, 0)

        intensity_by_volume = QLabel("Интенсивность по объёму")
        intensity_by_volume.setFixedHeight(20)
        intensity_by_volume.setFixedWidth(90)
        main_info_block_layout.addWidget(intensity_by_volume, 3, 1)

        main_info_block.setLayout(main_info_block_layout)

        return main_info_block

    def _update_graphic(self) -> None:
        """Update the plot widget with prediction data.

        Creates or updates a pyqtgraph PlotWidget to display minimum logging, maximum
        logging, and economic minimum lines, with a filled area between economic minimum
        and maximum logging lines. Sets axis labels and limits based on model data.

        Returns:
            None
        """
        if not hasattr(self, "graphic_layout"):
            self.graphic_layout = QVBoxLayout(self.graphic)

        plot_widget = pg.PlotWidget()
        plot_widget.setBackground("w")

        # Устанавливаем фиксированные пределы осей
        plot_widget.setXRange(self.x_min, self.x_max, padding=0)  # для оси X от 0 до 120
        plot_widget.setYRange(self.y_min, self.y_max, padding=0)  # для оси Y от 0 до 1

        # Отключаем автоматическое масштабирование
        plot_widget.setAutoVisible(y=False)
        plot_widget.enableAutoRange(enable=False)

        # Ограничиваем возможность прокрутки
        plot_widget.setLimits(xMin=self.x_min, xMax=self.x_max, yMin=self.y_min, yMax=self.y_max)

        plot_widget.plot(
            self.list_value_x,
            self.list_value_y_min_logging,
            pen=pg.mkPen((0, 0, 255, 255), width=2),
            name=f"Line {Type_line.MIN_LEVEL_LOGGING.value}",
        )
        plot_widget.plot(
            self.list_value_x,
            self.list_value_y_max_logging,
            pen=pg.mkPen((0, 0, 255, 255), width=2),
            name=f"Line {Type_line.ECONOMIC_MAX_LINE.value}",
        )
        plot_widget.plot(
            self.list_value_x,
            self.list_value_y_min_economic,
            pen=pg.mkPen((255, 0, 255, 255), width=2),
            name=f"Line {Type_line.ECONOMIC_MIN_LINE.value}",
        )

        polygon = pg.FillBetweenItem(
            curve1=pg.PlotDataItem(self.list_value_x, self.list_value_y_min_economic),
            curve2=pg.PlotDataItem(self.list_value_x, self.list_value_y_max_logging),
            brush=pg.mkBrush(color=(0, 0, 0, 15)),
        )
        plot_widget.addItem(polygon)

        plot_widget.plot(
            self.list_value_x,
            self.list_value_y_bearing_line,
            pen=pg.mkPen((0, 255, 0, 255), width=2),
            name=f"Line {Type_line.ECONOMIC_MIN_LINE.value}",
        )

        x_gr = []
        y_gr = []
        for item in self.list_value_y_track_thinning:
            x_gr.append(item["x"])
            y_gr.append(item["value"])
        plot_widget.plot(
            x_gr,
            y_gr,
            pen=pg.mkPen("r", width=2),
            name=f"Line {Type_line.ECONOMIC_MIN_LINE.value}",
        )

        print(self.list_record_planned_thinning)

        # for key, item in self.graph.dict_line.items():

        #         plot_widget.plot(x_args, y_predict, pen=pg.mkPen("r", width=2), name=f"Line {type_line.value}")

        plot_widget.addLegend()
        plot_widget.setLabel("left", "Полнота")
        plot_widget.setLabel("bottom", "Возраст, лет")

        if self.graphic_layout.count() > 0:
            self.graphic_layout.itemAt(0).widget().setParent(None)

        self.graphic_layout.addWidget(plot_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
