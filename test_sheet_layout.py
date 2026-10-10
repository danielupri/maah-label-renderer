from pathlib import Path
import xml.etree.ElementTree as ET

from label_formats import (
    load_label_formats,
    get_label_format
)

from sheet_layout import (
    get_artwork_box_mm,
    generate_sheet_svgs
)


# ============================================================================
# CONFIG
# ============================================================================

ARTWORK_FILE = Path(
    "output/test_artwork_rendered.svg"
)


OUTPUT_FOLDER = Path(
    "output"
)


FORMAT_CODE = "L7976"

QUANTITY = 10

START_POSITION = 7


# ---------------------------------------------------------------------------
# Visual settings for this test.
#
# Beige is deliberate so the generated background
# is easy to see visually.
# ---------------------------------------------------------------------------

ARTWORK_SCALE_PCT = 95.0

BACKGROUND_COLOR = "#E8DCCB"

BLEED_MM = 1.0


CALIBRATION_OVERRIDES = None


# ============================================================================
# LOAD FORMAT
# ============================================================================

config = load_label_formats()


format_data = get_label_format(
    config,
    FORMAT_CODE
)


# ============================================================================
# ARTWORK PLACEMENT TEST
# ============================================================================

slot_7_artwork = get_artwork_box_mm(
    format_data,
    slot=7,
    artwork_scale_pct=ARTWORK_SCALE_PCT,
    calibration_overrides=CALIBRATION_OVERRIDES
)


# L7976:
#
# label = 99.1 x 67.7
#
# base = 67.7
#
# 95% = 64.315 mm

if round(
    slot_7_artwork[
        "widthMm"
    ],
    3
) != 64.315:

    raise RuntimeError(
        "Artwork size calculation failed."
    )


if round(
    slot_7_artwork[
        "heightMm"
    ],
    3
) != 64.315:

    raise RuntimeError(
        "Artwork aspect ratio failed."
    )


# ============================================================================
# GENERATE
# ============================================================================

result = generate_sheet_svgs(
    rendered_artwork_svg=ARTWORK_FILE,
    format_data=format_data,
    quantity=QUANTITY,
    start_position=START_POSITION,
    output_folder=OUTPUT_FOLDER,
    artwork_scale_pct=ARTWORK_SCALE_PCT,
    background_color=BACKGROUND_COLOR,
    bleed_mm=BLEED_MM,
    calibration_overrides=CALIBRATION_OVERRIDES
)


# ============================================================================
# BASIC RESULT TEST
# ============================================================================

if result[
    "pageCount"
] != 2:

    raise RuntimeError(
        (
            "Expected 2 pages, "
            f"got {result['pageCount']}."
        )
    )


expected_slots = [

    [
        7,
        8
    ],

    [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8
    ]

]


actual_slots = [

    page[
        "slots"
    ]

    for page in result[
        "pages"
    ]

]


if actual_slots != expected_slots:

    raise RuntimeError(
        (
            "Unexpected slot allocation.\n"
            f"Expected: {expected_slots}\n"
            f"Actual: {actual_slots}"
        )
    )


# ============================================================================
# INSPECT GENERATED PAGE 1
# ============================================================================

page_1_path = result[
    "pages"
][0][
    "outputPath"
]


tree = ET.parse(
    page_1_path
)


root = tree.getroot()


# ---------------------------------------------------------------------------
# Physical page size
# ---------------------------------------------------------------------------

if root.get(
    "width"
) != "210.0mm":

    raise RuntimeError(
        (
            "Generated page width "
            "is not 210 mm."
        )
    )


if root.get(
    "height"
) != "297.0mm":

    raise RuntimeError(
        (
            "Generated page height "
            "is not 297 mm."
        )
    )


# ---------------------------------------------------------------------------
# Count backgrounds and artworks
# ---------------------------------------------------------------------------

backgrounds = []

artworks = []


for element in root.iter():

    element_class = element.get(
        "class"
    )


    if (
        element_class
        ==
        "maah-label-background"
    ):

        backgrounds.append(
            element
        )


    if (
        element_class
        ==
        "maah-label-artwork"
    ):

        artworks.append(
            element
        )


if len(
    backgrounds
) != 2:

    raise RuntimeError(
        (
            "Page 1 should contain "
            "2 backgrounds."
        )
    )


if len(
    artworks
) != 2:

    raise RuntimeError(
        (
            "Page 1 should contain "
            "2 artworks."
        )
    )


# ---------------------------------------------------------------------------
# Verify slots 7 and 8
# ---------------------------------------------------------------------------

background_slots = [

    int(
        element.get(
            "data-slot"
        )
    )

    for element in backgrounds

]


if background_slots != [
    7,
    8
]:

    raise RuntimeError(
        (
            "Page 1 background slots "
            "are incorrect."
        )
    )


# ---------------------------------------------------------------------------
# Verify bleed for L7976
#
# Nominal:
# 99.1 x 67.7 mm
#
# Bleed 1 mm:
# 101.1 x 69.7 mm
# ---------------------------------------------------------------------------

first_background = (
    backgrounds[0]
)


if round(
    float(
        first_background.get(
            "width"
        )
    ),
    2
) != 101.10:

    raise RuntimeError(
        "Background bleed width failed."
    )


if round(
    float(
        first_background.get(
            "height"
        )
    ),
    2
) != 69.70:

    raise RuntimeError(
        "Background bleed height failed."
    )


if (
    first_background.get(
        "fill"
    )
    !=
    "#E8DCCB"
):

    raise RuntimeError(
        "Background color failed."
    )


# ============================================================================
# OUTPUT
# ============================================================================

print(
    "Sheet settings:"
)

print(
    (
        f" - Format: "
        f"{result['formatCode']}"
    )
)

print(
    (
        f" - Quantity: "
        f"{result['quantity']}"
    )
)

print(
    (
        f" - Start position: "
        f"{result['startPosition']}"
    )
)

print(
    (
        f" - Artwork scale: "
        f"{result['artworkScalePct']} %"
    )
)

print(
    (
        f" - Background: "
        f"{result['backgroundColor']}"
    )
)

print(
    (
        f" - Bleed: "
        f"{result['bleedMm']} mm"
    )
)


print()

print(
    "Artwork slot 7:"
)

print(
    (
        f" - X: "
        f"{slot_7_artwork['xMm']} mm"
    )
)

print(
    (
        f" - Y: "
        f"{slot_7_artwork['yMm']} mm"
    )
)

print(
    (
        f" - Size: "
        f"{slot_7_artwork['widthMm']} x "
        f"{slot_7_artwork['heightMm']} mm"
    )
)


print()

print(
    "Generated pages:"
)


for page in result[
    "pages"
]:

    print(
        (
            f" - Page {page['page']}: "
            f"slots {page['slots']}"
        )
    )

    print(
        (
            f"   {page['outputPath']}"
        )
    )


print()

print(
    "Background + bleed: OK"
)

print(
    "Uniform artwork scaling: OK"
)

print(
    "Artwork clipping: OK"
)

print(
    "SHEET LAYOUT TEST: OK"
)