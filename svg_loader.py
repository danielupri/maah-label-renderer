import xml.etree.ElementTree as ET
from pathlib import Path


# ============================================================================
# MAAH LABEL RENDERER
# SVG LOADER
#
# Version: 1.0.0
#
# Responsibilities:
# - Load SVG artwork
# - Read artwork viewBox
# - Detect dynamic text fields
# - Validate duplicate IDs
#
# This module knows nothing about:
# - physical dimensions
# - Avery formats
# - artwork scaling
# - backgrounds
# - printing
# ============================================================================


SVG_NAMESPACE = "http://www.w3.org/2000/svg"

DYNAMIC_FIELD_PREFIX = "field_"


# ============================================================================
# HELPERS
# ============================================================================

def local_name(tag):
    """
    Remove XML namespace from a tag.

    Example:
    {http://www.w3.org/2000/svg}text
    becomes:
    text
    """

    if "}" in tag:
        return tag.split("}", 1)[1]

    return tag


# ============================================================================
# LOAD SVG
# ============================================================================

def load_svg(file_path):
    """
    Load an SVG file and return its ElementTree.
    """

    path = Path(file_path)


    if not path.exists():

        raise FileNotFoundError(
            f"SVG file not found: {path}"
        )


    if path.suffix.lower() != ".svg":

        raise ValueError(
            "Selected file is not an SVG file."
        )


    try:

        tree = ET.parse(
            path
        )

    except ET.ParseError as error:

        raise ValueError(
            f"Invalid SVG/XML file: {error}"
        ) from error


    root = tree.getroot()


    if local_name(
        root.tag
    ) != "svg":

        raise ValueError(
            "Root element is not an SVG."
        )


    return tree


# ============================================================================
# VIEWBOX
# ============================================================================

def get_viewbox(
    tree
):
    """
    Read and validate the SVG viewBox.

    Returns:

    {
        "minX": 0.0,
        "minY": 0.0,
        "width": 512.0,
        "height": 512.0
    }

    The numbers are design units, NOT millimeters.
    """

    root = tree.getroot()


    raw_viewbox = root.get(
        "viewBox"
    )


    if not raw_viewbox:

        raise ValueError(
            "SVG artwork must contain a viewBox."
        )


    parts = (
        raw_viewbox
        .replace(",", " ")
        .split()
    )


    if len(parts) != 4:

        raise ValueError(
            (
                "SVG viewBox must contain "
                "exactly 4 numbers."
            )
        )


    try:

        min_x = float(
            parts[0]
        )

        min_y = float(
            parts[1]
        )

        width = float(
            parts[2]
        )

        height = float(
            parts[3]
        )

    except ValueError as error:

        raise ValueError(
            "SVG viewBox contains invalid numbers."
        ) from error


    if width <= 0 or height <= 0:

        raise ValueError(
            "SVG viewBox width and height must be > 0."
        )


    return {
        "minX":
            min_x,

        "minY":
            min_y,

        "width":
            width,

        "height":
            height
    }


# ============================================================================
# ARTWORK VALIDATION
# ============================================================================

def validate_square_artwork(
    tree,
    tolerance=0.001
):
    """
    V1 artwork standard:
    square SVG design space.

    512x512 is recommended, but not hardcoded.
    1024x1024 would also be valid.
    """

    viewbox = get_viewbox(
        tree
    )


    difference = abs(
        viewbox["width"]
        -
        viewbox["height"]
    )


    if difference > tolerance:

        raise ValueError(
            (
                "V1 artwork must use a square viewBox.\n"
                f"Current viewBox: "
                f"{viewbox['width']} x "
                f"{viewbox['height']}"
            )
        )


    return viewbox


# ============================================================================
# VALIDATE IDS
# ============================================================================

def validate_unique_ids(
    tree
):
    """
    Ensure that IDs are unique across the complete SVG.
    """

    root = tree.getroot()

    seen = set()


    for element in root.iter():

        element_id = element.get(
            "id"
        )


        if not element_id:

            continue


        element_id = (
            element_id.strip()
        )


        if not element_id:

            continue


        if element_id in seen:

            raise ValueError(
                (
                    "Duplicate SVG ID detected: "
                    f"{element_id}"
                )
            )


        seen.add(
            element_id
        )


    return True


# ============================================================================
# DYNAMIC TEXT FIELDS
# ============================================================================

def get_dynamic_text_ids(
    tree
):
    """
    Detect dynamic text objects.

    A dynamic V1 field must:

    1. Be an SVG <text> element
    2. Have an ID beginning with "field_"

    Example:

    field_product_name
    field_frozen_status
    field_net_weight
    """

    validate_unique_ids(
        tree
    )


    root = tree.getroot()

    dynamic_ids = []


    for element in root.iter():

        if local_name(
            element.tag
        ) != "text":

            continue


        element_id = element.get(
            "id"
        )


        if not element_id:

            continue


        element_id = (
            element_id.strip()
        )


        if not element_id.startswith(
            DYNAMIC_FIELD_PREFIX
        ):

            continue


        dynamic_ids.append(
            element_id
        )


    return sorted(
        dynamic_ids
    )


# ============================================================================
# ARTWORK INFO
# ============================================================================

def get_artwork_info(
    tree
):
    """
    Return basic information about the artwork.
    """

    viewbox = validate_square_artwork(
        tree
    )


    dynamic_fields = (
        get_dynamic_text_ids(
            tree
        )
    )


    return {
        "viewBox":
            viewbox,

        "dynamicFields":
            dynamic_fields,

        "dynamicFieldCount":
            len(
                dynamic_fields
            )
    }