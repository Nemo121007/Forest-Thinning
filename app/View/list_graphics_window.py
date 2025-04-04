"""Module for the List Graphics Window.

This module contains the ListGraphicsWindow class, which is responsible for displaying
the list of graphics and providing functionality to add, edit, and delete graphics.
It uses PySide6 for the GUI components and inherits from QWidget.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QGridLayout,
    QScrollArea,
)
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt
from ..background_information.Type_settings import TypeSettings
from ..background_information.Reference_data import ReferenceData
from ..background_information.Type_action import TypeAction
from ..View.create_form import CreateForm
from ..View.add_forest import AddForest


class ListGraphicsWindow(QWidget):
    """Class representing the List Graphics Window.

    This class is responsible for displaying the list of graphics and providing
    functionality to add, edit, and delete graphics.
    It inherits from QWidget and uses PySide6 for the GUI components.

    Attributes:
        scroll_table (QScrollArea): Scroll area for displaying the graphics table.
        scroll_areas (QScrollArea): Scroll area for displaying the list of areas.
        scroll_breeds (QScrollArea): Scroll area for displaying the list of breeds.
        scroll_types_conditions (QScrollArea): Scroll area for displaying the list of conditions.
    """

    def __init__(self) -> None:
        """Initialize the ListGraphicsWindow.

        Sets up the UI components and layout for the window.
        """
        super().__init__()
        self.scroll_table = None
        self.setWindowTitle("Список графиков")
        self.setGeometry(0, 0, 1000, 800)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("white"))
        self.setPalette(palette)

        layout = QVBoxLayout()

        list_components = self._get_list_components()
        layout.addWidget(list_components)

        list_graphics = self._get_list_graphics()
        layout.addWidget(list_graphics)

        self.setLayout(layout)

        self.refresh_ui()

    def _get_list_components(self) -> QWidget:
        main_widget = QWidget()
        main_widget.setContentsMargins(5, 5, 5, 5)

        horizontal_layout = QHBoxLayout()
        main_widget.setLayout(horizontal_layout)

        areas_layout = QVBoxLayout()
        areas_names = QLabel("Регионы")
        areas_layout.addWidget(areas_names)

        scroll_areas = QScrollArea()
        scroll_areas.setWidgetResizable(True)
        self.scroll_areas = scroll_areas
        areas_layout.addWidget(scroll_areas)

        btn_add_area = QPushButton("Добавить регион")
        btn_add_area.setFixedHeight(50)
        btn_add_area.setStyleSheet("background-color: #D5E8D4; text-align: center;")
        btn_add_area.clicked.connect(lambda: self._add_block(type_settings=TypeSettings.AREA))
        areas_layout.addWidget(btn_add_area)

        # Для пород (breeds)
        breeds_layout = QVBoxLayout()
        breeds_names = QLabel("Породы")
        breeds_layout.addWidget(breeds_names)

        scroll_breeds = QScrollArea()
        self.scroll_breeds = scroll_breeds
        scroll_breeds.setWidgetResizable(True)
        breeds_layout.addWidget(scroll_breeds)

        btn_add_breed = QPushButton("Добавить породу")
        btn_add_breed.setFixedHeight(50)
        btn_add_breed.setStyleSheet("background-color: #D5E8D4; text-align: center;")
        btn_add_breed.clicked.connect(lambda: self._add_block(type_settings=TypeSettings.BREED))
        breeds_layout.addWidget(btn_add_breed)

        # Для типов условий (types_conditions)
        types_conditions_layout = QVBoxLayout()
        types_conditions_names = QLabel("Типы условий")
        types_conditions_layout.addWidget(types_conditions_names)

        scroll_types_conditions = QScrollArea()
        self.scroll_types_conditions = scroll_types_conditions
        scroll_types_conditions.setWidgetResizable(True)
        types_conditions_layout.addWidget(scroll_types_conditions)

        btn_add_types_conditions = QPushButton("Добавить тип условий")
        btn_add_types_conditions.setFixedHeight(50)
        btn_add_types_conditions.setStyleSheet("background-color: #D5E8D4; text-align: center;")
        btn_add_types_conditions.clicked.connect(lambda: self._add_block(type_settings=TypeSettings.CONDITION))
        types_conditions_layout.addWidget(btn_add_types_conditions)

        horizontal_layout.addLayout(areas_layout)
        horizontal_layout.addLayout(breeds_layout)
        horizontal_layout.addLayout(types_conditions_layout)

        return main_widget

    def _create_item_block(self, str_line: str, type_settings: TypeSettings) -> QWidget:
        main_widget = QWidget()
        main_widget.setFixedHeight(45)
        layout_block = QHBoxLayout(main_widget)

        label = QLabel(str_line)
        layout_block.addWidget(label)

        btn_item_block_edit = QPushButton()
        btn_item_block_edit.setFixedSize(30, 30)
        btn_item_block_edit.setStyleSheet("background-color: #D5E8D4; text-align: center;")
        btn_item_block_edit.clicked.connect(lambda: self._edit_block(str_line=str_line, type_settings=type_settings))
        layout_block.addWidget(btn_item_block_edit)

        btn_item_block_delete = QPushButton()
        btn_item_block_delete.setFixedSize(30, 30)
        btn_item_block_delete.setStyleSheet("background-color: #F8CECC; text-align: center;")
        btn_item_block_delete.clicked.connect(
            lambda: self._delete_block(str_line=str_line, type_settings=type_settings)
        )
        layout_block.addWidget(btn_item_block_delete)

        return main_widget

    def _get_list_graphics(self) -> QWidget:
        main_widget = QWidget()
        main_widget.setContentsMargins(5, 5, 5, 5)

        main_layout = QVBoxLayout(main_widget)

        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setSpacing(0)

        headers = ["Регионы", "Породы", "Условия", ""]
        for i, header_text in enumerate(headers):
            label = QLabel(header_text)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("background-color: lightgray; border: 1px solid black; font-weight: bold;")
            if i == 3:  # Четвертый столбец (индекс 3)
                label.setFixedWidth(50)  # Фиксированная ширина для заголовка кнопки
            else:
                label.setMinimumWidth(150)  # Минимальная ширина для масштабируемых колонок
                header_layout.addWidget(label, 1)  # Первые три столбца равномерно
                continue
            header_layout.addWidget(label)  # Четвертый столбец не растягивается

        scroll_table = QScrollArea()
        scroll_table.setWidgetResizable(True)
        self.scroll_table = scroll_table

        content_widget = QWidget()
        content_layout = QGridLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Устанавливаем политику растяжения столбцов
        content_layout.setColumnStretch(0, 1)  # Регионы
        content_layout.setColumnStretch(1, 1)  # Породы
        content_layout.setColumnStretch(2, 1)  # Условия
        content_layout.setColumnStretch(3, 0)  # Четвертый столбец не растягивается

        scroll_table.setWidget(content_widget)

        add_button = QPushButton("+")
        add_button.setFixedHeight(50)
        add_button.setStyleSheet("background-color: #D5E8D4; text-align: center;")
        add_button.clicked.connect(lambda: self._add_block(type_settings=TypeSettings.GRAPHIC))

        main_layout.addWidget(header_widget, 0)  # Заголовки не растягиваются
        main_layout.addWidget(scroll_table, 1)  # Прокручиваемая область занимает остальное пространство
        main_layout.addWidget(add_button, 0)  # Кнопка "Добавить" не растягивается

        return main_widget

    def refresh_ui(self) -> None:
        """Refreshes the UI by updating the scroll areas and graphics table."""
        self._update_scroll_areas(
            scroll_area=self.scroll_areas, items=ReferenceData.get_list_areas(), type_settings=TypeSettings.AREA
        )
        self._update_scroll_areas(
            scroll_area=self.scroll_breeds, items=ReferenceData.get_list_breeds(), type_settings=TypeSettings.BREED
        )
        self._update_scroll_areas(
            scroll_area=self.scroll_types_conditions,
            items=ReferenceData.get_list_type_conditions(),
            type_settings=TypeSettings.CONDITION,
        )
        self._update_graphics_table()

    def _update_scroll_areas(self, scroll_area: QScrollArea, items: list, type_settings: TypeSettings) -> None:
        blocks_widget = QWidget()
        blocks_layout = QVBoxLayout(blocks_widget)

        for index, item in enumerate(items):
            item_block = self._create_item_block(str_line=item, type_settings=type_settings)
            if index % 2 == 0:
                item_block.setStyleSheet("background-color: #FFFFFF;")
            else:
                item_block.setStyleSheet("background-color: #D3D3D3;")
            blocks_layout.addWidget(item_block)

        blocks_layout.addStretch()

        scroll_area.setWidget(blocks_widget)

    def _update_graphics_table(self) -> None:
        try:
            content_widget = QWidget()
            content_layout = QGridLayout(content_widget)
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.setSpacing(0)

            content_layout.setAlignment(Qt.AlignTop)  # Выравнивание содержимого по верху

            # Устанавливаем растяжение столбцов
            content_layout.setColumnStretch(0, 1)  # Регионы
            content_layout.setColumnStretch(1, 1)  # Породы
            content_layout.setColumnStretch(2, 1)  # Условия
            content_layout.setColumnStretch(3, 0)  # Кнопка удаления не растягивается

            graphics_data = list(ReferenceData.get_list_graphics())

            for row, (area, breed, condition) in enumerate(graphics_data):
                for col, text in enumerate([area, breed, condition]):
                    label = QLabel(text)
                    label.setAlignment(Qt.AlignCenter)
                    label.setStyleSheet("border: 1px solid black;")
                    if row % 2 == 0:
                        label.setStyleSheet(label.styleSheet() + "background-color: #FFFFFF;")
                    else:
                        label.setStyleSheet(label.styleSheet() + "background-color: #D3D3D3;")
                    content_layout.addWidget(label, row, col)

                delete_button = QPushButton("")
                delete_button.setFixedWidth(50)
                delete_button.setStyleSheet("background-color: #F8CECC; border: 1px solid black;")
                delete_button.clicked.connect(
                    lambda checked, a=area, b=breed, c=condition: self._delete_graphic(area=a, breed=b, condition=c)
                )
                content_layout.addWidget(delete_button, row, 3)

            self.scroll_table.setWidget(content_widget)

        except Exception as e:
            print(f"Error refresh table graphics: {e}")

    def _edit_block(self, str_line: str, type_settings: TypeSettings) -> None:
        if type_settings == TypeSettings.GRAPHIC:
            raise ValueError("Unidentified operation edit")
        edit_form = CreateForm(type_action=TypeAction.UPDATE, type_settings=type_settings, name_element=str_line)
        edit_form.form_closed.connect(self.refresh_ui)
        edit_form.show()
        pass

    def _add_block(self, type_settings: TypeSettings) -> None:
        if type_settings == TypeSettings.GRAPHIC:
            create_form = AddForest()
        else:
            create_form = CreateForm(type_action=TypeAction.CREATE, type_settings=type_settings)
        create_form.form_closed.connect(self.refresh_ui)
        create_form.show()
        pass

    def _delete_block(self, str_line: str, type_settings: TypeSettings) -> None:
        if type_settings == TypeSettings.AREA:
            ReferenceData.delete_area(name_areas=str_line)
        elif type_settings == TypeSettings.BREED:
            ReferenceData.delete_breed(name_breed=str_line)
        elif type_settings == TypeSettings.CONDITION:
            ReferenceData.delete_type_condition(type_condition=str_line)
        self.refresh_ui()
        pass

    def _delete_graphic(self, area: str, breed: str, condition: str) -> None:
        ReferenceData.delete_graphic(name_area=area, name_breed=breed, name_condition=condition)
        self.refresh_ui()
        pass
