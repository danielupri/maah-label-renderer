import xml.etree.ElementTree as ET
from pathlib import Path

from svg_loader import (
    load_svg,
    local_name
)


# ============================================================================
# MAAH LABEL RENDERER
# ARTWORK RENDERER
#
# Version: 1.0.0
#
# Responsibilities:
# - Load a fresh SVG artwork
# - Find dynamic text objects by ID
# - Replace their text values
# - Preserve the artwork viewBox and visual structure
# - Save a new transparent rendered SVG
#
# This module knows nothing about:
# - JSON paths
# - mappings
# - Avery formats
# - physical dimensions
# - backgrounds
# - bleed
# - printing
# ============================================================================


# ============================================================================
# COMMON SVG NAMESPACES
# ============================================================================

ET.register_namespace(
    "",
    "http://www.w3.org/2000/svg"
)

ET.register_namespace(
    "xlink",
    "http://www.w3.org/1999/xlink"
)

ET.register_namespace(
    "inkscape",
    "http://www.inkscape.org/namespaces/inkscape"
)

ET.register_namespace(
    "sodipodi",
    "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
)


# ============================================================================
# FIND ELEMENT
# ============================================================================

def find_element_by_id(
    tree,
    element_id
):
    """
    Find one SVG element by ID.

    Returns the element or None.
    """

    root = tree.getroot()


    for element in root.iter():

        if element.get(
            "id"
        ) == element_id:

            return element


    return None


# ============================================================================
# REPLACE TEXT
# ============================================================================

def set_text_by_id(
    tree,
    element_id,
    value
):
    """
    Replace the content of a dynamic SVG text object.

    For Inkscape-style text containing <tspan> elements:

    - first tspan receives the value
    - additional tspans are cleared

    Existing position, font, fill, transform and styling
    remain untouched.
    """

    element = find_element_by_id(
        tree,
        element_id
    )


    if element is None:

        raise ValueError(
            f"SVG element not found: {element_id}"
        )


    if local_name(
        element.tag
    ) != "text":

        raise ValueError(
            (
                f"SVG element '{element_id}' "
                "is not a text object."
            )
        )


    text_value = str(
        value
    )


    tspans = [

        child

        for child in element.iter()

        if (
            child is not element
            and
            local_name(
                child.tag
            ) == "tspan"
        )

    ]


    if tspans:

        tspans[0].text = (
            text_value
        )


        for extra_tspan in tspans[1:]:

            extra_tspan.text = ""


    else:

        element.text = (
            text_value
        )


    return True


# ============================================================================
# READ TEXT
# ============================================================================

def get_text_by_id(
    tree,
    element_id
):
    """
    Read the visible text content of one SVG text object.

    Mainly useful for testing and verification.
    """

    element = find_element_by_id(
        tree,
        element_id
    )


    if element is None:

        raise ValueError(
            f"SVG element not found: {element_id}"
        )


    if local_name(
        element.tag
    ) != "text":

        raise ValueError(
            (
                f"SVG element '{element_id}' "
                "is not a text object."
            )
        )


    text_parts = []


    for text in element.itertext():

        if text:

            cleaned = text.strip()


            if cleaned:

                text_parts.append(
                    cleaned
                )


    return " ".join(
        text_parts
    )


# ============================================================================
# RENDER ARTWORK
# ============================================================================

def render_artwork(
    template_path,
    resolved_values,
    output_path
):
    """
    Render dynamic values into a fresh SVG artwork.

    resolved_values example:

    {
        "field_product_name": "Chicken Curry",
        "field_frozen_status": "Tiefgefroren",
        "field_net_weight": "500 g"
    }

    Returns information about the generated file.
    """

    template_path = Path(
        template_path
    )


    output_path = Path(
        output_path
    )


    if not isinstance(
        resolved_values,
        dict
    ):

        raise ValueError(
            "Resolved values must be a dictionary."
        )


    if not resolved_values:

        raise ValueError(
            "No resolved values were provided."
        )


    # ------------------------------------------------------------------------
    # Always reload the original template.
    #
    # This guarantees that previous rendering operations
    # never modify the master artwork.
    # ------------------------------------------------------------------------

    tree = load_svg(
        template_path
    )


    rendered_fields = []


    for element_id, value in (
        resolved_values.items()
    ):

        if value is None:

            raise ValueError(
                (
                    f"Resolved value is None: "
                    f"{element_id}"
                )
            )


        set_text_by_id(
            tree,
            element_id,
            value
        )


        rendered_fields.append(
            {
                "svgId":
                    element_id,

                "value":
                    str(value)
            }
        )


    # ------------------------------------------------------------------------
    # OUTPUT
    # ------------------------------------------------------------------------

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    tree.write(
        output_path,
        encoding="utf-8",
        xml_declaration=True
    )


    if not output_path.exists():

        raise RuntimeError(
            "Rendered SVG was not created."
        )


    if output_path.stat().st_size <= 0:

        raise RuntimeError(
            "Rendered SVG is empty."
        )


    return {
        "outputPath":
            output_path,

        "filename":
            output_path.name,

        "bytes":
            output_path.stat().st_size,

        "fields":
            rendered_fields,

        "fieldCount":
            len(
                rendered_fields
            )
    }