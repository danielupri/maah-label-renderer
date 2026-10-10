from pathlib import Path

from json_loader import (
    load_json,
    get_json_paths,
    get_value_by_path
)


# ============================================================================
# CONFIG
# ============================================================================

JSON_FILE = Path(
    "input/test_label_job.json"
)


# ============================================================================
# LOAD
# ============================================================================

data = load_json(
    JSON_FILE
)


# ============================================================================
# PATH DETECTION
# ============================================================================

paths = sorted(
    get_json_paths(
        data
    )
)


required_paths = {

    "labelId",

    "lot.lotId",

    "product.labelName",
    "product.frozenStatus",
    "product.netWeightText",

    "print.formatCode",
    "print.quantity",
    "print.startPosition"

}


missing_paths = (
    required_paths
    -
    set(paths)
)


if missing_paths:

    raise RuntimeError(
        (
            "Missing expected JSON paths: "
            +
            ", ".join(
                sorted(
                    missing_paths
                )
            )
        )
    )


# ============================================================================
# VALUE TESTS
# ============================================================================

if (
    get_value_by_path(
        data,
        "product.labelName"
    )
    !=
    "Chicken Curry"
):

    raise RuntimeError(
        "product.labelName test failed."
    )


if (
    get_value_by_path(
        data,
        "product.netWeightText"
    )
    !=
    "500 g"
):

    raise RuntimeError(
        "product.netWeightText test failed."
    )


if (
    get_value_by_path(
        data,
        "print.formatCode"
    )
    !=
    "L7976"
):

    raise RuntimeError(
        "print.formatCode test failed."
    )


if (
    get_value_by_path(
        data,
        "print.quantity"
    )
    !=
    10
):

    raise RuntimeError(
        "print.quantity test failed."
    )


# ============================================================================
# OUTPUT
# ============================================================================

print(
    "Detected JSON fields:"
)


for path in paths:

    print(
        f" - {path}"
    )


print()

print(
    "Product:",
    get_value_by_path(
        data,
        "product.labelName"
    )
)


print(
    "Weight:",
    get_value_by_path(
        data,
        "product.netWeightText"
    )
)


print(
    "Format:",
    get_value_by_path(
        data,
        "print.formatCode"
    )
)


print(
    "Quantity:",
    get_value_by_path(
        data,
        "print.quantity"
    )
)


print()

print(
    "JSON LOADER TEST: OK"
)