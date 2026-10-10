import json
from pathlib import Path


# ============================================================================
# MAAH LABEL RENDERER
# MAPPING STORE
#
# Version: 1.0.0
#
# Responsibilities:
# - Load mappings.json
# - Save mappings.json
# - Read mapping for one SVG template
# - Store mapping for one SVG template
# - Remove mapping for one SVG template
#
# Mapping direction:
#
# SVG ID -> JSON path
#
# Example:
#
# field_product_name -> product.labelName
#
# This module does NOT validate whether:
# - JSON fields actually exist
# - SVG IDs actually exist
#
# That belongs to validator.py.
# ============================================================================


DEFAULT_MAPPING_PATH = (
    Path(__file__).with_name(
        "mappings.json"
    )
)


SCHEMA_VERSION = "1.0"


# ============================================================================
# TEMPLATE KEY
# ============================================================================

def get_template_key(
    template_path
):
    """
    Return the filename used as the persistent mapping key.

    Example:

    C:/templates/front_default.svg

    becomes:

    front_default.svg
    """

    if template_path is None:

        raise ValueError(
            "Template path is required."
        )


    template_text = str(
        template_path
    ).strip()


    if not template_text:

        raise ValueError(
            "Template path cannot be empty."
        )


    template_name = Path(
        template_text
    ).name


    if not template_name:

        raise ValueError(
            "Unable to determine template filename."
        )


    return template_name


# ============================================================================
# EMPTY STORE
# ============================================================================

def create_empty_mapping_store():
    """
    Return a valid empty mapping store.
    """

    return {
        "schemaVersion":
            SCHEMA_VERSION,

        "templates":
            {}
    }


# ============================================================================
# VALIDATE MAPPING
# ============================================================================

def validate_mapping(
    mapping
):
    """
    Validate the basic structure of one template mapping.

    Expected:

    {
        "field_product_name": "product.labelName",
        "field_net_weight": "product.netWeightText"
    }
    """

    if not isinstance(
        mapping,
        dict
    ):

        raise ValueError(
            "Template mapping must be an object."
        )


    for svg_id, json_path in mapping.items():

        if not isinstance(
            svg_id,
            str
        ) or not svg_id.strip():

            raise ValueError(
                "SVG mapping IDs must be non-empty strings."
            )


        if not isinstance(
            json_path,
            str
        ) or not json_path.strip():

            raise ValueError(
                (
                    "JSON mapping paths must be "
                    "non-empty strings."
                )
            )


    return True


# ============================================================================
# VALIDATE STORE
# ============================================================================

def validate_mapping_store(
    store
):
    """
    Validate mappings.json structure.
    """

    if not isinstance(
        store,
        dict
    ):

        raise ValueError(
            "Mapping store root must be an object."
        )


    schema_version = store.get(
        "schemaVersion"
    )


    if schema_version != SCHEMA_VERSION:

        raise ValueError(
            (
                "Unsupported mappings.json schemaVersion: "
                f"{schema_version}"
            )
        )


    templates = store.get(
        "templates"
    )


    if not isinstance(
        templates,
        dict
    ):

        raise ValueError(
            (
                "mappings.json must contain "
                "a 'templates' object."
            )
        )


    for template_name, mapping in templates.items():

        if not isinstance(
            template_name,
            str
        ) or not template_name.strip():

            raise ValueError(
                "Template mapping key cannot be empty."
            )


        validate_mapping(
            mapping
        )


    return True


# ============================================================================
# LOAD
# ============================================================================

def load_mapping_store(
    file_path=None
):
    """
    Load and validate mappings.json.
    """

    path = (
        Path(file_path)

        if file_path

        else DEFAULT_MAPPING_PATH
    )


    if not path.exists():

        raise FileNotFoundError(
            f"Mapping file not found: {path}"
        )


    try:

        with path.open(
            "r",
            encoding="utf-8"
        ) as file:

            store = json.load(
                file
            )


    except json.JSONDecodeError as error:

        raise ValueError(
            (
                "Invalid mappings.json.\n"
                f"Line {error.lineno}, "
                f"column {error.colno}: "
                f"{error.msg}"
            )
        ) from error


    validate_mapping_store(
        store
    )


    return store


# ============================================================================
# SAVE
# ============================================================================

def save_mapping_store(
    store,
    file_path=None
):
    """
    Validate and save the complete mapping store.
    """

    validate_mapping_store(
        store
    )


    path = (
        Path(file_path)

        if file_path

        else DEFAULT_MAPPING_PATH
    )


    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    with path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            store,
            file,
            indent=2,
            ensure_ascii=False
        )


        file.write(
            "\n"
        )


    return path


# ============================================================================
# GET TEMPLATE MAPPING
# ============================================================================

def get_template_mapping(
    store,
    template_path
):
    """
    Return the mapping stored for one SVG template.

    If no mapping exists, return an empty dictionary.
    """

    validate_mapping_store(
        store
    )


    template_key = get_template_key(
        template_path
    )


    mapping = (
        store["templates"]
        .get(
            template_key,
            {}
        )
    )


    return dict(
        mapping
    )


# ============================================================================
# SET TEMPLATE MAPPING
# ============================================================================

def set_template_mapping(
    store,
    template_path,
    mapping
):
    """
    Add or replace the mapping for one template.

    The supplied store is updated and also returned.
    """

    validate_mapping_store(
        store
    )


    validate_mapping(
        mapping
    )


    template_key = get_template_key(
        template_path
    )


    clean_mapping = {}


    for svg_id, json_path in mapping.items():

        clean_mapping[
            svg_id.strip()
        ] = (
            json_path.strip()
        )


    store[
        "templates"
    ][
        template_key
    ] = clean_mapping


    return store


# ============================================================================
# REMOVE TEMPLATE MAPPING
# ============================================================================

def remove_template_mapping(
    store,
    template_path
):
    """
    Remove a template mapping.

    Returns True if something was removed.
    Returns False if the template had no mapping.
    """

    validate_mapping_store(
        store
    )


    template_key = get_template_key(
        template_path
    )


    templates = store[
        "templates"
    ]


    if template_key not in templates:

        return False


    del templates[
        template_key
    ]


    return True