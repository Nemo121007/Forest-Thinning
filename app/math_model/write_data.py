"""write_data.py.

Description:
    File contains function rewrite data in archive  .tar in temp file tmp_data_d+
"""

import json
import re
import tarfile
import pandas as pd
from pathlib import Path


def main_all_line():
    """Write data on data all lines in graphics in tmp_data_all_line.json.

    Args:
        None
    Returns:
        None
    """
    # Путь к архиву
    tar_path = Path(__file__).parent
    tar_path = tar_path.parent.parent / "data_line" / "pine_sorrel.tar"

    # tar_path = "../../data_line/pine_sorrel.tar"

    # Распаковка архива и чтение файлов
    with tarfile.open(tar_path, "r") as tar_ref:
        # Открыть файл из архива на чтение
        file_member = tar_ref.getmember("pine_sorrel/wpd.json")

        with tar_ref.extractfile(file_member) as file:
            data = json.load(file)

            data = data["datasetColl"]

            # Создаем пустой словарь для хранения DataFrame
            dataframes_dict = {}

            for i in range(len(data)):
                line = data[i]
                b = []

                # Извлечение данных для текущей линии
                for item in line["data"]:
                    b.append(item["value"])

                # Создаем DataFrame для текущей линии
                df = pd.DataFrame(b, columns=["x", "y"])

                # Сохраняем DataFrame в словарь с ключом - названием линии
                if re.match(r"growth line \d+", data[i]["name"]):
                    dataframes_dict[line["name"]] = {
                        "name": line["name"],
                        "data": df.to_dict(orient="list"),
                        "start_point": df["y"][0],
                    }
                elif re.match(r"recovery line \d+", data[i]["name"]):
                    dataframes_dict[line["name"]] = {
                        "name": line["name"],
                        "data": df.to_dict(orient="list"),
                        "start_point": df["x"][0],
                    }
                else:
                    dataframes_dict[line["name"]] = {
                        "name": line["name"],
                        "data": df.to_dict(orient="list"),
                        "start_point": 0,
                    }

            tar_path = Path(__file__).parent
            tar_path = tar_path.parent.parent / "data_line" / "tmp_data_all_line.json"
            with open(tar_path, "w") as f:
                json.dump(dataframes_dict, f)

            print("Data successfully saved to tmp_data_all_line.json.")


if __name__ == "__main__":
    main_all_line()
