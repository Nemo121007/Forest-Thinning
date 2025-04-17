"""Module for managing graphics data in a reference data system.

This module provides the Graphics class, which handles graphic data associated with areas,
breeds, and conditions. It supports operations like adding, deleting, and querying graphics,
managing file storage, and tracking usage across related entities.
"""

import copy
import os
from pathlib import Path
import shutil
import tarfile
from ...background_information.Paths import Paths
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .Areas import Areas
    from .Breeds import Breeds
    from .Conditions import Conditions


class Graphics:
    """A class for managing graphics data associated with areas, breeds, and conditions.

    Handles storage, manipulation, and retrieval of graphic data, including file operations
    for storing graphic files and tracking usage in related Areas, Breeds, and Conditions
    entities. Provides methods to query graphics, generate file names, and ensure data
    consistency.

    Attributes:
        _data (dict): Dictionary mapping (area, breed, condition) tuples to graphic file names.
        _areas (Areas): The Areas entity for validating and tracking area usage.
        _breeds (Breeds): The Breeds entity for validating and tracking breed usage.
        _conditions (Conditions): The Conditions entity for validating and tracking condition usage.
    """

    def __init__(self, areas: "Areas", breeds: "Breeds", conditions: "Conditions") -> None:
        """Initialize the Graphics entity.

        Sets up the graphics data structure and links to Areas, Breeds, and Conditions entities.

        Args:
            areas (Areas): The Areas entity for area-related operations.
            breeds (Breeds): The Breeds entity for breed-related operations.
            conditions (Conditions): The Conditions entity for condition-related operations.
        """
        self._data = {}
        self._areas = areas
        self._breeds = breeds
        self._conditions = conditions

    def initialize(self, data: dict) -> None:
        """Initialize graphics data from a dictionary.

        Loads graphics data from the provided dictionary, parsing keys into (area, breed,
        condition) tuples.

        Args:
            data (dict): A dictionary containing graphics data under the 'graphics' key.

        Returns:
            None
        """
        graphics = dict(data.get("graphics", {}))
        self._data = {}
        for key, value in graphics.items():
            area, breed, condition = str(key).split("_")
            self._data[(area, breed, condition)] = value

    def save_data(self, reference_data: dict) -> None:
        """Save graphics data to a reference dictionary.

        Stores graphics data in the provided dictionary under the 'graphics' key, with keys
        formatted as 'area_breed_condition'.

        Args:
            reference_data (dict): The dictionary to store graphics data.

        Returns:
            None
        """
        graphics = {f"{area}_{breed}_{condition}": value for (area, breed, condition), value in self._data.items()}
        reference_data["graphics"] = graphics

    def get_list_graphics(self) -> list[str]:
        """Retrieve a list of all graphics.

        Returns:
            list[str]: A list of (area, breed, condition) tuples representing graphics.
        """
        return list(self._data.keys())

    def exist_graphic(self, name_area: str, name_breed: str, name_condition: str) -> bool:
        """Check if a graphic exists for the given area, breed, and condition.

        Args:
            name_area (str): The name of the area.
            name_breed (str): The name of the breed.
            name_condition (str): The name of the condition.

        Returns:
            bool: True if the graphic exists, False otherwise.
        """
        return (name_area, name_breed, name_condition) in self._data

    def get_value_graphic(self, name_area: str, name_breed: str, name_condition: str) -> str | None:
        """Retrieve the file name associated with a graphic.

        Args:
            name_area (str): The name of the area.
            name_breed (str): The name of the breed.
            name_condition (str): The name of the condition.

        Returns:
            str | None: The file name of the graphic, or None if it does not exist.
        """
        return self._data.get((name_area, name_breed, name_condition))

    def add_graphic(self, name_area: str, name_breed: str, name_condition: str, path_file: str) -> None:
        """Add a new graphic with the specified area, breed, condition, and file path.

        Validates the area, breed, and condition, copies the graphic file to the data directory,
        and updates usage tracking within a transaction.

        Args:
            name_area (str): The name of the area.
            name_breed (str): The name of the breed.
            name_condition (str): The name of the condition.
            path_file (str): The source path of the graphic file.

        Returns:
            None

        Raises:
            ValueError: If the area, breed, or condition is invalid or the graphic already exists.
        """
        if not (
            self._areas.exist_name(name_area)
            and self._breeds.exist_name(name_breed)
            and self._conditions.exist_name(name_condition)
        ):
            raise ValueError("Invalid parameter value")
        if (name_area, name_breed, name_condition) in self._data:
            raise ValueError("Graphic already exists")

        file_name = self.get_name_graphic(name_area, name_breed, name_condition)
        target_path = Paths.DATA_DIRECTORY / f"{file_name}.tar"
        path_file = Path(path_file)
        Paths.DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)

        with self._areas.transaction():
            self._copy_tar_file(path_file=path_file, target_path=target_path, file_name=file_name)
            self._data[(name_area, name_breed, name_condition)] = file_name
            self._areas._used[name_area] = True
            self._breeds._used[name_breed] = True
            self._conditions._used[name_condition] = True

    def _copy_tar_file(self, path_file: Path, target_path: Path, file_name: str) -> None:
        """Copy and restructure a tar file to the target path with a new root directory name.

        Reads the source tar file, renames its root directory to the specified file name,
        and writes the restructured contents to the target tar file.

        Args:
            path_file (Path): The source path of the tar file.
            target_path (Path): The destination path for the new tar file.
            file_name (str): The new name for the root directory in the tar file.

        Returns:
            None

        Raises:
            tarfile.ReadError: If the source tar file cannot be read.
            tarfile.TarError: If an error occurs while creating the new tar file.
        """
        with tarfile.open(path_file, "r") as src_tar, tarfile.open(target_path, "w") as dst_tar:
            # Получаем все элементы архива
            members = src_tar.getmembers()

            # Находим имя корневой папки
            root_dir = next(m for m in members if m.isdir())
            old_dir_name = root_dir.name

            # Копируем каждый файл с новым путем
            for member in members:
                # Читаем содержимое файла если это файл
                if member.isfile():
                    file_content = src_tar.extractfile(member)

                # Создаем новый TarInfo с измененным путем
                new_member = copy.copy(member)
                new_member.name = member.name.replace(old_dir_name, file_name)

                # Добавляем в новый архив
                if member.isfile():
                    dst_tar.addfile(new_member, file_content)
                else:
                    dst_tar.addfile(new_member)

    def delete_graphic(self, name_area: str, name_breed: str, name_condition: str) -> None:
        """Delete a graphic and its associated files.

        Removes the graphic identified by the specified area, breed, and condition from
        the data store, deletes its model directory, model info JSON file, and tar file,
        and updates usage tracking for related entities within a transaction.

        Args:
            name_area (str): The name of the area associated with the graphic.
            name_breed (str): The name of the breed associated with the graphic.
            name_condition (str): The name of the condition associated with the graphic.

        Returns:
            None

        Raises:
            KeyError: If the graphic does not exist in the data store.
            FileNotFoundError: If the model directory, model info file, or tar file is missing.
            OSError: If an error occurs while deleting files or directories.
        """
        name_graphic = self._data[(name_area, name_breed, name_condition)]

        with self._areas.transaction():
            model_path_delete = Paths.MODEL_DIRECTORY / f"{name_graphic}"
            model_info_path_delete = Paths.MODEL_DIRECTORY / f"{name_graphic}.json"
            shutil.rmtree(model_path_delete)
            os.remove(model_info_path_delete)
            tar_path = Paths.DATA_DIRECTORY / f"{name_graphic}.tar"
            os.remove(tar_path)
            del self._data[(name_area, name_breed, name_condition)]
            self.refresh_used_elements()

    def rename_graphic(self, old_name_graphic: str, new_name_graphic: str) -> None:
        """Rename a graphic's model directory and info file.

        Updates the model directory and its associated JSON info file by renaming them
        from the old name to the new name.

        Args:
            old_name_graphic (str): The current name of the graphic (without extension).
            new_name_graphic (str): The new name for the graphic (without extension).

        Returns:
            None

        Raises:
            FileNotFoundError: If the model directory or info file does not exist.
            OSError: If an error occurs while renaming the files.
        """
        model_old_path = Paths.MODEL_DIRECTORY / f"{old_name_graphic}"
        model_info_old_path = Paths.MODEL_DIRECTORY / f"{old_name_graphic}.json"
        model_new_path = Paths.MODEL_DIRECTORY / f"{new_name_graphic}"
        model_info_new_path = Paths.MODEL_DIRECTORY / f"{new_name_graphic}.json"
        model_old_path.rename(model_new_path)
        model_info_old_path.rename(model_info_new_path)

    def get_name_graphic(self, area: str, breed: str, condition: str) -> str:
        """Generate the file name for a graphic based on area, breed, and condition.

        Combines the codes of the area, breed, and condition to form a unique file name.

        Args:
            area (str): The name of the area.
            breed (str): The name of the breed.
            condition (str): The name of the condition.

        Returns:
            str: The generated file name (e.g., 'area_code_breed_code_condition_code').
        """
        return f"{self._areas.get_value(area)}_{self._breeds.get_value(breed)}_{self._conditions.get_value(condition)}"

    def update_name_file_graphic(self, old_name: str, new_name: str) -> None:
        """Rename a graphic file in the data directory.

        Updates the file name by moving it from the old name to the new name.

        Args:
            old_name (str): The current file name (without extension).
            new_name (str): The new file name (without extension).

        Returns:
            None

        Raises:
            TypeError: If old_name or new_name is not a string.
        """
        if not isinstance(old_name, str) or not isinstance(new_name, str):
            raise TypeError("Both old_name and new_name must be strings")
        if old_name == new_name:
            return
        old_path = Paths.DATA_DIRECTORY / f"{old_name}.tar"
        new_path = Paths.DATA_DIRECTORY / f"{new_name}.tar"
        os.rename(old_path, new_path)

    def refresh_used_elements(self) -> None:
        """Refresh usage tracking for areas, breeds, and conditions.

        Resets usage flags for all entities and marks those associated with existing graphics
        as used.

        Returns:
            None
        """
        for key in self._areas._used:
            self._areas._used[key] = False
        for key in self._breeds._used:
            self._breeds._used[key] = False
        for key in self._conditions._used:
            self._conditions._used[key] = False
        for area, breed, condition in self._data.keys():
            self._areas._used[area] = True
            self._breeds._used[breed] = True
            self._conditions._used[condition] = True

    def get_list_allowed_areas(self, breed: str = None, condition: str = None) -> list[str]:
        """Retrieve a list of areas used in graphics for the given breed and condition.

        Args:
            breed (str, optional): The breed to filter areas. Defaults to None.
            condition (str, optional): The condition to filter areas. Defaults to None.

        Returns:
            list[str]: A list of unique area names matching the filters.
        """
        result = []
        for area_current, breed_current, condition_current in self._data.keys():
            if (breed is None or breed == breed_current) and (condition is None or condition == condition_current):
                if area_current not in result:
                    result.append(area_current)
        return result

    def get_list_allowed_breeds(self, area: str = None, condition: str = None) -> list[str]:
        """Retrieve a list of breeds used in graphics for the given area and condition.

        Args:
            area (str, optional): The area to filter breeds. Defaults to None.
            condition (str, optional): The condition to filter breeds. Defaults to None.

        Returns:
            list: A list of unique breed names matching the filters.
        """
        result = []
        for area_current, breed_current, condition_current in self._data.keys():
            if (area is None or area == area_current) and (condition is None or condition == condition_current):
                if breed_current not in result:
                    result.append(breed_current)
        return result

    def get_list_allowed_conditions(self, area: str = None, breed: str = None) -> list[str]:
        """Retrieve a list of conditions used in graphics for the given area and breed.

        Args:
            area (str, optional): The area to filter conditions. Defaults to None.
            breed (str, optional): The breed to filter conditions. Defaults to None.

        Returns:
            list: A list of unique condition names matching the filters.
        """
        result = []
        for area_current, breed_current, condition_current in self._data.keys():
            if (area is None or area == area_current) and (breed is None or breed == breed_current):
                if condition_current not in result:
                    result.append(condition_current)
        return result
