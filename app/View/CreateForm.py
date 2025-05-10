"""Module for creating new elements in a PySide6-based GUI application.

This module provides the CreateForm class, which extends ElementForm to allow users to
create new elements of type Area, Breed, or Condition. It handles input validation and
interacts with respective services for adding new elements to the system.
"""

from PySide6.QtWidgets import QMessageBox, QWidget
from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import Signal
from ..background_information.TypeSettings import TypeSettings
from ..background_information.General_functions import validate_name, validate_float
from .ElementForm import ElementForm
from ..Services.AreasService import AreasService
from ..Services.BreedsService import BreedsService
from ..Services.ConditionsService import ConditionsService
from ..background_information.SettingView import SettingsView


class CreateForm(ElementForm, QWidget):
    """A form for creating new elements in a PySide6-based GUI application.

    This class extends ElementForm and QWidget to provide a user interface for adding new
    elements of type Area, Breed, or Condition. It validates user input using validate_name
    and validate_float, applies styles from SettingsView for field validation, and uses
    the appropriate service (AreasService, BreedsService, or ConditionsService) to persist
    the new element.

    Attributes:
        form_closed (Signal): Emitted when the form is closed, inherited from ElementForm.
        manager_areas (AreasService): Service for managing Area elements.
        manager_breeds (BreedsService): Service for managing Breed elements.
        manager_conditions (ConditionsService): Service for managing Condition elements.
        form_name (QLineEdit): Input field for the element's name, inherited from ElementForm.
        form_code_name (QLineEdit): Input field for the element's code, inherited from ElementForm.
        form_age_input (QLineEdit, optional): Input field for breed age thinning (BREED only),
            inherited from ElementForm.
        form_age_save_input (QLineEdit, optional): Input field for breed age thinning save
            (BREED only), inherited from ElementForm.
    """

    form_closed = Signal()

    def __init__(self, type_settings: TypeSettings):
        """Initialize the CreateForm with specified type settings.

        Sets up the form by calling ElementForm's initializer to create the UI, sets a title
        indicating the type of element being created, and initializes services for persistence.
        Styles are applied from SettingsView.

        Args:
            type_settings (TypeSettings): The type of element (AREA, BREED, or CONDITION).

        Returns:
            None
        """
        super().__init__(type_settings)

        self.manager_areas = AreasService()
        self.manager_breeds = BreedsService()
        self.manager_conditions = ConditionsService()

        self.setWindowTitle(f"Добавление {type_settings.value}")

    def _save_element(self):
        """Save the new element data.

        Validates input fields (name, code, and breed-specific fields if applicable) using
        validate_name and validate_float. Checks for duplicate names or codes via the
        respective service. Applies SettingsView.error_border to invalid fields and
        SettingsView.true_border to valid ones. Adds the new element using the appropriate
        service and closes the form on success. Exits early if validation fails, displaying
        an error message if an exception occurs.

        Returns:
            None

        Raises:
            Exception: If an error occurs during the addition process in the respective service.
        """
        name = self.form_name.text()
        code_name = self.form_code_name.text()
        flag_error = [False, False, False, False]
        age_thinning = None
        age_thinning_save = None

        # Валидация возраста рубки для BREED
        if self.type_settings == TypeSettings.BREED:
            if validate_float(self.form_age_input.text().replace(",", ".")) is None:
                flag_error[2] = True
                self.form_age_input.setStyleSheet(SettingsView.error_border)
            else:
                age_thinning = float(self.form_age_input.text().replace(",", "."))
                self.form_age_input.setStyleSheet(SettingsView.true_border)
            if validate_float(self.form_age_save_input.text().replace(",", ".")) is None:
                flag_error[3] = True
                self.form_age_save_input.setStyleSheet(SettingsView.error_border)
            else:
                age_thinning_save = float(self.form_age_save_input.text().replace(",", "."))
                self.form_age_save_input.setStyleSheet(SettingsView.true_border)

        if self.type_settings == TypeSettings.AREA:
            if self.manager_areas.exist_name_area(name) or not validate_name(name):
                flag_error[0] = True
            if self.manager_areas.exist_code_area(code_name) or not validate_name(code_name):
                flag_error[1] = True
        elif self.type_settings == TypeSettings.BREED:
            if self.manager_breeds.exist_name_breed(name) or not validate_name(name):
                flag_error[0] = True
            if self.manager_breeds.exist_code_breed(code_name) or not validate_name(code_name):
                flag_error[1] = True
        elif self.type_settings == TypeSettings.CONDITION:
            if self.manager_conditions.exist_name_condition(name) or not validate_name(name):
                flag_error[0] = True
            if self.manager_conditions.exist_code_condition(code_name) or not validate_name(code_name):
                flag_error[1] = True

        # Сброс стилей перед проверкой ошибок
        self.form_name.setStyleSheet(SettingsView.true_border)
        self.form_code_name.setStyleSheet(SettingsView.true_border)

        # Обработка ошибок валидации
        if True in flag_error:
            if flag_error[0]:
                self.form_name.setStyleSheet(SettingsView.error_border)
            if flag_error[1]:
                self.form_code_name.setStyleSheet(SettingsView.error_border)
            return

        try:
            if self.type_settings == TypeSettings.AREA:
                self.manager_areas.add_area(name=name, code=code_name)
            elif self.type_settings == TypeSettings.BREED:
                self.manager_breeds.add_breed(
                    name=name, code=code_name, age_thinning=age_thinning, age_thinning_save=age_thinning_save
                )
            elif self.type_settings == TypeSettings.CONDITION:
                self.manager_conditions.add_condition(name=name, code=code_name)
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при сохранении: {str(e)}")

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
