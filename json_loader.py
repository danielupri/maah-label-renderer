import json
from pathlib import Path


# ============================================================================
# MAAH LABEL RENDERER
# JSON LOADER
#
# Version: 1.0.0
#
# Responsibilities:
# - Load a MAAH SYSTEM JSON file
# - Detect scalar JSON fields
# - Read values using dot notation
#
# This module knows nothing about:
# - SVG
# - mappings
# - Avery formats
# - printing
# ============================================================================


# ============================================================================
# LOAD JSON
# ============================================================================

def load_json(file_path):
    """
    Load a JSON file and return the root dictionary.
    """

    path = Path(file_path)


    if not path.exists():

        raise FileNotFoundError(
            f"JSON file not found: {path}"
        )


    if path.suffix.lower() != ".json":

        raise ValueError(
            "Selected file is not a JSON file."
        )


    try:

        with path.open(
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(
                file
            )


    except json.JSONDecodeError as error:

        raise ValueError(
            (
                "Invalid JSON file.\n"
                f"Line {error.lineno}, "
                f"column {error.colno}: "
                f"{error.msg}"
            )
        ) from error


    if not isinstance(
        data,
        dict
    ):

        raise ValueError(
            "JSON root must be an object."
        )


    return data


# ============================================================================
# GET JSON PATHS
# ============================================================================

def get_json_paths(
    data,
    parent_path=""
):
    """
    Return all scalar fields using dot notation.

    Example:

    {
        "product": {
            "labelName": "Chicken Curry",
            "netWeightG": 500
        }
    }

    becomes:

    product.labelName
    product.netWeightG

    Lists are intentionally excluded from V1 mappings.
    """

    if not isinstance(
        data,
        dict
    ):

        raise ValueError(
            "get_json_paths expects a dictionary."
        )


    paths = []


    for key, value in data.items():

        current_path = (

            f"{parent_path}.{key}"

            if parent_path

            else key

        )


        if isinstance(
            value,
            dict
        ):

            paths.extend(
                get_json_paths(
                    value,
                    current_path
                )
            )


        elif isinstance(
            value,
            list
        ):

            # Lists are not directly mappable in V1.
            continue


        else:

            paths.append(
                current_path
            )


    return paths


# ============================================================================
# GET VALUE BY PATH
# ============================================================================

def get_value_by_path(
    data,
    path
):
    """
    Retrieve a value using dot notation.

    Example:

    get_value_by_path(
        data,
        "product.labelName"
    )
    """

    if not isinstance(
        data,
        dict
    ):

        raise ValueError(
            "JSON data must be a dictionary."
        )


    if not isinstance(
        path,
        str
    ) or not path.strip():

        raise ValueError(
            "JSON path must be a non-empty string."
        )


    current = data


    for part in path.split("."):

        if not isinstance(
            current,
            dict
        ):

            raise KeyError(
                f"Invalid JSON path: {path}"
            )


        if part not in current:

            raise KeyError(
                f"JSON field not found: {path}"
            )


        current = current[
            part
        ]


    return current