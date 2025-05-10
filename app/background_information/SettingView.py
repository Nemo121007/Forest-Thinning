"""Module for storing UI style settings in forest growth simulation applications.

This module defines the SettingsView dataclass, which encapsulates style configurations
for the graphical user interface, including colors, borders, and styles for widgets,
buttons, and other UI elements.

Dependencies:
    - dataclasses: Standard library module for defining the SettingsView dataclass.
"""

from dataclasses import dataclass


@dataclass
class SettingsView:
    """Dataclass for storing UI style settings in forest growth simulation applications.

    Encapsulates configuration for colors, borders, and styles used in the graphical user
    interface, including backgrounds, buttons, checkboxes, and graph elements. All attributes
    are defined with default values for consistent styling across the application.

    Attributes:
        main_background_filling_color (str): Primary background color in HEX format (e.g., '#D5E8D4').
        background_color (str): CSS style for widget background using main_background_filling_color.
        background_color_button (str): CSS style for button background color (e.g., '#A3D2A3').
        info_block (str): CSS style for info block widget, including background, border, and radius.
        item_block (str): CSS style for item block background color (e.g., '#AADEC0').
        checkbox_style (str): CSS style for QCheckBox, defining indicator appearance and checked state.
        main_line_color (str): Color for main graph lines in HEX format (e.g., '#0000FF' for blue).
        fill_color_graph (tuple[int, int, int, int]): RGBA tuple for graph fill color (e.g., (0, 0, 0, 30)).
        line_age_thinning (tuple[int, int, int, int]): RGBA tuple for thinning age line (e.g., (0, 0, 0, 255)).
        line_bearing_color (tuple[int, int, int, int]): RGBA tuple for bearing line (e.g., (0, 255, 0, 255) for green).
        background_list_item_white (str): CSS style for list item background (light, e.g., '#B4C3B3').
        background_list_item_gray (str): CSS style for list item background (gray, e.g., '#D3D3D3').
        back_button_color (str): CSS style for back button background (e.g., '#F8CECC').
        edit_form (str): CSS style for edit form, including background, border, and padding.
        true_border (str): CSS style for valid input field borders (gray, rounded).
        error_border (str): CSS style for invalid input field borders (red, rounded).
        cancel_button (str): CSS style for cancel button, using an icon and no border.
        edit_button (str): CSS style for edit button, using an icon and no border.
    """

    main_background_filling_color: str = "#D5E8D4"
    background_color: str = f"background-color: {main_background_filling_color}"
    background_color_button: str = "background-color: #A3D2A3"
    info_block = """
    QWidget#info_block {
        background-color: #D5E8D4;
        border: 1px solid #82B366;
        border-radius: 5px;
    }
    """
    item_block: str = "background-color: #AADEC0"
    checkbox_style = """
        QCheckBox::indicator {
            width: 15px;
            height: 15px;
            background-color: #D5E8D4;
            border: 1px solid black;
        }
        QCheckBox::indicator:checked {
            background-color: #D5E8D4;
        }
    """
    main_line_color = "#0000FF"
    fill_color_graph = (0, 0, 0, 30)
    line_age_thinning = (0, 0, 0, 255)
    line_bearing_color = (0, 200, 0, 255)
    background_list_item_white = "background-color: #B4C3B3"
    background_list_item_gray = "background-color: #D3D3D3;"
    back_button_color = "background-color: #F8CECC;"
    edit_form = "background-color: #D5E8D4; border: 1px solid gray; border-radius: 5px; padding: 2px;"
    true_border = "border: gray; border-radius: 5px; padding: 2px;"
    error_border = "border: 1px solid red; border-radius: 5px; padding: 2px;"

    cancel_button: str = """
        QPushButton {
            border: none;
            border-radius: 3px;
            image: url("image/cancel_icon.png");
        }
    """

    edit_button: str = """
        QPushButton {
            border: none;
            border-radius: 3px;
            image: url("image/edit_icon.png");
        }
    """
