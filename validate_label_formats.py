import json
import sys
from pathlib import Path

from label_formats import load_label_formats


# ============================================================================
# PATHS
# ============================================================================

BASE_DIR = Path(__file__).resolve().parent

LABEL_FORMATS_PATH = (
    BASE_DIR
    /
    "label_formats.json"
)


# ============================================================================
# CONFIGURATION
# ============================================================================

REQUIRED_FIELDS = {
    "displayName": str,

    "pageWidthMm": (int, float),
    "pageHeightMm": (int, float),

    "labelWidthMm": (int, float),
    "labelHeightMm": (int, float),

    "columns": int,
    "rows": int,

    "marginLeftMm": (int, float),
    "marginTopMm": (int, float),

    "pitchXMm": (int, float),
    "pitchYMm": (int, float),

    "offsetXmm": (int, float),
    "offsetYmm": (int, float),

    "pitchXAdjustMm": (int, float),
    "pitchYAdjustMm": (int, float),

    "labelsPerSheet": int,

    "active": bool
}


# ============================================================================
# HELPERS
# ============================================================================

def load_raw_json():
    """
    Load label_formats.json as raw JSON.

    This allows the validator to perform additional structural
    and physical geometry checks independently from the application loader.
    """

    if not LABEL_FORMATS_PATH.exists():

        raise FileNotFoundError(
            f"File not found: {LABEL_FORMATS_PATH}"
        )


    with LABEL_FORMATS_PATH.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(
            file
        )


def validate_positive(
    format_code,
    field_name,
    value,
    errors
):
    """
    Require a numeric value to be greater than zero.
    """

    if value <= 0:

        errors.append(
            (
                f"{format_code}: "
                f"{field_name} must be greater than 0."
            )
        )


def validate_non_negative(
    format_code,
    field_name,
    value,
    errors
):
    """
    Require a numeric value to be zero or greater.
    """

    if value < 0:

        errors.append(
            (
                f"{format_code}: "
                f"{field_name} cannot be negative."
            )
        )


# ============================================================================
# FORMAT VALIDATION
# ============================================================================

