from copy import deepcopy
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from svg_loader import (
    load_svg,
    local_name,
    validate_square_artwork
)

from label_formats import (
    get_effective_geometry,
    get_slot_origin_mm,
    build_page_slot_plan
)


# ============================================================================
# MAAH LABEL RENDERER
# SHEET LAYOUT
#
# Version: 1.0.0
#
# Responsibilities:
# - Create physical A4 SVG sheets
# - Generate solid label backgrounds
# - Apply background bleed
# - Uniformly scale square artwork
# - Center artwork inside each nominal label
# - Clip artwork to the nominal label area
# - Place labels into Avery slots
# - Generate one SVG per physical sheet
#
# This module knows nothing about:
# - JSON production paths
# - mappings
# - dynamic text replacement
# - PDF export
# ============================================================================


# ============================================================================
# SVG NAMESPACES
# ============================================================================

SVG_NS = "http://www.w3.org/2000/svg"

XLINK_NS = "http://www.w3.org/1999/xlink"


ET.register_namespace(
    "",
    SVG_NS
)

ET.register_namespace(
    "xlink",
    XLINK_NS
)

ET.register_namespace(
    "inkscape",
    "http://www.inkscape.org/namespaces/inkscape"
)

ET.register_namespace(
    "sodipodi",
    "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
)


def svg_tag(
    name
):

    return (
        f"{{{SVG_NS}}}{name}"
    )


# ============================================================================
# VISUAL SETTINGS
# ============================================================================

def validate_background_color(
    color
):
    """
    V1 supports solid hexadecimal RGB colors.

    Example:
    #FFFFFF
    #E8DCCB
    """

    if not isinstance(
        color,
        str
    ):

        raise ValueError(
            "Background color must be a string."
        )


    color = color.strip()


    if not re.fullmatch(
        r"#[0-9A-Fa-f]{6}",
        color
    ):

        raise ValueError(
            (
                "Background color must use "
                "the format #RRGGBB."
            )
        )


    return color.upper()


def validate_bleed_mm(
    bleed_mm
):
    """
    Bleed must be zero or positive.
    """

    try:

        value = float(
            bleed_mm
        )

    except (
        TypeError,
        ValueError
    ) as error:

        raise ValueError(
            "Bleed must be numeric."
        ) from error


    if value < 0:

        raise ValueError(
            "Bleed cannot be negative."
        )


    return value


def validate_artwork_scale_pct(
    scale_pct
):
    """
    Artwork scale must be positive.

    100 means:
    fit the square artwork to the shortest
    dimension of the physical label.

    Values over 100 are permitted, but the
    artwork is clipped to the nominal label area.
    """

    try:

        value = float(
            scale_pct
        )

    except (
        TypeError,
        ValueError
    ) as error:

        raise ValueError(
            "Artwork scale must be numeric."
        ) from error


    if value <= 0:

        raise ValueError(
            "Artwork scale must be > 0."
        )


    return value


# ============================================================================
# ARTWORK BOX
# ============================================================================

def get_artwork_box_mm(
    format_data,
    slot,
    artwork_scale_pct,
    calibration_overrides=None
):
    """
    Calculate the physical artwork square inside one label.

    Example:

    label = 99.1 x 67.7 mm
    scale = 95 %

    base size:
    min(99.1, 67.7) = 67.7

    artwork:
    67.7 * 0.95 = 64.315 mm
    """

    scale_pct = (
        validate_artwork_scale_pct(
            artwork_scale_pct
        )
    )


    origin = get_slot_origin_mm(
        format_data,
        slot,
        calibration_overrides
    )


    label_width = float(
        format_data[
            "labelWidthMm"
        ]
    )


    label_height = float(
        format_data[
            "labelHeightMm"
        ]
    )


    base_size = min(
        label_width,
        label_height
    )


    artwork_size = (

        base_size

        *

        (
            scale_pct
            /
            100.0
        )

    )


    artwork_x = (

        origin[
            "xMm"
        ]

        +

        (
            label_width
            -
            artwork_size
        )
        /
        2.0

    )


    artwork_y = (

        origin[
            "yMm"
        ]

        +

        (
            label_height
            -
            artwork_size
        )
        /
        2.0

    )


    return {
        "xMm":
            artwork_x,

        "yMm":
            artwork_y,

        "widthMm":
            artwork_size,

        "heightMm":
            artwork_size,

        "scalePct":
            scale_pct
    }


# ============================================================================
# ARTWORK SYMBOL
# ============================================================================

