from pathlib import Path

from svg_loader import (
    load_svg,
    get_viewbox,
    validate_square_artwork,
    get_dynamic_text_ids,
    get_artwork_info
)


# ============================================================================
# CONFIG
# ============================================================================

SVG_FILE = Path(
    "templates/test_artwork.svg"
)


# ============================================================================
# LOAD
# ============================================================================

tree = load_svg(
    SVG_FILE
)


# ============================================================================
# VIEWBOX
# ============================================================================

viewbox = get_viewbox(
    tree
)


if viewbox["width"] != 512:

    raise RuntimeError(
        "Unexpected artwork width."
    )


if viewbox["height"] != 512:

    raise RuntimeError(
        "Unexpected artwork height."
    )


# ============================================================================
# SQUARE ARTWORK
# ============================================================================

validate_square_artwork(
    tree
)


# ============================================================================
# DYNAMIC FIELDS
# ============================================================================

fields = get_dynamic_text_ids(
    tree
)


expected_fields = {

    "field_product_name",
    "field_frozen_status",
    "field_net_weight"

}


if set(fields) != expected_fields:

    raise RuntimeError(
        (
            "Unexpected SVG fields.\n"
            f"Expected: {sorted(expected_fields)}\n"
            f"Actual: {fields}"
        )
    )


# ============================================================================
# COMPLETE INFO
# ============================================================================

info = get_artwork_info(
    tree
)


# ============================================================================
# OUTPUT
# ============================================================================

print(
    "Artwork viewBox:"
)

print(
    (
        f" - Min X: {viewbox['minX']}"
    )
)

print(
    (
        f" - Min Y: {viewbox['minY']}"
    )
)

print(
    (
        f" - Width: {viewbox['width']}"
    )
)

print(
    (
        f" - Height: {viewbox['height']}"
    )
)


print()

print(
    "Dynamic SVG fields:"
)


for field in fields:

    print(
        f" - {field}"
    )


print()

print(
    (
        "Dynamic field count: "
        f"{info['dynamicFieldCount']}"
    )
)


print()

print(
    "SVG LOADER TEST: OK"
)