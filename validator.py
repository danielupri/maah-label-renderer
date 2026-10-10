from json_loader import (
    get_value_by_path
)

from svg_loader import (
    get_dynamic_text_ids
)

from mapping_store import (
    validate_mapping
)


# ============================================================================
# MAAH LABEL RENDERER
# VALIDATOR
#
# Version: 1.0.0
#
# Responsibilities:
# - Connect JSON + SVG + mapping
# - Ensure every dynamic SVG field is mapped
# - Ensure mapped SVG IDs exist
# - Ensure mapped JSON paths exist
# - Ensure mapped values are scalar and non-empty
# - Return resolved text values ready for rendering
#
# This module does NOT modify the SVG.
# ============================================================================


# ============================================================================
# VALUE VALIDATION
# ============================================================================

def validate_mapped_value(
    json_path,
    value
):
    """
    Ensure a mapped JSON value can safely become SVG text.
    """

    if value is None:

        raise ValueError(
            (
                "Mapped JSON field has no value: "
                f"{json_path}"
            )
        )


    if isinstance(
        value,
        (dict, list)
    ):

        raise ValueError(
            (
                "Mapped JSON field must be scalar: "
                f"{json_path}"
            )
        )


    text_value = str(
        value
    ).strip()


    if not text_value:

        raise ValueError(
            (
                "Mapped JSON field is empty: "
                f"{json_path}"
            )
        )


    return text_value


# ============================================================================
# VALIDATE RENDER INPUTS
# ============================================================================

def validate_render_inputs(
    json_data,
    svg_tree,
    mapping
):
    """
    Validate JSON + SVG + mapping.

    Mapping direction:

    SVG ID -> JSON path

    Returns:

    {
        "valid": True,

        "values": {
            "field_product_name": "Chicken Curry",
            ...
        },

        "fields": [
            {
                "svgId": "...",
                "jsonPath": "...",
                "value": "..."
            }
        ]
    }
    """

    if not isinstance(
        json_data,
        dict
    ):

        raise ValueError(
            "JSON data must be a dictionary."
        )


    if svg_tree is None:

        raise ValueError(
            "SVG artwork is not loaded."
        )


    validate_mapping(
        mapping
    )


    dynamic_ids = set(
        get_dynamic_text_ids(
            svg_tree
        )
    )


    if not dynamic_ids:

        raise ValueError(
            (
                "SVG artwork contains no "
                "dynamic field_* text objects."
            )
        )


    mapped_ids = set(
        mapping.keys()
    )


    # ------------------------------------------------------------------------
    # MISSING MAPPINGS
    #
    # Every field_* object in the SVG must be mapped.
    # ------------------------------------------------------------------------

    missing_mappings = (
        dynamic_ids
        -
        mapped_ids
    )


    if missing_mappings:

        raise ValueError(
            (
                "SVG fields without mapping: "
                +
                ", ".join(
                    sorted(
                        missing_mappings
                    )
                )
            )
        )


    # ------------------------------------------------------------------------
    # UNKNOWN SVG IDS
    #
    # mappings.json may not reference field IDs
    # that do not exist in the selected artwork.
    # ------------------------------------------------------------------------

    unknown_svg_ids = (
        mapped_ids
        -
        dynamic_ids
    )


    if unknown_svg_ids:

        raise ValueError(
            (
                "Mapping references unknown SVG fields: "
                +
                ", ".join(
                    sorted(
                        unknown_svg_ids
                    )
                )
            )
        )


    # ------------------------------------------------------------------------
    # RESOLVE VALUES
    # ------------------------------------------------------------------------

    resolved_values = {}

    fields = []


    for svg_id in sorted(
        dynamic_ids
    ):

        json_path = mapping[
            svg_id
        ]


        try:

            value = get_value_by_path(
                json_data,
                json_path
            )


        except KeyError as error:

            raise ValueError(
                (
                    f"JSON field mapped to "
                    f"'{svg_id}' does not exist: "
                    f"{json_path}"
                )
            ) from error


        text_value = validate_mapped_value(
            json_path,
            value
        )


        resolved_values[
            svg_id
        ] = text_value


        fields.append(
            {
                "svgId":
                    svg_id,

                "jsonPath":
                    json_path,

                "value":
                    text_value
            }
        )


    return {
        "valid":
            True,

        "values":
            resolved_values,

        "fields":
            fields,

        "fieldCount":
            len(
                fields
            )
    }