def create_artwork_symbol(
    source_root
):
    """
    Convert the rendered transparent artwork into
    one reusable SVG symbol.

    The original design units are preserved through
    the viewBox.

    512 x 512 is therefore NOT interpreted as mm.
    """

    source_tree = ET.ElementTree(
        source_root
    )


    viewbox = validate_square_artwork(
        source_tree
    )


    viewbox_text = (
        f"{viewbox['minX']} "
        f"{viewbox['minY']} "
        f"{viewbox['width']} "
        f"{viewbox['height']}"
    )


    symbol = ET.Element(
        svg_tag(
            "symbol"
        ),
        {
            "id":
                "maah_artwork_symbol",

            "viewBox":
                viewbox_text,

            "preserveAspectRatio":
                "xMidYMid meet"
        }
    )


    # Preserve a root-level style if one exists.
    root_style = source_root.get(
        "style"
    )


    if root_style:

        symbol.set(
            "style",
            root_style
        )


    for child in source_root:

        name = local_name(
            child.tag
        )


        # Inkscape editor metadata is not needed
        # in the generated print sheet.
        if name in {
            "namedview",
            "metadata"
        }:

            continue


        symbol.append(
            deepcopy(
                child
            )
        )


    return symbol


# ============================================================================
# CLIP PATH
# ============================================================================

def add_slot_clip_path(
    defs,
    slot,
    origin,
    label_width,
    label_height
):
    """
    Artwork is clipped to the nominal physical label.

    Background bleed is intentionally NOT clipped.
    """

    clip_id = (
        f"maah_clip_slot_{slot}"
    )


    clip_path = ET.SubElement(
        defs,
        svg_tag(
            "clipPath"
        ),
        {
            "id":
                clip_id,

            "clipPathUnits":
                "userSpaceOnUse"
        }
    )


    ET.SubElement(
        clip_path,
        svg_tag(
            "rect"
        ),
        {
            "x":
                str(
                    origin[
                        "xMm"
                    ]
                ),

            "y":
                str(
                    origin[
                        "yMm"
                    ]
                ),

            "width":
                str(
                    label_width
                ),

            "height":
                str(
                    label_height
                )
        }
    )


    return clip_id


# ============================================================================
# CREATE ONE SHEET PAGE
# ============================================================================

def create_sheet_page(
    source_root,
    format_data,
    slots,
    artwork_scale_pct,
    background_color,
    bleed_mm,
    calibration_overrides=None
):
    """
    Create one physical print-sheet SVG.
    """

    geometry = get_effective_geometry(
        format_data,
        calibration_overrides
    )


    background_color = (
        validate_background_color(
            background_color
        )
    )


    bleed_mm = validate_bleed_mm(
        bleed_mm
    )


    artwork_scale_pct = (
        validate_artwork_scale_pct(
            artwork_scale_pct
        )
    )


    page_width = float(
        geometry[
            "pageWidthMm"
        ]
    )


    page_height = float(
        geometry[
            "pageHeightMm"
        ]
    )


    label_width = float(
        geometry[
            "labelWidthMm"
        ]
    )


    label_height = float(
        geometry[
            "labelHeightMm"
        ]
    )


    # ------------------------------------------------------------------------
    # A4 ROOT
    #
    # The outer viewBox is expressed directly in millimeters.
    #
    # 1 user unit = 1 mm inside this generated sheet.
    # ------------------------------------------------------------------------

    root = ET.Element(
        svg_tag(
            "svg"
        ),
        {
            "width":
                f"{page_width}mm",

            "height":
                f"{page_height}mm",

            "viewBox":
                (
                    f"0 0 "
                    f"{page_width} "
                    f"{page_height}"
                ),

            "version":
                "1.1"
        }
    )


    defs = ET.SubElement(
        root,
        svg_tag(
            "defs"
        )
    )


    # ------------------------------------------------------------------------
    # ARTWORK SYMBOL
    # ------------------------------------------------------------------------

    artwork_symbol = (
        create_artwork_symbol(
            source_root
        )
    )


    defs.append(
        artwork_symbol
    )


    # ------------------------------------------------------------------------
    # PRECALCULATE SLOT DATA + CLIPPING
    # ------------------------------------------------------------------------

    slot_data = []


    for slot in slots:

        origin = get_slot_origin_mm(
            format_data,
            slot,
            calibration_overrides
        )


        artwork_box = get_artwork_box_mm(
            format_data,
            slot,
            artwork_scale_pct,
            calibration_overrides
        )


        clip_id = add_slot_clip_path(
            defs=defs,
            slot=slot,
            origin=origin,
            label_width=label_width,
            label_height=label_height
        )


        slot_data.append(
            {
                "slot":
                    slot,

                "origin":
                    origin,

                "artwork":
                    artwork_box,

                "clipId":
                    clip_id
            }
        )


    # ========================================================================
    # BACKGROUND LAYER
    #
    # ALL backgrounds are drawn before ANY artwork.
    #
    # This matters because bleed regions can overlap
    # adjacent labels.
    # ========================================================================

    background_layer = ET.SubElement(
        root,
        svg_tag(
            "g"
        ),
        {
            "id":
                "maah_background_layer"
        }
    )


    for item in slot_data:

        origin = item[
            "origin"
        ]


        background_x = (

            origin[
                "xMm"
            ]

            -
            bleed_mm

        )


        background_y = (

            origin[
                "yMm"
            ]

            -
            bleed_mm

        )


        background_width = (

            label_width

            +

            bleed_mm
            *
            2.0

        )


        background_height = (

            label_height

            +

            bleed_mm
            *
            2.0

        )


        ET.SubElement(
            background_layer,
            svg_tag(
                "rect"
            ),
            {
                "class":
                    "maah-label-background",

                "data-slot":
                    str(
                        item[
                            "slot"
                        ]
                    ),

                "x":
                    str(
                        background_x
                    ),

                "y":
                    str(
                        background_y
                    ),

                "width":
                    str(
                        background_width
                    ),

                "height":
                    str(
                        background_height
                    ),

                "fill":
                    background_color
            }
        )


    # ========================================================================
    # ARTWORK LAYER
    # ========================================================================

    artwork_layer = ET.SubElement(
        root,
        svg_tag(
            "g"
        ),
        {
            "id":
                "maah_artwork_layer"
        }
    )


    for item in slot_data:

        artwork = item[
            "artwork"
        ]


        use = ET.SubElement(
            artwork_layer,
            svg_tag(
                "use"
            ),
            {
                "class":
                    "maah-label-artwork",

                "data-slot":
                    str(
                        item[
                            "slot"
                        ]
                    ),

                "x":
                    str(
                        artwork[
                            "xMm"
                        ]
                    ),

                "y":
                    str(
                        artwork[
                            "yMm"
                        ]
                    ),

                "width":
                    str(
                        artwork[
                            "widthMm"
                        ]
                    ),

                "height":
                    str(
                        artwork[
                            "heightMm"
                        ]
                    ),

                "href":
                    "#maah_artwork_symbol",

                "clip-path":
                    (
                        "url(#"
                        f"{item['clipId']}"
                        ")"
                    )
            }
        )


        # Compatibility with older SVG readers.
        use.set(
            f"{{{XLINK_NS}}}href",
            "#maah_artwork_symbol"
        )


    return ET.ElementTree(
        root
    )


