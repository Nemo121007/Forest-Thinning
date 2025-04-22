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
)
from PySide6.QtGui import QColor, QPalette
import sys
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
        self.start_parameter: float = None
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

        self.replace_graphic()

        # self.set_list_parameter()

        # self._update_graphic()

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
        self.start_parameter_edit_field = start_parameter_edit_field
        start_parameter_edit_field.textChanged.connect(
            lambda: self.replace_predict(start_parameter=start_parameter_edit_field.text())
        )
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
        main_info_block_layout.addWidget(btn_cancel, 0, 4)

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
        increase_x = (self.x_max - self.x_min) * Settings.INCREASE_GRAPHIC
        increase_y = (self.y_max - self.y_min) * Settings.INCREASE_GRAPHIC

        if self.flag_save_forest:
            x_max = self.age_thinning_save
        else:
            x_max = self.age_thinning
        x_min = self.x_min

        plot_widget.setXRange(x_min - increase_x, x_max + increase_x, padding=0)
        plot_widget.setYRange(self.y_min - increase_y, self.y_max + increase_y, padding=0)

        # Отключаем автоматическое масштабирование
        plot_widget.setAutoVisible(y=False)
        plot_widget.enableAutoRange(enable=False)

        # Ограничиваем возможность прокрутки
        plot_widget.setLimits(
            xMin=x_min - increase_y, xMax=x_max + increase_x, yMin=self.y_min - increase_y, yMax=self.y_max + increase_y
        )

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

        polygon = pg.FillBetweenItem(
            curve1=pg.PlotDataItem(self.list_value_x, self.list_value_y_min_economic),
            curve2=pg.PlotDataItem(self.list_value_x, self.list_value_y_max_logging),
            brush=pg.mkBrush(color=(0, 0, 0, 15)),
        )
        plot_widget.addItem(polygon)

        plot_widget.plot(
            self.list_value_x,
            self.list_value_y_min_logging,
            pen=pg.mkPen((0, 0, 255, 255), width=2),
            name=f"Line {TypeLine.MIN_LEVEL_LOGGING.value}",
        )

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
        plot_widget.plot(
            [self.x_min, self.x_min],
            [self.y_min, self.y_max],
            pen=pg.mkPen((0, 0, 0, 255), width=2),
            name="Line thinning forest",
        )

        end_index = next((i for i, x in enumerate(self.list_value_x) if x > target_value), len(self.list_value_x))
        list_x = self.list_value_x[:end_index]
        list_bearing_line = self.list_value_y_bearing_line[:end_index]
        plot_widget.plot(
            list_x,
            list_bearing_line,
            pen=pg.mkPen((0, 255, 0, 255), width=2),
            name="Bearing line",
        )

        plot_widget.plot(
            self.list_value_y_track_thinning.get("x"),
            self.list_value_y_track_thinning.get("y"),
            pen=pg.mkPen("r", width=2),
            name="Predict line thinning",
        )

        print(self.list_record_planned_thinning)

        plot_widget.addLegend()
        plot_widget.setLabel("left", "Полнота")
        plot_widget.setLabel("bottom", "Возраст, лет")

        if self.graphic_layout.count() > 0:
            self.graphic_layout.itemAt(0).widget().setParent(None)

        self.graphic_layout.addWidget(plot_widget)

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
            ValueError: If one of type_changed_parameter or new_value_parameter is provided without the other.
        """
        if (type_changed_parameter is not None and new_value_parameter is None) or (
            type_changed_parameter is None and new_value_parameter is not None
        ):
            raise ValueError("Both parameters must be provided or both must be None.")

        self.changed_combo_boxes(type_changed_parameter=type_changed_parameter, new_value_parameter=new_value_parameter)

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
        (
            self.list_value_x,
            self.list_value_y_min_logging,
            self.list_value_y_max_logging,
            self.list_value_y_min_economic,
        ) = self.predict_model.get_base_lines_graph()

        self.start_parameter = None

        self.replace_predict()

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

    def replace_predict(self, start_parameter: str = None, flag_safe_forest: bool = False) -> None:
        """Update prediction data with new bearing parameter or forest mode.

        Updates the bearing parameter and protective forest flag, initializes the bearing
        line, runs a thinning simulation, and refreshes the plot. Sets the initial bearing
        parameter from the model if not provided.

        Args:
            start_parameter (str, optional): The new bearing parameter value (converted to float). Defaults to None.
            flag_safe_forest (bool, optional): Indicates protective forest mode. Defaults to False.

        Returns:
            None

        Raises:
            ValueError: If start_parameter cannot be converted to a float when provided.
        """
        if self.start_parameter is None and start_parameter is None:
            self.start_parameter = int(self.predict_model.get_bearing_parameter())

            self.start_parameter_edit_field.blockSignals(True)
            self.start_parameter_edit_field.setText(str(self.start_parameter))
            self.start_parameter_edit_field.blockSignals(False)
        if start_parameter is not None and start_parameter.replace(",", "").replace(".", "").isdigit():
            start_parameter = start_parameter.replace(",", ".")
            start_parameter = float(start_parameter)
            if (
                start_parameter > self.list_value_y_min_logging[0]
                and start_parameter < self.list_value_y_max_logging[0]
            ):
                self.start_parameter = start_parameter

        self.predict_model.set_bearing_parameter(bearing_parameter=self.start_parameter)
        self.list_value_y_bearing_line = self.predict_model.get_bearing_line()

        if flag_safe_forest is not None and flag_safe_forest != self.flag_save_forest:
            self.flag_save_forest = flag_safe_forest
            self.predict_model.set_flag_save_forest(flag_save_forest=self.flag_save_forest)

        self.list_value_y_track_thinning, self.list_record_planned_thinning = self.predict_model.simulation_thinning()

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
