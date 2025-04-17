"""Module for updating elements in a PySide6-based GUI application.

This module provides the UpdateForm class, which allows users to update existing elements
(Areas, Breeds, or Conditions) through a graphical interface. It handles validation,
data retrieval, and interaction with respective services for persistence.
"""

from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import Signal
from ..background_information.TypeSettings import TypeSettings
from ..background_information.General_functions import validate_name, validate_float
from .ElementForm import ElementForm
from ..Services.AreasService import AreasService
from ..Services.BreedsService import BreedsService
from ..Services.ConditionsService import ConditionsService


class UpdateForm(ElementForm):
    """A form for updating existing elements in a PySide6-based GUI application.

    This class extends ElementForm to provide a user interface for modifying existing
    elements of type Area, Breed, or Condition. It retrieves current data, populates
    form fields, validates user input, and updates the element through the appropriate
    service (AreasService, BreedsService, or ConditionsService).

    Attributes:
        form_closed (Signal): Emitted when the form is closed.
        manager_areas (AreasService): Service for managing Area elements.
        manager_breeds (BreedsService): Service for managing Breed elements.
        manager_conditions (ConditionsService): Service for managing Condition elements.
        name_element (str): The name of the element being updated.
        old_name_element (str): The original name of the element before updates.
        file_name_element (str): The code or identifier of the element.
        age_thinning (float, optional): The age thinning value for Breed elements.
        age_thinning_save (float, optional): The age thinning save value for Breed elements.
    """

    form_closed = Signal()

    def __init__(self, type_settings: TypeSettings, name_element: str) -> None:
        """Initialize the UpdateForm with specified type settings and element name.

        Args:
            type_settings (TypeSettings): The type of settings (AREA, BREED, or CONDITION).
            name_element (str): The name of the element to be updated.
        """
        self.manager_areas = AreasService()
        self.manager_breeds = BreedsService()
        self.manager_conditions = ConditionsService()

        super().__init__(type_settings)
        self.name_element = name_element
        self.old_name_element = name_element
        self.setWindowTitle(f"Изменение {name_element}")

        # Получение существующих данных
        if type_settings == TypeSettings.AREA:
            self.file_name_element = self.manager_areas.get_value_area(name=name_element)
        elif type_settings == TypeSettings.BREED:
            self.file_name_element = self.manager_breeds.get_value_breed(name=name_element)
            self.age_thinning = self.manager_breeds.get_age_thinning_breed(name=name_element)
            self.age_thinning_save = self.manager_breeds.get_age_thinning_save_breed(name=name_element)
        elif type_settings == TypeSettings.CONDITION:
            self.file_name_element = self.manager_conditions.get_value_condition(name=name_element)

        self._populate_fields()

    def _populate_fields(self) -> None:
        """Populate form fields with existing element data.

        Fills the form fields with the current values of the element, including name, code,
        and breed-specific fields (age_thinning, age_thinning_save) if applicable.

        Returns:
            None
        """
        self.form_name.setText(self.name_element)
        self.form_code_name.setText(self.file_name_element)
        if self.type_settings == TypeSettings.BREED:
            self.form_age_input.setText(str(self.age_thinning))
            self.form_age_save_input.setText(str(self.age_thinning_save))

    def _save_element(self) -> None:
        """Save the updated element data.

        Validates the input fields and updates the element in the appropriate service
        (AreasService, BreedsService, or ConditionsService). Displays an error message
        if validation fails or an exception occurs during saving.

        Returns:
            None

        Raises:
            Exception: If an error occurs during the update process in the respective service.
        """
        name = self.form_name.text()
        code_name = self.form_code_name.text()
        flag_error = [False, False, False, False]
        age_thinning = None
        age_thinning_save = None

        if self.type_settings == TypeSettings.BREED:
            if validate_float(self.form_age_input.text().replace(",", ".")) is None:
                flag_error[2] = True
                self.form_age_input.setStyleSheet("border: 1px solid red; border-radius: 5px; padding: 2px;")
            else:
                age_thinning = float(self.form_age_input.text().replace(",", "."))
                self.form_age_input.setStyleSheet("border: 1px solid gray; border-radius: 5px; padding: 2px;")
            if validate_float(self.form_age_save_input.text().replace(",", ".")) is None:
                flag_error[3] = True
                self.form_age_save_input.setStyleSheet("border: 1px solid red; border-radius: 5px; padding: 2px;")
            else:
                age_thinning_save = float(self.form_age_save_input.text().replace(",", "."))
                self.form_age_save_input.setStyleSheet("border: 1px solid gray; border-radius: 5px; padding: 2px;")

        if self.type_settings == TypeSettings.AREA:
            if (self.old_name_element != name and self.manager_areas.exist_name_area(name)) or not validate_name(name):
                flag_error[0] = True
            if (
                self.manager_areas.get_value_area(self.old_name_element) != code_name
                and self.manager_areas.exist_code_area(code_name)
            ) or not validate_name(code_name):
                flag_error[1] = True
        elif self.type_settings == TypeSettings.BREED:
            if (self.old_name_element != name and self.manager_breeds.exist_name_breed(name)) or not validate_name(
                name
            ):
                flag_error[0] = True
            if (
                self.manager_breeds.get_value_breed(self.old_name_element) != code_name
                and self.manager_breeds.exist_code_breed(code_name)
            ) or not validate_name(code_name):
                flag_error[1] = True
        elif self.type_settings == TypeSettings.CONDITION:
            if (
                self.old_name_element != name and self.manager_conditions.exist_name_condition(name)
            ) or not validate_name(name):
                flag_error[0] = True
            if (
                self.manager_conditions.get_value_condition(self.old_name_element) != code_name
                and self.manager_conditions.exist_code_condition(code_name)
            ) or not validate_name(code_name):
                flag_error[1] = True

        self.form_name.setStyleSheet("border: 1px solid gray; border-radius: 5px; padding: 2px;")
        self.form_code_name.setStyleSheet("border: 1px solid gray; border-radius: 5px; padding: 2px;")

        if True in flag_error:
            if flag_error[0]:
                self.form_name.setStyleSheet("border: 1px solid red; border-radius: 5px; padding: 2px;")
            if flag_error[1]:
                self.form_code_name.setStyleSheet("border: 1px solid red; border-radius: 5px; padding: 2px;")
            return

        try:
            if self.type_settings == TypeSettings.AREA:
                self.manager_areas.update_area(old_name=self.old_name_element, name=name, code=code_name)
            elif self.type_settings == TypeSettings.BREED:
                self.manager_breeds.update_breed(
                    old_name=self.old_name_element,
                    name=name,
                    code=code_name,
                    age_thinning=age_thinning,
                    age_thinning_save=age_thinning_save,
                )
            elif self.type_settings == TypeSettings.CONDITION:
                self.manager_conditions.update_condition(old_name=self.old_name_element, name=name, code=code_name)
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