def validate_format(
    format_code,
    format_data
):

    errors = []

    warnings = []


    # ========================================================================
    # BASIC STRUCTURE
    # ========================================================================

    if not isinstance(
        format_data,
        dict
    ):

        return [
            (
                f"{format_code}: "
                "format definition must be a JSON object."
            )
        ], warnings


    # ========================================================================
    # REQUIRED FIELDS
    # ========================================================================

    for field_name, expected_type in REQUIRED_FIELDS.items():

        if field_name not in format_data:

            errors.append(
                (
                    f"{format_code}: "
                    f"missing required field '{field_name}'."
                )
            )

            continue


        value = format_data[
            field_name
        ]


        # bool is technically an int in Python.
        # Explicitly reject it for numeric fields.

        if expected_type != bool and isinstance(
            value,
            bool
        ):

            errors.append(
                (
                    f"{format_code}: "
                    f"'{field_name}' has invalid type."
                )
            )

            continue


        if not isinstance(
            value,
            expected_type
        ):

            errors.append(
                (
                    f"{format_code}: "
                    f"'{field_name}' has invalid type."
                )
            )


    if errors:

        return errors, warnings


    # ========================================================================
    # BASIC VALUES
    # ========================================================================

    validate_positive(
        format_code,
        "pageWidthMm",
        format_data[
            "pageWidthMm"
        ],
        errors
    )


    validate_positive(
        format_code,
        "pageHeightMm",
        format_data[
            "pageHeightMm"
        ],
        errors
    )


    validate_positive(
        format_code,
        "labelWidthMm",
        format_data[
            "labelWidthMm"
        ],
        errors
    )


    validate_positive(
        format_code,
        "labelHeightMm",
        format_data[
            "labelHeightMm"
        ],
        errors
    )


    validate_positive(
        format_code,
        "pitchXMm",
        format_data[
            "pitchXMm"
        ],
        errors
    )


    validate_positive(
        format_code,
        "pitchYMm",
        format_data[
            "pitchYMm"
        ],
        errors
    )


    validate_positive(
        format_code,
        "columns",
        format_data[
            "columns"
        ],
        errors
    )


    validate_positive(
        format_code,
        "rows",
        format_data[
            "rows"
        ],
        errors
    )


    validate_positive(
        format_code,
        "labelsPerSheet",
        format_data[
            "labelsPerSheet"
        ],
        errors
    )


    validate_non_negative(
        format_code,
        "marginLeftMm",
        format_data[
            "marginLeftMm"
        ],
        errors
    )


    validate_non_negative(
        format_code,
        "marginTopMm",
        format_data[
            "marginTopMm"
        ],
        errors
    )


    # ========================================================================
    # LABEL COUNT
    # ========================================================================

    expected_count = (
        format_data[
            "columns"
        ]
        *
        format_data[
            "rows"
        ]
    )


    if format_data[
        "labelsPerSheet"
    ] != expected_count:

        errors.append(
            (
                f"{format_code}: "
                "labelsPerSheet does not match "
                "columns x rows. "
                f"Expected {expected_count}, "
                f"got {format_data['labelsPerSheet']}."
            )
        )


    # ========================================================================
    # PITCH VS LABEL SIZE
    # ========================================================================

    if (
        format_data[
            "columns"
        ] > 1
        and
        format_data[
            "pitchXMm"
        ]
        <
        format_data[
            "labelWidthMm"
        ]
    ):

        errors.append(
            (
                f"{format_code}: "
                "pitchXMm is smaller than labelWidthMm. "
                "Labels would overlap horizontally."
            )
        )


    if (
        format_data[
            "rows"
        ] > 1
        and
        format_data[
            "pitchYMm"
        ]
        <
        format_data[
            "labelHeightMm"
        ]
    ):

        errors.append(
            (
                f"{format_code}: "
                "pitchYMm is smaller than labelHeightMm. "
                "Labels would overlap vertically."
            )
        )


    # ========================================================================
    # NOMINAL SHEET FIT
    #
    # Calibration values are deliberately NOT included here.
    # This verifies the manufacturer's physical geometry.
    # ========================================================================

    last_label_right = (
        format_data[
            "marginLeftMm"
        ]
        +
        (
            format_data[
                "columns"
            ]
            - 1
        )
        *
        format_data[
            "pitchXMm"
        ]
        +
        format_data[
            "labelWidthMm"
        ]
    )


    last_label_bottom = (
        format_data[
            "marginTopMm"
        ]
        +
        (
            format_data[
                "rows"
            ]
            - 1
        )
        *
        format_data[
            "pitchYMm"
        ]
        +
        format_data[
            "labelHeightMm"
        ]
    )


    if last_label_right > (
        format_data[
            "pageWidthMm"
        ]
        + 0.01
    ):

        errors.append(
            (
                f"{format_code}: "
                "nominal horizontal geometry exceeds "
                "the physical page width. "
                f"Right edge = {last_label_right:.3f} mm, "
                f"page width = "
                f"{format_data['pageWidthMm']:.3f} mm."
            )
        )


    if last_label_bottom > (
        format_data[
            "pageHeightMm"
        ]
        + 0.01
    ):

        errors.append(
            (
                f"{format_code}: "
                "nominal vertical geometry exceeds "
                "the physical page height. "
                f"Bottom edge = {last_label_bottom:.3f} mm, "
                f"page height = "
                f"{format_data['pageHeightMm']:.3f} mm."
            )
        )


    # ========================================================================
    # CALIBRATED GEOMETRY WARNING
    #
    # Calibration may intentionally move the print slightly outside nominal
    # geometry, so this is a warning rather than a hard validation error.
    # ========================================================================

    effective_pitch_x = (
        format_data[
            "pitchXMm"
        ]
        +
        format_data[
            "pitchXAdjustMm"
        ]
    )


    effective_pitch_y = (
        format_data[
            "pitchYMm"
        ]
        +
        format_data[
            "pitchYAdjustMm"
        ]
    )


    calibrated_right = (
        format_data[
            "marginLeftMm"
        ]
        +
        format_data[
            "offsetXmm"
        ]
        +
        (
            format_data[
                "columns"
            ]
            - 1
        )
        *
        effective_pitch_x
        +
        format_data[
            "labelWidthMm"
        ]
    )


    calibrated_bottom = (
        format_data[
            "marginTopMm"
        ]
        +
        format_data[
            "offsetYmm"
        ]
        +
        (
            format_data[
                "rows"
            ]
            - 1
        )
        *
        effective_pitch_y
        +
        format_data[
            "labelHeightMm"
        ]
    )


    calibrated_left = (
        format_data[
            "marginLeftMm"
        ]
        +
        format_data[
            "offsetXmm"
        ]
    )


    calibrated_top = (
        format_data[
            "marginTopMm"
        ]
        +
        format_data[
            "offsetYmm"
        ]
    )


    if calibrated_left < 0:

        warnings.append(
            (
                f"{format_code}: "
                "calibrated layout starts outside "
                "the left edge of the page."
            )
        )


    if calibrated_top < 0:

        warnings.append(
            (
                f"{format_code}: "
                "calibrated layout starts outside "
                "the top edge of the page."
            )
        )


    if calibrated_right > (
        format_data[
            "pageWidthMm"
        ]
        + 0.01
    ):

        warnings.append(
            (
                f"{format_code}: "
                "calibrated layout extends beyond "
                "the right edge of the page."
            )
        )


    if calibrated_bottom > (
        format_data[
            "pageHeightMm"
        ]
        + 0.01
    ):

        warnings.append(
            (
                f"{format_code}: "
                "calibrated layout extends beyond "
                "the bottom edge of the page."
            )
        )


    # ========================================================================
    # DISPLAY NAME SANITY CHECK
    # ========================================================================

    if not format_data[
        "displayName"
    ].strip():

        errors.append(
            (
                f"{format_code}: "
                "displayName cannot be empty."
            )
        )


    return errors, warnings


