from pathlib import Path

from inkscape_exporter import (
    find_inkscape,
    export_svg_to_pdf
)


# ============================================================================
# CONFIG
#
# This is the page generated during Step 09.
# ============================================================================

SVG_FILE = Path(
    "output/test_artwork_rendered__L7976__page_01.svg"
)


# ============================================================================
# FIND INKSCAPE
# ============================================================================

inkscape = find_inkscape()


if not inkscape.exists():

    raise RuntimeError(
        "Inkscape detection failed."
    )


# ============================================================================
# EXPORT
# ============================================================================

result = export_svg_to_pdf(
    SVG_FILE
)


# ============================================================================
# VERIFY
# ============================================================================

pdf_path = result[
    "pdfPath"
]


if not pdf_path.exists():

    raise RuntimeError(
        "PDF file does not exist."
    )


if pdf_path.suffix.lower() != ".pdf":

    raise RuntimeError(
        "Generated file is not a PDF."
    )


if pdf_path.stat().st_size <= 0:

    raise RuntimeError(
        "Generated PDF is empty."
    )


# ============================================================================
# OUTPUT
# ============================================================================

print(
    "Inkscape:"
)

print(
    f" - {inkscape}"
)


print()

print(
    "Input SVG:"
)

print(
    f" - {result['svgPath']}"
)


print()

print(
    "Output PDF:"
)

print(
    f" - {result['pdfPath']}"
)

print(
    (
        f" - Bytes: "
        f"{result['bytes']}"
    )
)


print()

print(
    "INKSCAPE EXPORT TEST: OK"
)