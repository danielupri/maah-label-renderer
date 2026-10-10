from pathlib import Path

from template_settings_store import (
    load_template_settings_store,
    save_template_settings_store,
    get_template_settings,
    set_template_settings
)


BASE_DIR = Path(
    __file__
).resolve().parent


SETTINGS_FILE = (
    BASE_DIR
    /
    "template_settings.json"
)


TEST_TEMPLATE = (
    BASE_DIR
    /
    "templates"
    /
    "test_artwork.svg"
)


store = load_template_settings_store(
    SETTINGS_FILE
)


print(
    "Before:"
)

print(
    get_template_settings(
        store,
        TEST_TEMPLATE
    )
)


set_template_settings(
    store,
    TEST_TEMPLATE,
    {
        "artworkScalePct": 92.0,
        "backgroundColor": "#E8DCCB",
        "bleedMm": 1.5
    }
)


save_template_settings_store(
    store,
    SETTINGS_FILE
)


reloaded_store = (
    load_template_settings_store(
        SETTINGS_FILE
    )
)


print()

print(
    "After:"
)

print(
    get_template_settings(
        reloaded_store,
        TEST_TEMPLATE
    )
)