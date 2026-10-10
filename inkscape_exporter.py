import shutil
import subprocess
from pathlib import Path


# ============================================================================
# MAAH LABEL RENDERER
# INKSCAPE EXPORTER
#
# Version: 1.0.0
#
# Responsibilities:
# - Locate Inkscape
# - Export generated SVG sheets to PDF
# - Validate generated PDF files
#
# This module knows nothing about:
# - JSON
# - mappings
# - Avery geometry
# - artwork positioning
# ============================================================================


COMMON_INKSCAPE_PATHS = [

    Path(
        r"C:\Program Files\Inkscape\bin\inkscape.exe"
    ),

    Path(
        r"C:\Program Files\Inkscape\inkscape.exe"
    )

]


# ============================================================================
# FIND INKSCAPE
# ============================================================================

def find_inkscape(
    configured_path=None
):
    """
    Locate the Inkscape executable.

    Search order:

    1. Explicit configured path
    2. System PATH
    3. Common Windows installation paths
    """

    # ------------------------------------------------------------------------
    # CONFIGURED PATH
    # ------------------------------------------------------------------------

    if configured_path:

        configured = Path(
            configured_path
        )


        if configured.exists():

            return configured


        raise FileNotFoundError(
            (
                "Configured Inkscape executable "
                f"does not exist: {configured}"
            )
        )


    # ------------------------------------------------------------------------
    # SYSTEM PATH
    # ------------------------------------------------------------------------

    path_result = shutil.which(
        "inkscape"
    )


    if path_result:

        return Path(
            path_result
        )


    # ------------------------------------------------------------------------
    # COMMON WINDOWS PATHS
    # ------------------------------------------------------------------------

    for path in COMMON_INKSCAPE_PATHS:

        if path.exists():

            return path


    raise FileNotFoundError(
        (
            "Inkscape executable was not found.\n"
            "Install Inkscape or configure "
            "inkscape.executablePath in config.json."
        )
    )


# ============================================================================
# EXPORT ONE SVG
# ============================================================================

def export_svg_to_pdf(
    svg_path,
    pdf_path=None,
    inkscape_path=None
):
    """
    Export one SVG page to PDF using Inkscape CLI.
    """

    svg_path = Path(
        svg_path
    )


    if not svg_path.exists():

        raise FileNotFoundError(
            f"SVG file not found: {svg_path}"
        )


    if svg_path.suffix.lower() != ".svg":

        raise ValueError(
            "Input file must be an SVG."
        )


    executable = find_inkscape(
        inkscape_path
    )


    if pdf_path is None:

        pdf_path = (
            svg_path.with_suffix(
                ".pdf"
            )
        )

    else:

        pdf_path = Path(
            pdf_path
        )


    pdf_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    command = [

        str(
            executable
        ),

        str(
            svg_path
        ),

        "--export-type=pdf",

        "--export-area-page",

        (
            "--export-filename="
            f"{pdf_path}"
        )

    ]


    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False
    )


    if result.returncode != 0:

        raise RuntimeError(
            (
                "Inkscape PDF export failed.\n\n"
                f"Exit code: {result.returncode}\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )
        )


    if not pdf_path.exists():

        raise RuntimeError(
            (
                "Inkscape finished without an error "
                "but the PDF was not created."
            )
        )


    if pdf_path.stat().st_size <= 0:

        raise RuntimeError(
            "Generated PDF is empty."
        )


    return {
        "svgPath":
            svg_path,

        "pdfPath":
            pdf_path,

        "filename":
            pdf_path.name,

        "bytes":
            pdf_path.stat().st_size,

        "inkscapePath":
            executable
    }


# ============================================================================
# EXPORT MULTIPLE SHEET PAGES
# ============================================================================

def export_sheet_pages_to_pdf(
    pages,
    inkscape_path=None
):
    """
    Export all pages returned by generate_sheet_svgs().

    Expected page structure:

    {
        "page": 1,
        "outputPath": Path(...)
    }
    """

    if not isinstance(
        pages,
        list
    ):

        raise ValueError(
            "Pages must be a list."
        )


    if not pages:

        raise ValueError(
            "No sheet pages were provided."
        )


    results = []


    for page in pages:

        if not isinstance(
            page,
            dict
        ):

            raise ValueError(
                "Invalid sheet page entry."
            )


        svg_path = page.get(
            "outputPath"
        )


        if not svg_path:

            raise ValueError(
                (
                    "Sheet page has no "
                    "outputPath."
                )
            )


        export_result = export_svg_to_pdf(
            svg_path=svg_path,
            inkscape_path=inkscape_path
        )


        results.append(
            {
                "page":
                    page.get(
                        "page"
                    ),

                "svgPath":
                    export_result[
                        "svgPath"
                    ],

                "pdfPath":
                    export_result[
                        "pdfPath"
                    ],

                "filename":
                    export_result[
                        "filename"
                    ],

                "bytes":
                    export_result[
                        "bytes"
                    ]
            }
        )


    return results