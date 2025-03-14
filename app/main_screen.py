"""File with main screen of the application."""

from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QGridLayout
from PySide6.QtGui import QColor, QPalette
import sys


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
        self.setWindowTitle("Прототип экрана")
        self.setGeometry(100, 100, 1024, 768)  # Окно

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
        btn_settings = QPushButton("Настройки")
        btn_settings.setFixedWidth(150)
        btn_settings.setStyleSheet("background-color: #D5E8D4;")
        header_layout.addWidget(btn_list_graphics)
        header_layout.addWidget(btn_settings)

        return header

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

        graphic = QWidget()
        graphic.setStyleSheet("background-color: #DAE8FC; text-align: center;")
        graphic.setFixedWidth(800)
        main_layout.addWidget(graphic)

        # Создаем контейнер для блоков информации
        blocks_container = QWidget()
        blocks_info_layout = QVBoxLayout(blocks_container)
        blocks_info_layout.setContentsMargins(5, 0, 5, 0)

        blocks_info = QWidget()
        blocks_info.setStyleSheet("background-color: #ffffff; text-align: center;")
        blocks_info_layout.addWidget(blocks_info)

        btn_block_info = QPushButton("Добавить блок")
        btn_block_info.setFixedHeight(50)
        btn_block_info.setStyleSheet("background-color: #D5E8D4; text-align: center;")
        blocks_info_layout.addWidget(btn_block_info)

        main_layout.addWidget(blocks_container)
        main.setLayout(main_layout)

        return main


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
