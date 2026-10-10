import json
import math
from pathlib import Path


# ============================================================================
# MAAH LABEL RENDERER
# LABEL FORMATS
#
# Version: 1.0.0
#
# Responsibilities:
# - Load label_formats.json
# - Validate Avery format definitions
# - Read one format by code
# - Apply temporary calibration overrides
# - Calculate effective sheet geometry
# - Calculate physical slot positions
# - Calculate page allocation
#
# This module knows nothing about:
# - SVG artwork
# - JSON production data
# - mappings
# - background colors
# - bleed
# - PDF export
# ============================================================================


DEFAULT_FORMATS_PATH = (
    Path(__file__).with_name(
        "label_formats.json"
    )
)


SCHEMA_VERSION = "1.0"


# ============================================================================
# FIELDS
# ============================================================================

REQUIRED_FORMAT_FIELDS = {

    "displayName",

    "pageWidthMm",
    "pageHeightMm",

    "labelWidthMm",
    "labelHeightMm",

    "columns",
    "rows",

    "marginLeftMm",
    "marginTopMm",

    "pitchXMm",
    "pitchYMm",

    "offsetXmm",
    "offsetYmm",

    "pitchXAdjustMm",
    "pitchYAdjustMm",

    "labelsPerSheet",

    "active"

}


CALIBRATION_FIELDS = {

    "offsetXmm",
    "offsetYmm",

    "pitchXAdjustMm",
    "pitchYAdjustMm"

}


# ============================================================================
# LOAD CONFIG
# ============================================================================

def load_label_formats(
    file_path=None
):
    """
    Load and validate label_formats.json.
    """

    path = (

        Path(file_path)

        if file_path

        else DEFAULT_FORMATS_PATH

    )


    if not path.exists():

        raise FileNotFoundError(
            (
                "Label format configuration "
                f"not found: {path}"
            )
        )


    try:

        with path.open(
            "r",
            encoding="utf-8"
        ) as file:

            config = json.load(
                file
            )


    except json.JSONDecodeError as error:

        raise ValueError(
            (
                "Invalid label_formats.json.\n"
                f"Line {error.lineno}, "
                f"column {error.colno}: "
                f"{error.msg}"
            )
        ) from error


    validate_label_formats_config(
        config
    )


    return config


# ============================================================================
# VALIDATE COMPLETE CONFIG
# ============================================================================

def validate_label_formats_config(
    config
):
    """
    Validate the complete configuration structure.
    """

    if not isinstance(
        config,
        dict
    ):

        raise ValueError(
            (
                "label_formats.json root "
                "must be an object."
            )
        )


    schema_version = config.get(
        "schemaVersion"
    )


    if schema_version != SCHEMA_VERSION:

        raise ValueError(
            (
                "Unsupported label_formats.json "
                f"schemaVersion: {schema_version}"
            )
        )


    formats = config.get(
        "formats"
    )


    if not isinstance(
        formats,
        dict
    ):

        raise ValueError(
            (
                "label_formats.json must contain "
                "a 'formats' object."
            )
        )


    if not formats:

        raise ValueError(
            "No label formats are configured."
        )


    for format_code, format_data in (
        formats.items()
    ):

        validate_format_definition(
            format_code,
            format_data
        )


    return True


# ============================================================================
# VALIDATE ONE FORMAT
# ============================================================================

