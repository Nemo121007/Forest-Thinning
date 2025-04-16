"""Module for the List Graphics Window in a PySide6-based GUI application.

This module contains the ListGraphicsWindow class, which provides a user interface for
displaying and managing a list of graphics, areas, breeds, and conditions. It supports
adding, editing, and deleting these elements through interaction with respective services,
using PySide6 for GUI components.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QGridLayout,
    QScrollArea,
    QMessageBox,
)
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt
from ..background_information.TypeSettings import TypeSettings
from .AddForest import AddForest
from .CreateForm import CreateForm
from .UpdateForm import UpdateForm
from ..Services.AreasService import AreasService
from ..Services.BreedsService import BreedsService
from ..Services.ConditionsService import ConditionsService
from ..Services.GraphicsService import GraphicsService


class ListGraphicsWindow(QWidget):
    """A window for displaying and managing graphics, areas, breeds, and conditions.

    This class provides a PySide6-based GUI to display lists of areas, breeds, conditions,
    and graphics in scrollable areas and a table. It supports adding, editing, and deleting
    these elements via buttons, with validation to prevent deletion of used items. It
    interacts with services (AreasService, BreedsService, ConditionsService, GraphicsService)
    to manage data persistence.

    Attributes:
        scroll_table (QScrollArea): Scroll area for the graphics table.
        scroll_areas (QScrollArea): Scroll area for the list of areas.
        scroll_breeds (QScrollArea): Scroll area for the list of breeds.
        scroll_types_conditions (QScrollArea): Scroll area for the list of conditions.
        manager_areas (AreasService): Service for managing Area elements.
        manager_breeds (BreedsService): Service for managing Breed elements.
        manager_conditions (ConditionsService): Service for managing Condition elements.
        manager_graphics (GraphicsService): Service for managing graphic entries.
        forms (list): List of open form windows (CreateForm, UpdateForm, AddForest).
    """

    def __init__(self) -> None:
        """Initialize the ListGraphicsWindow.

        Sets up the window title, geometry, background, UI components, and services.
        Initializes scroll areas and refreshes the UI to populate data.
        """
        super().__init__()

        self.forms = []  # Список для хранения открытых форм

        self.manager_areas = AreasService()
        self.manager_breeds = BreedsService()
        self.manager_conditions = ConditionsService()
        self.manager_graphics = GraphicsService()

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
        """Create and configure the component lists for areas, breeds, and conditions.

        Returns a widget containing three vertical layouts, each with a label, a scroll
        area for items, and an add button for areas, breeds, and conditions.

        Returns:
            QWidget: A widget containing the component lists arranged horizontally.
        """
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
        """Create a block for an item in a scroll area.

        Creates a widget with a label for the item name and buttons for editing and
        deleting. The delete button is disabled (gray) if the item is used in graphics.

        Args:
            str_line (str): The name of the item (area, breed, or condition).
            type_settings (TypeSettings): The type of item (AREA, BREED, or CONDITION).

        Returns:
            QWidget: A widget containing the item label and action buttons.
        """
        if type_settings == TypeSettings.AREA:
            flag_used = self.manager_areas.check_used_area(str_line)
        elif type_settings == TypeSettings.BREED:
            flag_used = self.manager_breeds.check_used_breed(str_line)
        elif type_settings == TypeSettings.CONDITION:
            flag_used = self.manager_conditions.check_used_condition(str_line)
        else:
            flag_used = False

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
        if not flag_used:
            btn_item_block_delete.setStyleSheet("background-color: #F8CECC; text-align: center;")
            btn_item_block_delete.clicked.connect(
                lambda: self._delete_block(str_line=str_line, type_settings=type_settings)
            )
        else:
            btn_item_block_delete.setStyleSheet("background-color: gray; text-align: center;")
            btn_item_block_delete.clicked.connect(
                lambda: QMessageBox.critical(self, "Ошибка", f"Данный {type_settings.value} используется в графиках")
            )
        layout_block.addWidget(btn_item_block_delete)

        return main_widget

    def _get_list_graphics(self) -> QWidget:
        """Create and configure the graphics table with an add button.

        Returns a widget containing a header row, a scrollable table of graphics
        (area, breed, condition, delete button), and an add button for new graphics.

        Returns:
            QWidget: A widget containing the graphics table and add button.
        """
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
        """Refresh all UI elements in the window.

        Updates the scroll areas for areas, breeds, and conditions, and the graphics table
        with the latest data from the respective services.

        Returns:
            None
        """
        self._update_scroll_areas(
            scroll_area=self.scroll_areas, items=self.manager_areas.get_list_areas(), type_settings=TypeSettings.AREA
        )
        self._update_scroll_areas(
            scroll_area=self.scroll_breeds,
            items=self.manager_breeds.get_list_breeds(),
            type_settings=TypeSettings.BREED,
        )
        self._update_scroll_areas(
            scroll_area=self.scroll_types_conditions,
            items=self.manager_conditions.get_list_conditions(),
            type_settings=TypeSettings.CONDITION,
        )
        self._update_graphics_table()

    def _update_scroll_areas(self, scroll_area: QScrollArea, items: list, type_settings: TypeSettings) -> None:
        """Update a scroll area with a list of items.

        Populates the scroll area with item blocks (name, edit/delete buttons) for the
        given items, alternating background colors for readability.

        Args:
            scroll_area (QScrollArea): The scroll area to update.
            items (list): List of item names to display.
            type_settings (TypeSettings): The type of items (AREA, BREED, or CONDITION).

        Returns:
            None
        """
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
        """Update the graphics table with the latest data.

        Populates the table with graphics data (area, breed, condition) and a delete
        button for each row. Alternates row colors for readability.

        Returns:
            None

        Raises:
            Exception: If an error occurs while retrieving or displaying graphics data.
        """
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

            graphics_data = list(self.manager_graphics.get_list_graphics())

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
                    lambda checked, a=area, b=breed, c=condition: self._delete_graphic(
                        area=area, breed=breed, condition=condition
                    )
                )
                content_layout.addWidget(delete_button, row, 3)

            self.scroll_table.setWidget(content_widget)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении таблицы: {str(e)}")

    # TODO: Проверить переполнение списков форм
    def _edit_block(self, str_line: str, type_settings: TypeSettings) -> None:
        """Open a form to edit an existing item.

        Opens an UpdateForm for the specified item. Tracks the form and refreshes the UI
        when it closes.

        Args:
            str_line (str): The name of the item to edit.
            type_settings (TypeSettings): The type of item (AREA, BREED, or CONDITION).

        Returns:
            None

        Raises:
            ValueError: If type_settings is GRAPHIC, as editing graphics is not supported.
        """
        if type_settings == TypeSettings.GRAPHIC:
            raise ValueError("Unidentified operation edit")
        edit_form = UpdateForm(type_settings=type_settings, name_element=str_line)
        self.forms.append(edit_form)
        edit_form.form_closed.connect(self.refresh_ui)
        edit_form.form_closed.connect(lambda: self.forms.clear())
        edit_form.show()

    def _add_block(self, type_settings: TypeSettings) -> None:
        """Open a form to add a new item or graphic.

        Opens a CreateForm for areas, breeds, or conditions, or an AddForest form for
        graphics. Tracks the form and refreshes the UI when it closes.

        Args:
            type_settings (TypeSettings): The type of item or graphic to add (AREA, BREED, CONDITION, or GRAPHIC).

        Returns:
            None
        """
        if type_settings == TypeSettings.GRAPHIC:
            create_form = AddForest()
        else:
            create_form = CreateForm(type_settings=type_settings)
        self.forms.append(create_form)  # Сохраняем ссылку
        create_form.form_closed.connect(self.refresh_ui)
        create_form.form_closed.connect(lambda: self.forms.clear())  # Удаляем при закрытии
        create_form.show()

    def _delete_block(self, str_line: str, type_settings: TypeSettings) -> None:
        """Delete an item if it is not used in graphics.

        Deletes the specified item using the appropriate service and refreshes the UI.
        Displays an error if the item is used in graphics.

        Args:
            str_line (str): The name of the item to delete.
            type_settings (TypeSettings): The type of item (AREA, BREED, or CONDITION).

        Returns:
            None

        Raises:
            RuntimeError: If the item is used in graphics and cannot be deleted.
        """
        if type_settings == TypeSettings.AREA:
            if not self.manager_areas.check_used_area(str_line):
                self.manager_areas.delete_area(name=str_line)
            else:
                raise RuntimeError(f"{type_settings.value} {str_line} used in graphic")
        elif type_settings == TypeSettings.BREED:
            if not self.manager_breeds.check_used_breed(str_line):
                self.manager_breeds.delete_breed(name=str_line)
            else:
                raise RuntimeError(f"{type_settings.value} {str_line} used in graphic")
        elif type_settings == TypeSettings.CONDITION:
            if not self.manager_conditions.check_used_condition(str_line):
                self.manager_conditions.delete_condition(name=str_line)
            else:
                raise RuntimeError(f"{type_settings.value} {str_line} used in graphic")
        self.refresh_ui()
        pass

    def _delete_graphic(self, area: str, breed: str, condition: str) -> None:
        """Delete a graphic entry.

        Removes the specified graphic using GraphicsService and refreshes the UI.

        Args:
            area (str): The area of the graphic.
            breed (str): The breed of the graphic.
            condition (str): The condition of the graphic.

        Returns:
            None
        """
        self.manager_graphics.delete_graphic(name_area=area, name_breed=breed, name_condition=condition)
        self.refresh_ui()
        pass