# ============================================================================
# GENERATE SHEET SVGS
# ============================================================================

def generate_sheet_svgs(
    rendered_artwork_svg,
    format_data,
    quantity,
    start_position,
    output_folder,
    artwork_scale_pct,
    background_color,
    bleed_mm,
    calibration_overrides=None
):
    """
    Generate one SVG per physical print sheet.
    """

    rendered_artwork_svg = Path(
        rendered_artwork_svg
    )


    output_folder = Path(
        output_folder
    )


    if not rendered_artwork_svg.exists():

        raise FileNotFoundError(
            (
                "Rendered artwork SVG "
                f"not found: {rendered_artwork_svg}"
            )
        )


    # ------------------------------------------------------------------------
    # LOAD + VALIDATE ARTWORK
    # ------------------------------------------------------------------------

    source_tree = load_svg(
        rendered_artwork_svg
    )


    validate_square_artwork(
        source_tree
    )


    source_root = source_tree.getroot()


    # ------------------------------------------------------------------------
    # VALIDATE VISUAL SETTINGS
    # ------------------------------------------------------------------------

    artwork_scale_pct = (
        validate_artwork_scale_pct(
            artwork_scale_pct
        )
    )


    background_color = (
        validate_background_color(
            background_color
        )
    )


    bleed_mm = validate_bleed_mm(
        bleed_mm
    )


    # ------------------------------------------------------------------------
    # PAGE PLAN
    # ------------------------------------------------------------------------

    page_plan = build_page_slot_plan(
        format_data,
        quantity,
        start_position
    )


    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )


    format_code = format_data[
        "formatCode"
    ]


    results = []


    # ------------------------------------------------------------------------
    # CREATE EACH PAGE
    # ------------------------------------------------------------------------

    for page_number, slots in enumerate(
        page_plan,
        start=1
    ):

        page_tree = create_sheet_page(
            source_root=source_root,
            format_data=format_data,
            slots=slots,
            artwork_scale_pct=artwork_scale_pct,
            background_color=background_color,
            bleed_mm=bleed_mm,
            calibration_overrides=calibration_overrides
        )


        filename = (
            f"{rendered_artwork_svg.stem}"
            f"__{format_code}"
            f"__page_{page_number:02d}"
            f".svg"
        )


        output_path = (
            output_folder
            /
            filename
        )


        page_tree.write(
            output_path,
            encoding="utf-8",
            xml_declaration=True
        )


        if not output_path.exists():

            raise RuntimeError(
                (
                    "Sheet SVG was not created: "
                    f"{output_path}"
                )
            )


        if output_path.stat().st_size <= 0:

            raise RuntimeError(
                (
                    "Generated sheet SVG is empty: "
                    f"{output_path}"
                )
            )


        results.append(
            {
                "page":
                    page_number,

                "slots":
                    list(
                        slots
                    ),

                "filename":
                    filename,

                "outputPath":
                    output_path,

                "bytes":
                    output_path.stat().st_size
            }
        )


    return {
        "formatCode":
            format_code,

        "quantity":
            int(
                quantity
            ),

        "startPosition":
            int(
                start_position
            ),

        "artworkScalePct":
            artwork_scale_pct,

        "backgroundColor":
            background_color,

        "bleedMm":
            bleed_mm,

        "pageCount":
            len(
                results
            ),

        "pages":
            results
    }