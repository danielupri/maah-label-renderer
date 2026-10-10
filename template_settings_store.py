import json
import math
import re
from pathlib import Path


# ============================================================================
# DEFAULT PATH
# ============================================================================

MODULE_DIR = Path(__file__).resolve().parent

DEFAULT_TEMPLATE_SETTINGS_PATH = (
    MODULE_DIR
    /
    "template_settings.json"
)


# ============================================================================
# CONSTANTS
# ============================================================================

SCHEMA_VERSION = "1.0"

HEX_COLOR_PATTERN = re.compile(
    r"^#[0-9A-Fa-f]{6}$"
)


FACTORY_ARTWORK_DEFAULTS = {
    "artworkScalePct": 95.0,
    "backgroundColor": "#FFFFFF",
    "bleedMm": 1.0
}


# ============================================================================
# HELPERS
# ============================================================================

def get_template_key(
    template_path
):
    """
    Return the filename used as the persistent template key.
    """

    key = Path(
        template_path
    ).name.strip()


    if not key:

        raise ValueError(
            "Template filename cannot be empty."
        )


    return key


def get_factory_artwork_defaults():
    """
    Return a copy of the immutable factory artwork defaults.
    """

    return dict(
        FACTORY_ARTWORK_DEFAULTS
    )


def create_empty_template_settings_store():
    """
    Create a new settings store using factory defaults
    as the initial global settings.
    """

    return {
        "schemaVersion": SCHEMA_VERSION,
        "global": get_factory_artwork_defaults(),
        "templates": {}
    }


def _is_number(
    value
):
    """
    Return True only for valid finite numeric values.
    """

    if isinstance(
        value,
        bool
    ):

        return False


    if not isinstance(
        value,
        (int, float)
    ):

        return False


    return math.isfinite(
        float(
            value
        )
    )


# ============================================================================
# VISUAL SETTINGS VALIDATION
# ============================================================================

def validate_visual_settings(
    settings
):
    """
    Validate one Scale / Background / Bleed settings object.
    """

    if not isinstance(
        settings,
        dict
    ):

        raise ValueError(
            "Artwork settings must be an object."
        )


    required_fields = (
        "artworkScalePct",
        "backgroundColor",
        "bleedMm"
    )


    for field_name in required_fields:

        if field_name not in settings:

            raise ValueError(
                (
                    "Artwork settings are missing "
                    f"required field: {field_name}"
                )
            )


    # ------------------------------------------------------------------------
    # ARTWORK SCALE
    # ------------------------------------------------------------------------

    artwork_scale = settings[
        "artworkScalePct"
    ]


    if not _is_number(
        artwork_scale
    ):

        raise ValueError(
            "artworkScalePct must be numeric."
        )


    if float(
        artwork_scale
    ) <= 0:

        raise ValueError(
            "artworkScalePct must be greater than 0."
        )


    # ------------------------------------------------------------------------
    # BACKGROUND COLOR
    # ------------------------------------------------------------------------

    background_color = settings[
        "backgroundColor"
    ]


    if not isinstance(
        background_color,
        str
    ):

        raise ValueError(
            "backgroundColor must be a string."
        )


    if not HEX_COLOR_PATTERN.fullmatch(
        background_color.strip()
    ):

        raise ValueError(
            (
                "backgroundColor must use "
                "#RRGGBB format."
            )
        )


    # ------------------------------------------------------------------------
    # BLEED
    # ------------------------------------------------------------------------

    bleed = settings[
        "bleedMm"
    ]


    if not _is_number(
        bleed
    ):

        raise ValueError(
            "bleedMm must be numeric."
        )


    if float(
        bleed
    ) < 0:

        raise ValueError(
            "bleedMm cannot be negative."
        )


    return True


# ============================================================================
# NORMALIZATION
# ============================================================================

def normalize_visual_settings(
    settings
):
    """
    Validate and normalize a visual settings object.
    """

    validate_visual_settings(
        settings
    )


    return {
        "artworkScalePct":
            float(
                settings[
                    "artworkScalePct"
                ]
            ),

        "backgroundColor":
            settings[
                "backgroundColor"
            ]
            .strip()
            .upper(),

        "bleedMm":
            float(
                settings[
                    "bleedMm"
                ]
            )
    }


