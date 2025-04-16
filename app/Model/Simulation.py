"""Module for forest growth simulation and thinning operations.

This module provides the Simulation class that enables:
- Forest growth modeling based on different growth curves
- Automatic thinning point determination
- Visualization of simulation results
- Management of forest stand parameters

The module implements mathematical models for:
- Standard forest growth
- Recovery after thinning
- Economic minimum thresholds
- Logging level boundaries
"""

import numpy as np

from .Graph import Graph
from ..background_information.TypeLine import Type_line


class Simulation:
    """A class for modeling forest growth and thinning operations.

    This class provides functionality for:
    - Initializing simulation parameters
    - Calculating forest growth curves
    - Determining thinning points
    - Visualizing simulation results

    Attributes:
        name_simulation (str): Name identifier for the simulation
        forest_area (str): Forest area identifier
        main_breed (str): Main tree species identifier
        type_conditions (str): Growing conditions type
        save_forest (bool): Flag for saving simulation results
        age (int): Stand age
        start_value (float): Initial wood stock value
        preprocessing_value (dict): Pre-calculated curve values for simulation
        thinning_forest (dict): Information about thinning points
        path_modeling (list): Simulation path points
        graph (Graph): Container for growth curves

    Methods:
        set_params_simulation: Sets simulation parameters
        initialize_step_simulation: Initializes simulation step and calculates curves
        auto_generate_simulation: Automatically generates simulation with thinning points
        visualize_simulation: Visualizes simulation results
    """

    def __init__(self):
        """Initialize a new Simulation instance.

        This class manages forest growth simulation including:
        - Parameter initialization
        - Growth curve calculations
        - Thinning point determination
        - Visualization of results

        Attributes:
            name_simulation (str): Name of the simulation
            forest_area (str): Forest area identifier
            main_breed (str): Main tree species
            type_conditions (str): Growing conditions type
            save_forest (bool): Flag for saving results
            age (int): Stand age
            start_value (float): Initial wood stock
            preprocessing_value (list): Pre-calculated curve values
            thinning_forest (dict): Thinning points information
            path_modeling (list): Simulation path points
            graph (Graph): Growth curves container
        """
        pass

    def set_params_simulation(
        self,
        name_simulation: str,
        forest_area: str = None,
        main_breed: str = None,
        type_conditions: str = None,
        save_forest: bool = False,
        age: int = None,
        start_value: int = None,
    ):
        """Set simulation parameters for forest growth modeling.

        This method initializes core parameters for forest growth simulation,
        including stand characteristics and initial conditions. When all required
        parameters (forest_area, main_breed, type_conditions) are provided,
        it also loads the corresponding growth graph.

        Args:
            name_simulation (str): Simulation name identifier
            forest_area (str, optional): Forest area identifier. Defaults to None
            main_breed (str, optional): Main tree species. Defaults to None
            type_conditions (str, optional): Growing conditions type. Defaults to None
            save_forest (bool, optional): Flag for saving results. Defaults to False
            age (int, optional): Stand age. Defaults to None
            start_value (int, optional): Initial wood stock. Defaults to None
        Modifies:
            self.name_simulation: Sets simulation name
            self.forest_area: Sets forest area ID
            self.main_breed: Sets main species
            self.type_conditions: Sets conditions type
            self.save_forest: Sets saving flag
            self.age: Sets stand age
            self.start_value: Sets initial stock
            self.preprocessing_value: Initializes list for precalculations
            self.thinning_forest: Initializes dictionary for thinning points
            self.path_modeling: Initializes list for modeling path
            self.graph: Creates and loads growth graph if all required parameters present
        """
        self.name_simulation = name_simulation
        self.forest_area = forest_area
        self.main_breed = main_breed
        self.type_conditions = type_conditions
        self.save_forest = save_forest
        self.age = age
        self.start_value = start_value
        self.preprocessing_value = []
        self.thinning_forest = {}
        self.path_modeling = []

        if self.forest_area is not None and self.main_breed is not None and self.type_conditions is not None:
            self.full_file_name_resources = self.forest_area + self.main_breed + self.type_conditions
            # TODO: real name
            self.graph = Graph(name="pine_sorrel")
            self.graph.load_graph()

    def initialize_step_simulation(
        self,
        step: int,
        start_x: int = None,
        end_x: int = None,
    ):
        """Initialize simulation parameters and pre-calculate key values for forest growth modeling.

        This method prepares arrays of values for different forest growth curves used in simulation:
        - Standard growth line
        - Minimum/maximum logging levels
        - Economic minimum line
        All curves are adjusted to stay within allowed logging boundaries.

        Args:
            step: Integer value determining the simulation time step size
            start_x: Optional integer specifying simulation start age. If None, uses graph's minimum x value
            end_x: Optional integer specifying simulation end age. If None, uses graph's maximum x value

        Returns:
            None

        Modifies:
            self.preprocessing_value: Dictionary containing pre-calculated arrays:
                - array_x: Age values array
                - max_logging: Maximum logging level curve
                - min_logging: Minimum logging level curve
                - min_economic: Economic minimum curve
                - standard: Standard growth curve

        Raises:
            ValueError: If x_min or x_max values are None
        """
        if start_x is not None:
            x_min = start_x
        else:
            x_min = int(self.graph.x_min)
        if x_min is None:
            raise ValueError("x_min is None")

        if end_x is not None:
            x_max = end_x
        else:
            x_max = int(self.graph.x_max)
        if x_max is None:
            raise ValueError("x_max is None")

        array_x = np.arange(x_min, x_max, step)
        array_min_logging = np.array([self.graph.predict(type_line=Type_line.MIN_LEVEL_LOGGING, X=x) for x in array_x])
        array_max_logging = np.array([self.graph.predict(type_line=Type_line.MAX_LEVEL_LOGGING, X=x) for x in array_x])
        array_min_economic = np.minimum(
            np.array([self.graph.predict(type_line=Type_line.ECONOMIC_MIN_LINE, X=x) for x in array_x]),
            array_max_logging,
        )
        array_min_economic = np.maximum(array_min_economic, array_min_logging)
        array_standard = np.minimum(
            np.array(
                [
                    self.graph.predict(type_line=Type_line.GROWTH_LINE, X=x, start_parameter=self.start_value)
                    for x in array_x
                ]
            ),
            array_max_logging,
        )
        array_standard = np.maximum(array_standard, array_min_logging)

        self.preprocessing_value = {
            "max_logging": array_max_logging,
            "min_economic": array_min_economic,
            "min_logging": array_min_logging,
            "standard": array_standard,
            "array_x": array_x,
        }

        pass

    # def auto_generate_simulation(self):
    # current_x = self.start_value
    # current_value = self.start_value
    # new_value = None
    # start_value = self.start_value
    # flag_thinning = False
    # step = self.array_x[1] - self.array_x[0]
    # while current_x < self.end_x:
    #     if current_value > self.graph.predict(type_line=Type_line.ECONOMIC_MIN_LINE,
    #                                           X= current_x):
    #         flag_thinning = True
    #         new_value = self.graph.predict(type_line=Type_line.MIN_LEVEL_LOGGING,
    #                                        X= current_x)
    #         self.thinning_forest[current_x] = {
    #             "past_value": current_value,
    #             "new_value": new_value,
    #         }
    #         start_value = current_x
    #     elif not flag_thinning:
    #         current_value = self.graph.predict(type_line=Type_line.GROWTH_LINE,
    #                                            X= current_x,
    #                                            start_parameter= start_value)
    #     else:
    #         current_value = self.graph.predict(type_line=Type_line.RECOVERY_LINE,
    #                                            X= current_x,
    #                                            start_parameter= start_value)
    #     current_x += step
    #     self.path_modeling.append({
    #         "x": current_x,
    #         "value": current_value
    #     })
    #     pass

    def auto_generate_simulation(self):
        """Automatically generates forest growth simulation with thinning points.

        This method simulates forest growth based on predefined parameters and conditions.
        It tracks the forest's development path and determines optimal thinning points
        when the forest reaches economic maturity.

        The simulation follows these rules:
        1. If no thinning has occurred, follows standard growth path
        2. After thinning, follows recovery growth path
        3. Enforces minimum logging levels
        4. Records thinning points when economic conditions are met

        Args:
            None

        Returns:
            None

        Modifies:
            self.path_modeling: List of dictionaries containing simulation path points
            self.thinning_forest: Dictionary containing thinning points information
        """
        start_index = self.start_value
        current_value = self.start_value
        flag_thinning = False
        for current_index in range(len(self.preprocessing_value["array_x"])):
            if not flag_thinning:
                current_value = self.preprocessing_value["standard"][current_index]
            else:
                current_value = self.graph.predict(
                    type_line=Type_line.RECOVERY_LINE,
                    X=self.preprocessing_value["array_x"][current_index],
                    start_parameter=start_index,
                )
                if current_value < self.preprocessing_value["min_logging"][current_index]:
                    current_value = self.preprocessing_value["min_logging"][current_index]
            # if new_current_value is not None:
            #     current_value = new_current_value

            self.path_modeling.append({"x": self.preprocessing_value["array_x"][current_index], "value": current_value})

            if (
                current_value >= self.preprocessing_value["standard"][current_index]
                and current_value >= self.preprocessing_value["min_economic"][current_index]
            ):
                flag_thinning = True
                start_index = self.preprocessing_value["array_x"][current_index]
                self.thinning_forest[self.preprocessing_value["array_x"][current_index]] = {
                    "x": self.preprocessing_value["array_x"][current_index],
                    "past_value": current_value,
                    "new_value": self.preprocessing_value["min_logging"][current_index],
                }
                current_value = self.preprocessing_value["min_logging"][current_index]
                self.path_modeling.append(
                    {"x": self.preprocessing_value["array_x"][current_index], "value": current_value}
                )
        self.path_modeling.append({"x": self.preprocessing_value["array_x"][current_index], "value": current_value})

        pass

    def visualize_simulation(self):
        """Визуализация результатов симуляции."""
        import matplotlib.pyplot as plt

        # Построение линий из preprocessing_value
        plt.plot(
            self.preprocessing_value["array_x"],
            self.preprocessing_value["max_logging"],
            "r--",
            label="Максимальный уровень вырубки",
        )

        plt.plot(
            self.preprocessing_value["array_x"],
            self.preprocessing_value["min_logging"],
            "g--",
            label="Минимальный уровень вырубки",
        )

        plt.plot(
            self.preprocessing_value["array_x"],
            self.preprocessing_value["min_economic"],
            "b--",
            label="Экономический минимум",
        )

        plt.plot(
            self.preprocessing_value["array_x"], self.preprocessing_value["standard"], "y--", label="Стандартный рост"
        )

        # Построение пути моделирования
        x_values = [point["x"] for point in self.path_modeling]
        y_values = [point["value"] for point in self.path_modeling]
        plt.plot(x_values, y_values, "k-", label="Путь моделирования", linewidth=2)

        # Отметка точек вырубки
        for x, data in self.thinning_forest.items():
            plt.plot([x, x], [data["past_value"], data["new_value"]], "r-", linewidth=2)
            plt.plot(x, data["past_value"], "ro")
            plt.plot(x, data["new_value"], "ro")

        plt.xlabel("Возраст")
        plt.ylabel("Запас древесины")
        plt.title("Моделирование роста леса")
        plt.legend()
        plt.grid(True)
        plt.show()


if __name__ == "__main__":
    a = Simulation()
    a.set_params_simulation(
        name_simulation="test",
        forest_area="test",
        main_breed="test",
        type_conditions="test",
        save_forest=False,
        age=10,
        start_value=19,
    )
    a.initialize_step_simulation(step=0.5)
    a.auto_generate_simulation()
    a.visualize_simulation()