def validate_format_definition(
    format_code,
    format_data
):
    """
    Validate one Avery format definition.
    """

    if not isinstance(
        format_code,
        str
    ) or not format_code.strip():

        raise ValueError(
            "Format code must be a non-empty string."
        )


    if not isinstance(
        format_data,
        dict
    ):

        raise ValueError(
            (
                f"Format '{format_code}' "
                "must be an object."
            )
        )


    missing_fields = (

        REQUIRED_FORMAT_FIELDS

        -

        set(
            format_data.keys()
        )

    )


    if missing_fields:

        raise ValueError(
            (
                f"Format '{format_code}' "
                "is missing fields: "
                +
                ", ".join(
                    sorted(
                        missing_fields
                    )
                )
            )
        )


    # ------------------------------------------------------------------------
    # INTEGER FIELDS
    # ------------------------------------------------------------------------

    try:

        columns = int(
            format_data[
                "columns"
            ]
        )

        rows = int(
            format_data[
                "rows"
            ]
        )

        labels_per_sheet = int(
            format_data[
                "labelsPerSheet"
            ]
        )


    except (
        TypeError,
        ValueError
    ) as error:

        raise ValueError(
            (
                f"Format '{format_code}' "
                "contains invalid row/column values."
            )
        ) from error


    if columns <= 0:

        raise ValueError(
            (
                f"Format '{format_code}': "
                "columns must be > 0."
            )
        )


    if rows <= 0:

        raise ValueError(
            (
                f"Format '{format_code}': "
                "rows must be > 0."
            )
        )


    if labels_per_sheet <= 0:

        raise ValueError(
            (
                f"Format '{format_code}': "
                "labelsPerSheet must be > 0."
            )
        )


    if (
        columns * rows
        !=
        labels_per_sheet
    ):

        raise ValueError(
            (
                f"Format '{format_code}': "
                "columns x rows does not match "
                "labelsPerSheet."
            )
        )


    # ------------------------------------------------------------------------
    # POSITIVE PHYSICAL VALUES
    # ------------------------------------------------------------------------

    positive_fields = [

        "pageWidthMm",
        "pageHeightMm",

        "labelWidthMm",
        "labelHeightMm",

        "pitchXMm",
        "pitchYMm"

    ]


    for field in positive_fields:

        try:

            value = float(
                format_data[
                    field
                ]
            )

        except (
            TypeError,
            ValueError
        ) as error:

            raise ValueError(
                (
                    f"Format '{format_code}': "
                    f"{field} must be numeric."
                )
            ) from error


        if value <= 0:

            raise ValueError(
                (
                    f"Format '{format_code}': "
                    f"{field} must be > 0."
                )
            )


    # ------------------------------------------------------------------------
    # OTHER NUMERIC VALUES
    #
    # These may legitimately be 0 or negative.
    # ------------------------------------------------------------------------

    numeric_fields = [

        "marginLeftMm",
        "marginTopMm",

        "offsetXmm",
        "offsetYmm",

        "pitchXAdjustMm",
        "pitchYAdjustMm"

    ]


    for field in numeric_fields:

        try:

            float(
                format_data[
                    field
                ]
            )

        except (
            TypeError,
            ValueError
        ) as error:

            raise ValueError(
                (
                    f"Format '{format_code}': "
                    f"{field} must be numeric."
                )
            ) from error


    # ------------------------------------------------------------------------
    # ACTIVE
    # ------------------------------------------------------------------------

    if not isinstance(
        format_data[
            "active"
        ],
        bool
    ):

        raise ValueError(
            (
                f"Format '{format_code}': "
                "active must be true or false."
            )
        )


    return True


# ============================================================================
# LIST ACTIVE FORMATS
# ============================================================================

def list_active_formats(
    config
):
    """
    Return active formats.

    Result:

    [
        {
            "formatCode": "L7976",
            ...
        }
    ]
    """

    validate_label_formats_config(
        config
    )


    result = []


    for format_code, format_data in (
        config[
            "formats"
        ].items()
    ):

        if not format_data[
            "active"
        ]:

            continue


        item = dict(
            format_data
        )


        item[
            "formatCode"
        ] = format_code


        result.append(
            item
        )


    return result


# ============================================================================
# GET FORMAT
# ============================================================================

def get_label_format(
    config,
    format_code
):
    """
    Return one active Avery format.
    """

    validate_label_formats_config(
        config
    )


    if not isinstance(
        format_code,
        str
    ) or not format_code.strip():

        raise ValueError(
            "Format code is required."
        )


    code = format_code.strip()


    formats = config[
        "formats"
    ]


    if code not in formats:

        raise KeyError(
            f"Unknown label format: {code}"
        )


    format_data = dict(
        formats[
            code
        ]
    )


    if not format_data[
        "active"
    ]:

        raise ValueError(
            (
                "Label format is inactive: "
                f"{code}"
            )
        )


    format_data[
        "formatCode"
    ] = code


    return format_data


# ============================================================================
# APPLY CALIBRATION OVERRIDES
# ============================================================================

def apply_calibration_overrides(
    format_data,
    overrides=None
):
    """
    Apply temporary calibration overrides.

    Supported fields:

    offsetXmm
    offsetYmm
    pitchXAdjustMm
    pitchYAdjustMm

    The original format_data is NEVER modified.
    """

    result = dict(
        format_data
    )


    if overrides is None:

        return result


    if not isinstance(
        overrides,
        dict
    ):

        raise ValueError(
            (
                "Calibration overrides "
                "must be a dictionary."
            )
        )


    for field, value in overrides.items():

        if field not in CALIBRATION_FIELDS:

            raise ValueError(
                (
                    "Unsupported calibration "
                    f"override: {field}"
                )
            )


        if value is None:

            continue


        try:

            numeric_value = float(
                value
            )

        except (
            TypeError,
            ValueError
        ) as error:

            raise ValueError(
                (
                    f"Calibration override "
                    f"'{field}' must be numeric."
                )
            ) from error


        result[
            field
        ] = numeric_value


    return result


# ============================================================================
# EFFECTIVE GEOMETRY
# ============================================================================

