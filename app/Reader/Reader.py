"""Module Reader."""

import json
import os.path
from pathlib import Path
import tarfile
import re


class Reader:
    """Static class Reader.

    Class provides methods for reading data for building graphics polynomials,
    as well as generating and caching this data at './' address when first accessed:
    - Generates data for building polynomials on which graphics are built
    - Saves and reads them from a collection located in

    Attributes:
        _dict_data_graphics: dict: dictionary with data for graphics
        _file_path_cache: str: path to the cache file
        _dir_path_data: str: path to the data directory
        _list_name_graphics: list: list of graphic names
        _list_unique_name_group_line: list: list of unique line names
    """

    _dict_data_graphics = None
    _file_path_cache = "../../cache_data_graphics.json"
    _dir_path_data = "../../data_line"
    _list_name_graphics = []
    _list_unique_name_group_line = [
        "min level logging",
        "max level logging",
        "economic max line",
        "economic min line",
        "growth line",
        "recovery",
    ]

    @staticmethod
    def _initialize_graphics_data():
        try:
            if Reader._dict_data_graphics is None:
                if os.path.isfile(Reader._file_path_cache):
                    print("Cache file detected")
                    with open(Reader._file_path_cache) as f:
                        Reader._dict_data_graphics = json.load(f)
                        if not isinstance(Reader._dict_data_graphics, dict):
                            raise ValueError("Cached data is not a dictionary")
                    print("Cache file was read")

            set_files_in_disk = os.listdir(Reader._dir_path_data)
            set_files_in_disk = [
                re.match(r"^([a-zA-Z_]+)\.tar$", name).group(1)
                for name in set_files_in_disk
                if re.match(r"^([a-zA-Z_]+)\.tar$", name)
            ]
            set_files_in_disk = set(set_files_in_disk)

            set_name_graphics_in_cache = set(Reader._dict_data_graphics.keys())

            if not (set_files_in_disk == set_name_graphics_in_cache):
                print("Synchronization data in cache and disk")
                different = set_files_in_disk - set_name_graphics_in_cache
                for name_in_disk in different:
                    name, data = Reader._generate_data_graphics(name_in_disk)
                    Reader._dict_data_graphics[name] = data

                different = set_name_graphics_in_cache - set_files_in_disk
                for name_in_cache in different:
                    Reader._dict_data_graphics.pop(name_in_cache)

                print("Rewrite cache")
                with open(Reader._file_path_cache, "w") as f:
                    json.dump(Reader._dict_data_graphics, f)

        except Exception as e:
            raise RuntimeError(f"Error in _initialize_graphics_data(): {e}") from e

    @staticmethod
    def _generate_data_graphics(name_file_in_disk: str) -> tuple:
        tar_path = f"../../data_line/{name_file_in_disk}.tar"
        with tarfile.open(tar_path, "r") as tar_ref:
            # Открыть файл из архива на чтение
            file_member = tar_ref.getmember(f"{name_file_in_disk}/wpd.json")

            with tar_ref.extractfile(file_member) as file:
                data = json.load(file)
                data = data["datasetColl"]

                # Создаем пустой словарь для хранения DataFrame
                for unique_name_line in Reader._list_unique_name_group_line:
                    X = []
                    Y = []
                    for line in data:
                        if unique_name_line in line["name"]:
                            data_line = line["data"]
                            # Извлечение данных для текущей линии
                            for item in data_line:
                                X.append(item["value"][0])
                                Y.append(item["value"][1])

        return {"a": "a"}

    @staticmethod
    def read_text_file(file_path: Path) -> dict:
        """Reads the contents of a text file.

        :param file_path: Path: path to the file
        :return: dict: file content
        """
        with open(file_path, encoding="utf-8") as file:
            return file.read()

    @staticmethod
    def test() -> None:
        """Test method.

        :return: None
        """
        Reader._initialize_graphics_data()


if __name__ == "__main__":
    Reader.test()
