"""File with main screen of the application."""

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
)
from PySide6.QtGui import QColor, QPalette
import sys
import numpy as np
import pyqtgraph as pg

from ..Model.Graph import Graph
from ..background_information.Type_line import Type_line
from .list_graphics_window import ListGraphicsWindow
from ..Services.AreasService import AreasService
from ..Services.BreedsService import BreedsService
from ..Services.ConditionsService import ConditionsService


class MainWindow(QWidget):
    """Class for main window of the application.

    Attributes:
        None

    Methods:
        __init__: Create main window of the application.
        create_header: Create header part of the screen.
        create_info: Create info part of the screen.
        create_main_part: Create main part of the screen
    """

    def __init__(self):
        """Create main window of the application.

        Args:
            None

        Returns:
            None
        """
        super().__init__()

        self.manager_areas = AreasService()
        self.manager_breeds = BreedsService()
        self.manager_conditions = ConditionsService()

        self.setWindowTitle("Прототип экрана")
        self.setGeometry(0, 0, 1024, 768)  # Окно

        # Главный фон
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("white"))
        self.setPalette(palette)

        # Основная вертикальная компоновка
        layout = QVBoxLayout()

        # Создание заголовка
        header = self.create_header()
        layout.addWidget(header)

        # Область информации
        info = self.create_info()
        layout.addWidget(info)

        # Основная область
        content = self.create_main_part()
        layout.addWidget(content)

        self.setLayout(layout)

        self.areas = self.manager_areas.get_list()
        self.breeds = self.manager_breeds.get_list()
        self.types_conditions = self.manager_conditions.get_list()

        graph = Graph(name="pine_sorrel")
        self.graph = graph
        self.graph.load_graph()
        self._update_graphic()

        pass

    def create_header(self) -> QWidget:
        """Create header part of the screen.

        Args:
            None

        Returns:
            QWidget: Header part of the screen.
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

    def open_list_graphics(self):
        """Open list graphics window."""
        self.list_graphics_window = ListGraphicsWindow()
        self.list_graphics_window.show()

    def create_info(self) -> QWidget:
        """Create info part of the screen.

        Args:
            None

        Returns:
            QWidget: Info part of the screen.
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

        forest_area = QLabel("Лесной район")
        main_setting.addWidget(forest_area, 0, 0)
        main_breed = QLabel("Основная порода")
        main_setting.addWidget(main_breed, 0, 1)
        type_conditions = QLabel("Тип условий")
        main_setting.addWidget(type_conditions, 1, 0)
        save_forest = QLabel("Защитный лес")
        main_setting.addWidget(save_forest, 1, 1)

        main_setting_widget.setLayout(main_setting)

        current_settings_widget = QWidget()
        current_settings_widget.setFixedWidth(331)

        current_settings = QGridLayout()
        current_settings.setContentsMargins(5, 0, 5, 0)
        current_settings.setSpacing(5)

        age = QLabel("Возраст")
        current_settings.addWidget(age, 0, 0)
        auto_mode = QLabel("Автоматический режим")
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
        """Create main part of the screen.

        Args:
            None

        Returns:
            QWidget: Main part of the screen.
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
        """Generate information block.

        Args:
            None

        Returns:
            QWidget: Information block.
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

    def _update_graphic(self):
        x_min = self.graph.x_min
        x_max = self.graph.x_max
        delta = x_max - x_min
        x_min = x_min - delta * 0.1
        x_max = x_max + delta * 0.1

        y_min = self.graph.y_min
        y_max = self.graph.y_max
        delta = y_max - y_min
        y_min = y_min - delta * 0.1
        y_max = y_max + delta * 0.1

        if not hasattr(self, "graphic_layout"):
            self.graphic_layout = QVBoxLayout(self.graphic)

        plot_widget = pg.PlotWidget()
        plot_widget.setBackground("w")

        # Устанавливаем фиксированные пределы осей
        plot_widget.setXRange(x_min, x_max, padding=0)  # для оси X от 0 до 120
        plot_widget.setYRange(y_min, y_max, padding=0)  # для оси Y от 0 до 1

        # Отключаем автоматическое масштабирование
        plot_widget.setAutoVisible(y=False)
        plot_widget.enableAutoRange(enable=False)

        # Ограничиваем возможность прокрутки
        plot_widget.setLimits(xMin=x_min, xMax=x_max, yMin=y_min, yMax=y_max)

        # Создаем базовый массив X от 0 до 120 с шагом 0.5
        x_values = np.arange(x_min, x_max + 0.5, 0.5)

        for key, item in self.graph.dict_line.items():
            type_line = item.type_line

            if type_line == Type_line.GROWTH_LINE:
                # Для growth line создаем пучок линий с start_parameter от 21 до 35
                for start_param in range(21, 36, 2):
                    y_predict = []
                    x_args = []
                    for x in x_values:
                        predict = self.graph.predict(type_line=type_line, X=x, start_parameter=start_param)
                        if predict:
                            y_predict.append(predict)
                            x_args.append(x)
                    plot_widget.plot(x_args, y_predict, pen=pg.mkPen("g", width=2), name=f"Line {type_line.value}")

            elif type_line == Type_line.RECOVERY_LINE:
                # Для recovery line создаем пучок линий с start_parameter от 0 до 120
                for start_param in range(20, 121, 5):
                    y_predict = []
                    x_args = []
                    for x in x_values:
                        predict = self.graph.predict(type_line=type_line, X=x, start_parameter=start_param)
                        if predict:
                            y_predict.append(predict)
                            x_args.append(x)
                    plot_widget.plot(x_args, y_predict, pen=pg.mkPen("b", width=2), name=f"Line {type_line.value}")

            else:
                # Для уникальных линий используем start_parameter = 0
                y_predict = []
                x_args = []
                for x in x_values:
                    predict = self.graph.predict(type_line=type_line, X=x, start_parameter=0)
                    if predict:
                        y_predict.append(predict)
                        x_args.append(x)
                plot_widget.plot(x_args, y_predict, pen=pg.mkPen("r", width=2), name=f"Line {type_line.value}")

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
