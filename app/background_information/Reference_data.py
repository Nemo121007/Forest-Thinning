"""Module for managing reference data.

This module provides a class ReferenceData that manages reference data related to areas,
breeds, types of conditions, and graphics.
It includes methods for initializing, saving, and manipulating reference data.
It uses a JSON file to store the data and provides methods to add, delete,
and update areas, breeds, and types of conditions.
It also provides methods to retrieve lists of areas, breeds, and types of conditions.
"""

from app.background_information.Paths import Paths
import json


class ReferenceData:
    """Class for managing reference data.

    This class provides methods to initialize, save, and manipulate reference data
    related to areas, breeds, types of conditions, and graphics.
    It uses a JSON file to store the data and provides methods to add, delete,
    and update areas, breeds, and types of conditions.
    It also provides methods to retrieve lists of areas, breeds, and types of conditions.
    """

    _private_areas = {}
    _private_breeds = {}
    _private_types_conditions = {}
    _private_graphics = {}
    _flag_initialize = False
    _flag_transaction = False

    @staticmethod
    def initialize_reference_data():
        """Initialize reference data from a file.

        This method loads reference data from a JSON file if it exists.
        If the file does not exist, it creates a new one with default values.
        It also sets the flag to indicate that the reference data has been initialized.

        Raises:
            OSError: If there is an error while loading the file.
        """
        if ReferenceData._flag_initialize:
            return
        elif Paths.REFERENCE_DATA.exists():
            with open(Paths.REFERENCE_DATA, encoding="utf-8") as file:
                reference_data = json.load(file)
            ReferenceData._private_areas = reference_data["areas"]
            ReferenceData._private_breeds = reference_data["breeds"]
            ReferenceData._private_types_conditions = reference_data["types_conditions"]
            try:
                graphics = reference_data["graphics"]
            except KeyError:
                graphics = {}
            for key, value in dict(graphics).items():
                area, breed, condition = str(key).split("_")
                ReferenceData._private_graphics[(area, breed, condition)] = value
        else:
            ReferenceData.save_data()
        ReferenceData._flag_initialize = True

    @staticmethod
    def save_data():
        """Save reference data to a file.

        This method creates a JSON file with the reference data if it does not exist.
        It also saves the current state of areas, breeds, types_conditions, and graphics.
        If the file already exists, it will be overwritten.

        Raises:
            OSError: If there is an error while saving the file.
        """
        if ReferenceData._flag_transaction:
            return
        if not Paths.REFERENCE_DATA.exists():
            Paths.REFERENCE_DATA.parent.mkdir(parents=True, exist_ok=True)
            Paths.REFERENCE_DATA.touch()

        graphics = {}
        for (area, breed, condition), value in ReferenceData._private_graphics.items():
            key_str = f"{area}_{breed}_{condition}"
            graphics[key_str] = value

        reference_data = {
            "areas": ReferenceData._private_areas,
            "breeds": ReferenceData._private_breeds,
            "types_conditions": ReferenceData._private_types_conditions,
            "graphics": graphics,
        }
        try:
            with open(Paths.REFERENCE_DATA, "w", encoding="utf-8") as file:
                json.dump(reference_data, file, indent=4, ensure_ascii=False)
        except OSError as e:
            raise OSError(f"Error save file: {e}")

    @staticmethod
    def get_list_areas() -> list:
        """Get list of areas from the reference data.

        Returns:
            list: List of areas.
        """
        ReferenceData.initialize_reference_data()
        return ReferenceData._private_areas.keys()

    @staticmethod
    def get_value_area(name: str) -> str:
        """Get value of area from the reference data.

        Args:
            name (str): Name of the area.
        """
        return ReferenceData._private_areas.get(name, {}).get("value")

    @staticmethod
    def get_age_thinning_area(name: str) -> float:
        """Get age thinning area from the reference data.

        Args:
            name (str): Name of the area.
        """
        return float(ReferenceData._private_areas[name]["age_thinning"])

    @staticmethod
    def get_age_thinning_save_area(name: str) -> float:
        """Get age thinning save area from the reference data.

        Args:
            name (str): Name of the area.
        """
        return float(ReferenceData._private_areas[name]["age_thinning_save"])

    @staticmethod
    def get_list_breeds() -> list:
        """Get list of breeds from the reference data.

        Returns:
            list: List of breeds.
        """
        ReferenceData.initialize_reference_data()
        return ReferenceData._private_breeds.keys()

    @staticmethod
    def get_value_breed(name: str) -> str:
        """Get value of breed from the reference data.

        Args:
            name (str): Name of the breed.
        """
        return ReferenceData._private_breeds.get(name)

    @staticmethod
    def get_list_type_conditions() -> list:
        """Get list of type conditions from the reference data.

        Returns:
            list: List of type conditions.
        """
        ReferenceData.initialize_reference_data()
        return ReferenceData._private_types_conditions.keys()

    @staticmethod
    def get_value_types_conditions(name: str) -> str:
        """Get value of type conditions from the reference data.

        Args:
            name (str): Name of the type conditions.

        Returns:
            str: Value of the type conditions.

        Raises:
            ValueError: If the type conditions does not exist.
        """
        return ReferenceData._private_types_conditions.get(name)

    @staticmethod
    def add_area(name_area: str, area_file_name: str, age_thinning: int, age_thinning_save: int) -> None:
        """Add area to the reference data.

        Args:
            name_area (str): Name of the area.
            area_file_name (str): File name of the area.
            age_thinning (int): Age of thinning.
            age_thinning_save (int): Age of thinning save.

        Returns:
            None
        Raises:
            ValueError: If the area already exists.
        """
        ReferenceData._private_areas[name_area] = {
            "value": area_file_name,
            "age_thinning": age_thinning,
            "age_thinning_save": age_thinning_save,
        }
        ReferenceData.save_data()

    @staticmethod
    def delete_area(name_area: str) -> None:
        """Delete area from the reference data.

        Args:
            name_area (str): Name of the area.

        Returns:
            None
        Raises:
            ValueError: If the area does not exist.
        """
        del ReferenceData._private_areas[name_area]
        ReferenceData.save_data()

    @staticmethod
    def update_area(
        old_name_area: str, name_area: str, area_file_name: str, age_thinning: int, age_thinning_save: int
    ) -> None:
        """Update area in the reference data.

        Args:
            old_name_area (str): Old name of the area.
            name_area (str): New name of the area.
            area_file_name (str): File name of the area.
            age_thinning (int): Age of thinning.
            age_thinning_save (int): Age of thinning save.

        Returns:
            None
        Raises:
            ValueError: If the area does not exist.
        """
        ReferenceData._flag_transaction = True
        ReferenceData.delete_area(name_area=old_name_area)
        ReferenceData.add_area(
            name_area=name_area,
            area_file_name=area_file_name,
            age_thinning=age_thinning,
            age_thinning_save=age_thinning_save,
        )
        ReferenceData._flag_transaction = False
        ReferenceData.save_data()

    @staticmethod
    def add_breeds(breed_file_name: str, name_breed: str) -> None:
        """Add breed to the reference data.

        Args:
            breed_file_name (str): File name of the breed.
            name_breed (str): Name of the breed.

        Returns:
            None
        Raises:
            ValueError: If the breed already exists.
        """
        ReferenceData._private_breeds[name_breed] = breed_file_name
        ReferenceData.save_data()

    @staticmethod
    def delete_breed(name_breed: str) -> None:
        """Delete breed from the reference data.

        Args:
            name_breed (str): Name of the breed.

        Returns:
            None
        Raises:
            ValueError: If the breed does not exist.
        """
        del ReferenceData._private_breeds[name_breed]
        ReferenceData.save_data()

    @staticmethod
    def update_breeds(old_name_breed: str, name_breed: str, breed_file_name: str) -> None:
        """Update breeds in the reference data.

        Args:
            old_name_breed (str): Old name of the breed.
            name_breed (str): New name of the breed.
            breed_file_name (str): File name of the breed.

        Returns:
            None
        Raises:
            ValueError: If the breed does not exist.
        """
        ReferenceData._flag_transaction = True
        ReferenceData.delete_breed(name_breed=old_name_breed)
        ReferenceData.add_breeds(name_breed=name_breed, breed_file_name=breed_file_name)
        ReferenceData._flag_transaction = False
        ReferenceData.save_data()

    @staticmethod
    def add_type_conditions(condition_file_name: str, name_type_conditions: str) -> None:
        """Add type conditions to the reference data.

        Args:
            condition_file_name (str): File name of the condition.
            name_type_conditions (str): Name of the type condition.

        Returns:
            None
        Raises:
            ValueError: If the type condition already exists.
        """
        ReferenceData._private_types_conditions[name_type_conditions] = condition_file_name
        ReferenceData.save_data()

    @staticmethod
    def delete_type_condition(type_condition: str) -> None:
        """Delete type condition from the reference data.

        Args:
            type_condition (str): Name of the type condition.

        Returns:
            None
        Raises:
            ValueError: If the type condition does not exist.
        """
        del ReferenceData._private_types_conditions[type_condition]
        ReferenceData.save_data()

    @staticmethod
    def update_type_conditions(
        old_name_type_condition: str, name_type_conditions: str, condition_file_name: str
    ) -> None:
        """Update type conditions in the reference data.

        Args:
            old_name_type_condition (str): Old name of the type condition.
            name_type_conditions (str): New name of the type condition.
            condition_file_name (str): File name of the condition.

        Returns:
            None
        Raises:
            ValueError: If the type condition does not exist.
        """
        ReferenceData._flag_transaction = True
        ReferenceData.delete_type_condition(type_condition=old_name_type_condition)
        ReferenceData.add_type_conditions(
            name_type_conditions=name_type_conditions, condition_file_name=condition_file_name
        )
        ReferenceData._flag_transaction = False
        ReferenceData.save_data()

    @staticmethod
    def get_list_graphics() -> list:
        """Get list of graphics from the reference data.

        Returns:
            list: List of graphics.
        """
        ReferenceData.initialize_reference_data()
        return ReferenceData._private_graphics.keys()

    @staticmethod
    def get_value_graphic(name_area: str, name_breed: str, name_condition: str) -> str:
        """Get graphic data from the reference data.

        Args:
            name_area (str): Name of the area.
            name_breed (str): Name of the breed.
            name_condition (str): Name of the condition.

        Returns:
            str: Graphic data.

        Raises:
            ValueError: If the area, breed, or condition does not exist.
        """
        return ReferenceData._private_graphics.get((name_area, name_breed, name_condition))

    @staticmethod
    def add_graphic(name_area: str, name_breed: str, name_condition: str, path_file_data: str) -> None:
        """Add graphic data to the reference data.

        Args:
            name_area (str): Name of the area.
            name_breed (str): Name of the breed.
            name_condition (str): Name of the condition.
            path_file_data (str): Path to the graphic data file.

        Returns:
            None
        Raises:
            ValueError: If the area, breed, or condition does not exist.
        """
        if not (
            ReferenceData._private_areas.__contains__(name_area)
            and ReferenceData._private_breeds.__contains__(name_breed)
            and ReferenceData._private_types_conditions.__contains__(name_condition)
        ):
            raise ValueError("Invalid parameter value")
        ReferenceData._private_graphics[(name_area, name_breed, name_condition)] = str(
            ReferenceData.get_value_area(name=name_area)
            + ReferenceData.get_value_breed(name=name_breed)
            + ReferenceData.get_value_types_conditions(name=name_condition)
        )
        print(path_file_data)
        ReferenceData.save_data()

    @staticmethod
    def delete_graphic(name_area: str, name_breed: str, name_condition: str) -> None:
        """Delete graphic data from the reference data.

        Args:
            name_area (str): Name of the area.
            name_breed (str): Name of the breed.
            name_condition (str): Name of the condition.

        Returns:
            None
        Raises:
            ValueError: If the area, breed, or condition does not exist.
        """
        del ReferenceData._private_graphics[(name_area, name_breed, name_condition)]
        ReferenceData.save_data()


# TODO: Затереть в финальной версии
if __name__ == "__main__":
    ReferenceData.add_area(name_area="Регион1", area_file_name="Region1", age_thinning=1, age_thinning_save=1)
    ReferenceData.add_area(name_area="Регион2", area_file_name="Region2", age_thinning=1, age_thinning_save=1)
    ReferenceData.add_breeds(name_breed="Порода1", breed_file_name="Breed1")
    ReferenceData.add_breeds(name_breed="Порода2", breed_file_name="Breed2")
    ReferenceData.add_type_conditions(name_type_conditions="Условия1", condition_file_name="Condition1")
    ReferenceData.add_type_conditions(name_type_conditions="Условия2", condition_file_name="Condition2")

    ReferenceData.add_graphic(
        name_area="Регион1", name_breed="Порода1", name_condition="Условия1", path_file_data="path_file_1"
    )

    ReferenceData._private_areas.clear()
    ReferenceData._private_breeds.clear()
    ReferenceData._private_types_conditions.clear()
    ReferenceData._private_graphics.clear()
    ReferenceData._flag_initialize = False

    ReferenceData.initialize_reference_data()
    a = ReferenceData._private_graphics

    ReferenceData.save_data()
    pass
