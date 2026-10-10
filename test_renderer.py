from pathlib import Path

from json_loader import (
    load_json
)

from svg_loader import (
    load_svg,
    get_viewbox
)

from validator import (
    validate_render_inputs
)

from renderer import (
    render_artwork,
    get_text_by_id
)


# ============================================================================
# FILES
# ============================================================================

JSON_FILE = Path(
    "input/test_label_job.json"
)


TEMPLATE_FILE = Path(
    "templates/test_artwork.svg"
)


OUTPUT_FILE = Path(
    "output/test_artwork_rendered.svg"
)


# ============================================================================
# MAPPING
# ============================================================================

MAPPING = {

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
    TEMPLATE_FILE
)


original_viewbox = get_viewbox(
    svg_tree
)


# ============================================================================
# VALIDATE
# ============================================================================

validation = validate_render_inputs(
    json_data,
    svg_tree,
    MAPPING
)


# ============================================================================
# RENDER
# ============================================================================

result = render_artwork(
    template_path=TEMPLATE_FILE,
    resolved_values=validation["values"],
    output_path=OUTPUT_FILE
)


# ============================================================================
# RELOAD GENERATED SVG
# ============================================================================

rendered_tree = load_svg(
    OUTPUT_FILE
)


rendered_viewbox = get_viewbox(
    rendered_tree
)


# ============================================================================
# VERIFY VIEWBOX
# ============================================================================

if (
    rendered_viewbox
    !=
    original_viewbox
):

    raise RuntimeError(
        "Renderer modified the artwork viewBox."
    )


# ============================================================================
# VERIFY VALUES
# ============================================================================

product_name = get_text_by_id(
    rendered_tree,
    "field_product_name"
)


frozen_status = get_text_by_id(
    rendered_tree,
    "field_frozen_status"
)


net_weight = get_text_by_id(
    rendered_tree,
    "field_net_weight"
)


if product_name != "Chicken Curry":

    raise RuntimeError(
        (
            "Product name rendering failed. "
            f"Actual: {product_name}"
        )
    )


if frozen_status != "Tiefgefroren":

    raise RuntimeError(
        (
            "Frozen status rendering failed. "
            f"Actual: {frozen_status}"
        )
    )


if net_weight != "500 g":

    raise RuntimeError(
        (
            "Net weight rendering failed. "
            f"Actual: {net_weight}"
        )
    )


# ============================================================================
# VERIFY ORIGINAL TEMPLATE WAS NOT MODIFIED
# ============================================================================

original_tree_again = load_svg(
    TEMPLATE_FILE
)


original_product_name = get_text_by_id(
    original_tree_again,
    "field_product_name"
)


if original_product_name != "PRODUCT NAME":

    raise RuntimeError(
        (
            "Original artwork was modified. "
            "The renderer must never modify "
            "the master template."
        )
    )


# ============================================================================
# OUTPUT
# ============================================================================

print(
    "Rendered fields:"
)


for field in result["fields"]:

    print(
        (
            f" - {field['svgId']} "
            f"= "
            f"{field['value']}"
        )
    )


print()

print(
    (
        "ViewBox preserved: "
        f"{rendered_viewbox['width']} x "
        f"{rendered_viewbox['height']}"
    )
)


print(
    (
        "Output: "
        f"{result['outputPath']}"
    )
)


print(
    (
        "Bytes: "
        f"{result['bytes']}"
    )
)


print()

print(
    "Original template unchanged: OK"
)

print(
    "RENDERER TEST: OK"
)