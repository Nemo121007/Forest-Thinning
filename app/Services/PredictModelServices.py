"""Module for managing prediction models in a reference data system.

This module provides the PredictModelService class, which handles initialization, training,
and querying of prediction models for graphics data associated with areas, breeds, and conditions.
"""

from .ReferenceDataManagerService import ReferenceDataManagerServices
from ..background_information.Type_line import Type_line


class PredictModelService:
    """A service class for managing prediction models for graphics data.

    Provides methods to initialize, train, save, load, and query prediction models based on
    area, breed, and condition data. Integrates with ReferenceDataManager for accessing
    graphics, areas, breeds, and conditions, and supports plotting predictions for various
    line types (e.g., growth, logging).

    Attributes:
        manager_reference_data (ReferenceDataManager): The reference data manager instance.
        manager_areas (object): The areas entity from ReferenceDataManager.
        manager_breeds (object): The breeds entity from ReferenceDataManager.
        manager_conditions (object): The conditions entity from ReferenceDataManager.
        manager_graphics (object): The graphics entity from ReferenceDataManager.
        predict_model (object): The prediction model instance from ReferenceDataManagerServices.
        area (str): The current area name for the model.
        breed (str): The current breed name for the model.
        condition (str): The current condition name for the model.
        name (str): The name of the graphic (file name) for the model.
        age_thinning (float): The age of thinning for the breed.
        age_thinning_save (float): The age of thinning for protective forests.
        flag_save_forest (bool): Flag indicating protective forest mode.
    """

    def __init__(self) -> None:
        """Initialize the PredictModelService.

        Sets up connections to ReferenceDataManager entities (areas, breeds, conditions,
        graphics) and the prediction model instance.

        Returns:
            None
        """
        self.manager_reference_data = ReferenceDataManagerServices().manager
        self.manager_areas = self.manager_reference_data.get_areas()
        self.manager_breeds = self.manager_reference_data.get_breeds()
        self.manager_conditions = self.manager_reference_data.get_conditions()
        self.manager_graphics = self.manager_reference_data.get_graphics()

        self.predict_model = ReferenceDataManagerServices().predict_model
        self.area: str = None
        self.breed: str = None
        self.condition: str = None

        self.name: str = None
        self.age_thinning: float = None
        self.age_thinning_save: float = None
        self.flag_save_forest: bool = False

    def initialize_predict_model(
        self, area: str, breed: str, condition: str, flag_save_forest: bool = False, flag_prepare_model: bool = False
    ) -> None:
        """Initialize the prediction model with specified parameters.

        Sets up the model with the given area, breed, condition, and forest mode, retrieves
        related codes and thinning ages, and optionally prepares the model.

        Args:
            area (str): The name of the area.
            breed (str): The name of the breed.
            condition (str): The name of the condition.
            flag_save_forest (bool, optional): Indicates protective forest mode. Defaults to False.
            flag_prepare_model (bool, optional): If True, prepares the model after initialization. Defaults to False.

        Returns:
            None
        """
        self.area = area
        self.breed = breed
        self.condition = condition

        self.name: str = self.manager_graphics.get_value_graphic(
            name_area=area, name_breed=breed, name_condition=condition
        )
        code_area: str = self.manager_areas.get_value(name=area)
        code_breed: str = self.manager_breeds.get_value(name=breed)
        code_condition: str = self.manager_conditions.get_value(name=condition)
        self.age_thinning: float = self.manager_breeds.get_age_thinning(name=breed)
        self.age_thinning_save: float = self.manager_breeds.get_age_thinning_save(name=breed)
        self.flag_save_forest: bool = flag_save_forest

        self.predict_model.initialize_model(
            name=self.name,
            area=area,
            breed=breed,
            condition=condition,
            age_thinning=self.age_thinning,
            age_thinning_save=self.age_thinning_save,
            flag_save_forest=flag_save_forest,
        )
        self.predict_model.load_reference_info(
            code_area=code_area, code_breed=code_breed, code_condition=code_condition
        )
        if flag_prepare_model:
            self.prepare_model()

    def prepare_model(self) -> None:
        """Prepare the prediction model by loading data and fitting models.

        Loads data from a tar file, fits the models, and clears training data to optimize memory.

        Returns:
            None

        Raises:
            Exception: If an error occurs during data loading, model fitting, or data clearing.
        """
        self.load_data()
        self.fit_models()
        self.clear_train_data()

    def load_data(self) -> None:
        """Load graphics data from a tar file for model training.

        Retrieves data from the tar file associated with the current graphic.

        Returns:
            None

        Raises:
            Exception: If an error occurs while loading data from the tar file.
        """
        try:
            self.predict_model.load_graph_from_tar()
        except Exception as e:
            raise Exception(f"Error load data from tar: {str(e)}")

    def fit_models(self) -> None:
        """Fit the prediction models using loaded data.

        Trains the models based on the current graphic’s data.

        Returns:
            None

        Raises:
            Exception: If an error occurs while fitting the models.
        """
        try:
            self.predict_model.fit_models()
        except Exception as e:
            raise Exception(f"Error fir models: {str(e)}")

    def clear_train_data(self) -> None:
        """Clear training data to free memory.

        Removes temporary training data after model fitting.

        Returns:
            None

        Raises:
            Exception: If an error occurs while clearing training data.
        """
        try:
            self.predict_model.clear_train_data()
        except Exception as e:
            raise Exception(f"Error clear train data: {str(e)}")

    def save_model(self) -> None:
        """Save the trained prediction model.

        Persists the model to storage for later use.

        Returns:
            None

        Raises:
            Exception: If an error occurs while saving the model.
        """
        try:
            self.predict_model.save_graph()
        except Exception as e:
            raise Exception(f"Error save model: {str(e)}")

    # TODO:  Проверить валидацию прочитанных данных из файла и инициализированных
    def load_model(self) -> None:
        """Load a previously saved prediction model.

        Retrieves the model associated with the current graphic from storage.

        Returns:
            None

        Raises:
            Exception: If an error occurs while loading the model.
        """
        try:
            self.predict_model.load_graph()
        except Exception as e:
            raise Exception(f"Error load model: {str(e)}")

    def get_min_max_value(self) -> tuple[float, float, float, float]:
        """Retrieve the minimum and maximum values for plotting.

        Returns the x and y range limits for the current model’s predictions.

        Returns:
            tuple[float, float, float, float]: A tuple of (x_min, x_max, y_min, y_max).

        Raises:
            Exception: If an error occurs while retrieving min/max values.
        """
        try:
            result = self.predict_model.get_min_max_value()
            return result
        except Exception as e:
            raise Exception(f"Error get min max value: {str(e)}")

    def get_predict_value(self, type_line: Type_line, x: float, start_parameter: float = 0) -> float:
        """Predict a single value for a specified line type at a given x.

        Validates that start_parameter is zero for growth or recovery lines and computes
        the prediction.

        Args:
            type_line (Type_line): The type of line to predict (e.g., growth, logging).
            x (float): The x-value for the prediction.
            start_parameter (float, optional): Starting parameter for the prediction,
            must be 0 for growth/recovery lines. Defaults to 0.

        Returns:
            float: The predicted y-value.

        Raises:
            ValueError: If start_parameter is non-zero for growth or recovery lines.
            Exception: If an error occurs while computing the prediction.
        """
        if (type_line == Type_line.GROWTH_LINE or type_line == Type_line.RECOVERY_LINE) and start_parameter != 0:
            test_error = f"Value {start_parameter} of starting parameter is unacceptable for {type_line} type of line."
            raise ValueError(test_error)
        try:
            result = self.predict_model.predict_value(type_line=type_line, X=x, start_parameter=start_parameter)
            return result
        except Exception as e:
            raise Exception(f"Error get predict value: {str(e)}")

    def get_predict_list(self, type_line: Type_line, x_list: list[float], start_parameter: float = 0) -> list[float]:
        """Predict a list of values for a specified line type over a list of x-values.

        Validates that start_parameter is zero for growth or recovery lines and computes
        predictions for each x-value.

        Args:
            type_line (Type_line): The type of line to predict (e.g., growth, logging).
            x_list (list[float]): The list of x-values for predictions.
            start_parameter (float, optional): Starting parameter, must be 0 for growth/recovery lines. Defaults to 0.

        Returns:
            list[float]: A list of predicted y-values.

        Raises:
            ValueError: If start_parameter is non-zero for growth or recovery lines.
            Exception: If an error occurs while computing predictions.
        """
        if (type_line == Type_line.GROWTH_LINE or type_line == Type_line.RECOVERY_LINE) and start_parameter != 0:
            test_error = f"Value {start_parameter} of starting parameter is unacceptable for {type_line} type of line."
            raise ValueError(test_error)
        try:
            result = self.predict_model.predict_list_value(
                type_line=type_line, X=x_list, start_parameter=start_parameter
            )
            return result
        except Exception as e:
            raise Exception(f"Error get predict value: {str(e)}")

    def get_predict_line(
        self,
        type_line: Type_line,
        start_x: float = None,
        end_x: float = None,
        step: float = None,
        start_parameter: float = 0,
    ) -> list[float]:
        """Generate a list of predicted values for a line type over a range of x-values.

        Validates that start_parameter is zero for growth or recovery lines and computes
        predictions for the specified x-range with the given step size.

        Args:
            type_line (Type_line): The type of line to predict (e.g., growth, logging).
            start_x (float, optional): The starting x-value for the range. Defaults to None.
            end_x (float, optional): The ending x-value for the range. Defaults to None.
            step (float, optional): The step size between x-values. Defaults to None.
            start_parameter (float, optional): Starting parameter, must be 0 for growth/recovery lines. Defaults to 0.

        Returns:
            list[float]: A list of predicted y-values for the specified range.

        Raises:
            ValueError: If start_parameter is non-zero for growth or recovery lines.
            Exception: If an error occurs while generating the prediction line.
        """
        if (type_line == Type_line.GROWTH_LINE or type_line == Type_line.RECOVERY_LINE) and start_parameter != 0:
            test_error = f"Value {start_parameter} of starting parameter is unacceptable for {type_line} type of line."
            raise ValueError(test_error)
        try:
            result = self.predict_model.predict_line(
                type_line=type_line, start_x=start_x, end_x=end_x, step=step, start_parameter=start_parameter
            )
            return result
        except Exception as e:
            raise Exception(f"Error get predict line: {str(e)}")