# ============================================================================
# MAIN VALIDATION
# ============================================================================

def main():

    print()
    print(
        "============================================================"
    )

    print(
        "MAAH LABEL RENDERER - LABEL FORMAT VALIDATION"
    )

    print(
        "============================================================"
    )

    print()


    # ========================================================================
    # RAW JSON
    # ========================================================================

    try:

        raw_data = load_raw_json()


    except Exception as error:

        print(
            "[FAIL] JSON could not be loaded."
        )

        print()

        print(
            error
        )

        print()

        return 1


    print(
        "[OK] JSON syntax is valid."
    )


    # ========================================================================
    # ROOT STRUCTURE
    # ========================================================================

    if not isinstance(
        raw_data,
        dict
    ):

        print(
            "[FAIL] Root JSON value must be an object."
        )

        return 1


    if raw_data.get(
        "schemaVersion"
    ) != "1.0":

        print(
            "[FAIL] schemaVersion must be '1.0'."
        )

        return 1


    formats = raw_data.get(
        "formats"
    )


    if not isinstance(
        formats,
        dict
    ):

        print(
            "[FAIL] 'formats' must be a JSON object."
        )

        return 1


    if not formats:

        print(
            "[FAIL] No label formats are defined."
        )

        return 1


    print(
        "[OK] Root structure is valid."
    )


    # ========================================================================
    # USE APPLICATION'S OWN LOADER
    #
    # This ensures the same Python validation used by the actual application
    # also accepts the configuration.
    # ========================================================================

    try:

        load_label_formats(
            LABEL_FORMATS_PATH
        )


    except Exception as error:

        print()

        print(
            "[FAIL] Application validator rejected label_formats.json."
        )

        print()

        print(
            error
        )

        print()

        return 1


    print(
        "[OK] Application loader accepts the file."
    )

    print()


    # ========================================================================
    # VALIDATE EACH FORMAT
    # ========================================================================

    total_errors = 0

    total_warnings = 0

    active_count = 0


    for format_code, format_data in (
        formats.items()
    ):

        errors, warnings = validate_format(
            format_code,
            format_data
        )


        if (
            isinstance(
                format_data,
                dict
            )
            and
            format_data.get(
                "active"
            ) is True
        ):

            active_count += 1


        if errors:

            status = "FAIL"

        elif warnings:

            status = "WARNING"

        else:

            status = "OK"


        if isinstance(
            format_data,
            dict
        ):

            width = format_data.get(
                "labelWidthMm",
                "?"
            )

            height = format_data.get(
                "labelHeightMm",
                "?"
            )

            labels = format_data.get(
                "labelsPerSheet",
                "?"
            )


        else:

            width = "?"

            height = "?"

            labels = "?"


        print(
            (
                f"[{status}] "
                f"{format_code:<10} "
                f"{width} x {height} mm "
                f"| {labels} labels/sheet"
            )
        )


        for warning in warnings:

            total_warnings += 1

            print(
                f"          WARNING: {warning}"
            )


        for error in errors:

            total_errors += 1

            print(
                f"          ERROR: {error}"
            )


    # ========================================================================
    # SUMMARY
    # ========================================================================

    print()

    print(
        "------------------------------------------------------------"
    )

    print(
        f"Formats checked : {len(formats)}"
    )

    print(
        f"Active formats  : {active_count}"
    )

    print(
        f"Warnings        : {total_warnings}"
    )

    print(
        f"Errors          : {total_errors}"
    )

    print(
        "------------------------------------------------------------"
    )

    print()


    if total_errors > 0:

        print(
            "VALIDATION FAILED"
        )

        print()

        print(
            "label_formats.json should NOT be used until "
            "the errors above are corrected."
        )

        print()

        return 1


    if total_warnings > 0:

        print(
            "VALIDATION PASSED WITH WARNINGS"
        )

        print()

        print(
            "The file can be loaded, but review the warnings "
            "before using the affected formats for production printing."
        )

        print()

        return 0


    print(
        "VALIDATION PASSED"
    )

    print()

    print(
        "label_formats.json is valid and ready for use."
    )

    print()

    return 0


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":

    sys.exit(
        main()
    )