def normalize_template_settings_store(
    store
):
    """
    Normalize the complete settings store.

    Backward compatibility:
    Older V1 stores containing only:

        schemaVersion
        templates

    are automatically given factory global defaults.
    """

    if not isinstance(
        store,
        dict
    ):

        raise ValueError(
            "Template settings store must be an object."
        )


    if store.get(
        "schemaVersion"
    ) != SCHEMA_VERSION:

        raise ValueError(
            (
                "Unsupported template settings "
                "schemaVersion."
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
            "'templates' must be an object."
        )


    global_settings = store.get(
        "global"
    )


    # ------------------------------------------------------------------------
    # BACKWARD COMPATIBILITY
    #
    # Previous version did not contain a global section.
    # ------------------------------------------------------------------------

    if global_settings is None:

        global_settings = (
            get_factory_artwork_defaults()
        )


    normalized_templates = {}


    for template_key, settings in (
        templates.items()
    ):

        if not isinstance(
            template_key,
            str
        ):

            raise ValueError(
                "Template keys must be strings."
            )


        template_key = (
            template_key.strip()
        )


        if not template_key:

            raise ValueError(
                "Template key cannot be empty."
            )


        normalized_templates[
            template_key
        ] = normalize_visual_settings(
            settings
        )


    return {
        "schemaVersion":
            SCHEMA_VERSION,

        "global":
            normalize_visual_settings(
                global_settings
            ),

        "templates":
            normalized_templates
    }


# ============================================================================
# STORE VALIDATION
# ============================================================================

def validate_template_settings_store(
    store
):
    """
    Validate the complete normalized settings store.
    """

    normalize_template_settings_store(
        store
    )


    return True


# ============================================================================
# LOAD
# ============================================================================

def load_template_settings_store(
    file_path=None
):
    """
    Load template_settings.json.

    If the file does not exist, create an in-memory store
    using factory defaults.

    Older V1 stores without a global section are automatically
    normalized without losing template-specific settings.
    """

    path = Path(
        file_path
        if file_path is not None
        else DEFAULT_TEMPLATE_SETTINGS_PATH
    )


    if not path.exists():

        return (
            create_empty_template_settings_store()
        )


    with path.open(
        "r",
        encoding="utf-8"
    ) as file:

        store = json.load(
            file
        )


    return normalize_template_settings_store(
        store
    )


# ============================================================================
# SAVE
# ============================================================================

def save_template_settings_store(
    store,
    file_path=None
):
    """
    Validate, normalize and safely save the complete settings store.
    """

    normalized_store = (
        normalize_template_settings_store(
            store
        )
    )


    path = Path(
        file_path
        if file_path is not None
        else DEFAULT_TEMPLATE_SETTINGS_PATH
    )


    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    temporary_path = path.with_suffix(
        path.suffix + ".tmp"
    )


    with temporary_path.open(
        "w",
        encoding="utf-8",
        newline="\n"
    ) as file:

        json.dump(
            normalized_store,
            file,
            indent=2,
            ensure_ascii=False
        )


        file.write(
            "\n"
        )


    temporary_path.replace(
        path
    )


# ============================================================================
# GLOBAL SETTINGS
# ============================================================================

def get_global_settings(
    store
):
    """
    Return the current user global artwork defaults.
    """

    normalized_store = (
        normalize_template_settings_store(
            store
        )
    )


    return dict(
        normalized_store[
            "global"
        ]
    )


def set_global_settings(
    store,
    settings
):
    """
    Replace the current user global artwork defaults.
    """

    normalized_store = (
        normalize_template_settings_store(
            store
        )
    )


    normalized_store[
        "global"
    ] = normalize_visual_settings(
        settings
    )


    store.clear()

    store.update(
        normalized_store
    )


    return store


# ============================================================================
# TEMPLATE SETTINGS
# ============================================================================

def get_template_settings(
    store,
    template_path
):
    """
    Return template-specific settings.

    Returns an empty dictionary when the template does not
    have an artwork-specific override.
    """

    normalized_store = (
        normalize_template_settings_store(
            store
        )
    )


    template_key = get_template_key(
        template_path
    )


    settings = (
        normalized_store[
            "templates"
        ].get(
            template_key
        )
    )


    if settings is None:

        return {}


    return dict(
        settings
    )


def set_template_settings(
    store,
    template_path,
    settings
):
    """
    Save or replace artwork-specific defaults for one SVG.
    """

    normalized_store = (
        normalize_template_settings_store(
            store
        )
    )


    template_key = get_template_key(
        template_path
    )


    normalized_store[
        "templates"
    ][
        template_key
    ] = normalize_visual_settings(
        settings
    )


    store.clear()

    store.update(
        normalized_store
    )


    return store


def remove_template_settings(
    store,
    template_path
):
    """
    Remove the artwork-specific override for one SVG.

    After removal, the SVG will inherit the current
    user global defaults.
    """

    normalized_store = (
        normalize_template_settings_store(
            store
        )
    )


    template_key = get_template_key(
        template_path
    )


    normalized_store[
        "templates"
    ].pop(
        template_key,
        None
    )


    store.clear()

    store.update(
        normalized_store
    )


    return store