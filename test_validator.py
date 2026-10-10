from pathlib import Path

from json_loader import (
    load_json
)

from svg_loader import (
    load_svg
)

from validator import (
    validate_render_inputs
)


# ============================================================================
# CONFIG
# ============================================================================

JSON_FILE = Path(
    "input/test_label_job.json"
)


SVG_FILE = Path(
    "templates/test_artwork.svg"
)


VALID_MAPPING = {

    "field_product_name":
        "product.labelName",

    "field_frozen_status":
        "product.frozenStatus",

    "field_net_weight":
        "product.netWeightText"

}


# ============================================================================
# LOAD
# ============================================================================

json_data = load_json(
    JSON_FILE
)


svg_tree = load_svg(
    SVG_FILE
)


# ============================================================================
# VALID TEST
# ============================================================================

result = validate_render_inputs(
    json_data,
    svg_tree,
    VALID_MAPPING
)


if result["valid"] is not True:

    raise RuntimeError(
        "Expected validation to succeed."
    )


if result["fieldCount"] != 3:

    raise RuntimeError(
        "Unexpected validated field count."
    )


if (
    result["values"][
        "field_product_name"
    ]
    !=
    "Chicken Curry"
):

    raise RuntimeError(
        "Product name resolution failed."
    )


if (
    result["values"][
        "field_frozen_status"
    ]
    !=
    "Tiefgefroren"
):

    raise RuntimeError(
        "Frozen status resolution failed."
    )


if (
    result["values"][
        "field_net_weight"
    ]
    !=
    "500 g"
):

    raise RuntimeError(
        "Net weight resolution failed."
    )


# ============================================================================
# NEGATIVE TEST 1
# Missing SVG mapping must fail.
# ============================================================================

INCOMPLETE_MAPPING = {

    "field_product_name":
        "product.labelName",

    "field_net_weight":
        "product.netWeightText"

}


try:

    validate_render_inputs(
        json_data,
        svg_tree,
        INCOMPLETE_MAPPING
    )


    raise RuntimeError(
        (
            "Validator incorrectly accepted "
            "an incomplete mapping."
        )
    )


except ValueError:

    pass


# ============================================================================
# NEGATIVE TEST 2
# Invalid JSON path must fail.
# ============================================================================

INVALID_JSON_MAPPING = {

    "field_product_name":
        "product.doesNotExist",

    "field_frozen_status":
        "product.frozenStatus",

    "field_net_weight":
        "product.netWeightText"

}


try:

    validate_render_inputs(
        json_data,
        svg_tree,
        INVALID_JSON_MAPPING
    )


    raise RuntimeError(
        (
            "Validator incorrectly accepted "
            "an invalid JSON path."
        )
    )


except ValueError:

    pass


# ============================================================================
# OUTPUT
# ============================================================================

print(
    "Resolved fields:"
)


for field in result["fields"]:

    print(
        (
            f" - {field['svgId']} "
            f"<- "
            f"{field['jsonPath']} "
            f"= "
            f"{field['value']}"
        )
    )


print()

print(
    "Incomplete mapping rejection: OK"
)

print(
    "Invalid JSON path rejection: OK"
)

print()

print(
    "VALIDATOR TEST: OK"
)