def get_effective_geometry(
    format_data,
    overrides=None
):
    """
    Return the actual geometry used for printing.

    Effective values:

    effectiveMarginLeftMm
    effectiveMarginTopMm
    effectivePitchXMm
    effectivePitchYMm
    """

    geometry = (
        apply_calibration_overrides(
            format_data,
            overrides
        )
    )


    geometry[
        "effectiveMarginLeftMm"
    ] = (

        float(
            geometry[
                "marginLeftMm"
            ]
        )

        +

        float(
            geometry[
                "offsetXmm"
            ]
        )

    )


    geometry[
        "effectiveMarginTopMm"
    ] = (

        float(
            geometry[
                "marginTopMm"
            ]
        )

        +

        float(
            geometry[
                "offsetYmm"
            ]
        )

    )


    geometry[
        "effectivePitchXMm"
    ] = (

        float(
            geometry[
                "pitchXMm"
            ]
        )

        +

        float(
            geometry[
                "pitchXAdjustMm"
            ]
        )

    )


    geometry[
        "effectivePitchYMm"
    ] = (

        float(
            geometry[
                "pitchYMm"
            ]
        )

        +

        float(
            geometry[
                "pitchYAdjustMm"
            ]
        )

    )


    if (
        geometry[
            "effectivePitchXMm"
        ]
        <= 0
    ):

        raise ValueError(
            "Effective Pitch X must be > 0."
        )


    if (
        geometry[
            "effectivePitchYMm"
        ]
        <= 0
    ):

        raise ValueError(
            "Effective Pitch Y must be > 0."
        )


    return geometry


# ============================================================================
# SLOT ORIGIN
# ============================================================================

def get_slot_origin_mm(
    format_data,
    slot,
    overrides=None
):
    """
    Return the physical top-left origin of one Avery slot.

    Slot numbering is row-major and starts at 1.

    Example, 2 columns:

    1  2
    3  4
    5  6
    ...
    """

    geometry = get_effective_geometry(
        format_data,
        overrides
    )


    try:

        slot_number = int(
            slot
        )

    except (
        TypeError,
        ValueError
    ) as error:

        raise ValueError(
            "Slot must be an integer."
        ) from error


    labels_per_sheet = int(
        geometry[
            "labelsPerSheet"
        ]
    )


    if (
        slot_number < 1
        or
        slot_number > labels_per_sheet
    ):

        raise ValueError(
            (
                "Slot must be between 1 and "
                f"{labels_per_sheet}."
            )
        )


    columns = int(
        geometry[
            "columns"
        ]
    )


    zero_based_index = (
        slot_number - 1
    )


    row_index = (
        zero_based_index
        //
        columns
    )


    column_index = (
        zero_based_index
        %
        columns
    )


    x_mm = (

        float(
            geometry[
                "effectiveMarginLeftMm"
            ]
        )

        +

        column_index
        *
        float(
            geometry[
                "effectivePitchXMm"
            ]
        )

    )


    y_mm = (

        float(
            geometry[
                "effectiveMarginTopMm"
            ]
        )

        +

        row_index
        *
        float(
            geometry[
                "effectivePitchYMm"
            ]
        )

    )


    return {
        "slot":
            slot_number,

        "row":
            row_index + 1,

        "column":
            column_index + 1,

        "xMm":
            x_mm,

        "yMm":
            y_mm
    }


# ============================================================================
# BUILD PAGE SLOT PLAN
# ============================================================================

def build_page_slot_plan(
    format_data,
    quantity,
    start_position=1
):
    """
    Allocate labels across physical sheets.

    Example:

    labelsPerSheet = 8
    quantity = 10
    start_position = 7

    returns:

    [
        [7, 8],
        [1, 2, 3, 4, 5, 6, 7, 8]
    ]
    """

    try:

        quantity_value = int(
            quantity
        )

        start_value = int(
            start_position
        )

    except (
        TypeError,
        ValueError
    ) as error:

        raise ValueError(
            (
                "Quantity and start position "
                "must be integers."
            )
        ) from error


    if quantity_value <= 0:

        raise ValueError(
            "Quantity must be > 0."
        )


    labels_per_sheet = int(
        format_data[
            "labelsPerSheet"
        ]
    )


    if (
        start_value < 1
        or
        start_value > labels_per_sheet
    ):

        raise ValueError(
            (
                "Start position must be between "
                f"1 and {labels_per_sheet}."
            )
        )


    pages = []

    remaining = quantity_value

    current_start = start_value


    while remaining > 0:

        available_slots = list(
            range(
                current_start,
                labels_per_sheet + 1
            )
        )


        amount_this_page = min(
            remaining,
            len(
                available_slots
            )
        )


        page_slots = (
            available_slots[
                :amount_this_page
            ]
        )


        pages.append(
            page_slots
        )


        remaining -= (
            amount_this_page
        )


        # Every page after the first begins at slot 1.
        current_start = 1


    return pages


# ============================================================================
# PAGE COUNT
# ============================================================================

def calculate_page_count(
    format_data,
    quantity,
    start_position=1
):
    """
    Return only the number of required physical sheets.
    """

    pages = build_page_slot_plan(
        format_data,
        quantity,
        start_position
    )


    return len(
        pages
    )