from pathlib import Path
from tempfile import TemporaryDirectory

from mapping_store import (
    create_empty_mapping_store,
    load_mapping_store,
    save_mapping_store,
    get_template_key,
    get_template_mapping,
    set_template_mapping,
    remove_template_mapping
)


# ============================================================================
# TEST DATA
# ============================================================================

TEMPLATE = Path(
    "templates/test_artwork.svg"
)


EXPECTED_MAPPING = {

    "field_product_name":
        "product.labelName",

    "field_frozen_status":
        "product.frozenStatus",

    "field_net_weight":
        "product.netWeightText"

}


# ============================================================================
# TEMPLATE KEY
# ============================================================================

template_key = get_template_key(
    TEMPLATE
)


if template_key != "test_artwork.svg":

    raise RuntimeError(
        "Template key test failed."
    )


# ============================================================================
# EMPTY STORE
# ============================================================================

store = create_empty_mapping_store()


if store["templates"] != {}:

    raise RuntimeError(
        "Empty mapping store test failed."
    )


# ============================================================================
# SET MAPPING
# ============================================================================

set_template_mapping(
    store,
    TEMPLATE,
    EXPECTED_MAPPING
)


loaded_mapping = get_template_mapping(
    store,
    TEMPLATE
)


if loaded_mapping != EXPECTED_MAPPING:

    raise RuntimeError(
        "Stored mapping does not match expected mapping."
    )


# ============================================================================
# SAVE + RELOAD
#
# Use a temporary directory so the real mappings.json
# is not modified by this test.
# ============================================================================

with TemporaryDirectory() as temp_directory:

    test_file = (
        Path(temp_directory)
        /
        "mappings.json"
    )


    save_mapping_store(
        store,
        test_file
    )


    reloaded_store = load_mapping_store(
        test_file
    )


    reloaded_mapping = get_template_mapping(
        reloaded_store,
        TEMPLATE
    )


    if reloaded_mapping != EXPECTED_MAPPING:

        raise RuntimeError(
            "Reloaded mapping does not match expected mapping."
        )


# ============================================================================
# REMOVE
# ============================================================================

removed = remove_template_mapping(
    store,
    TEMPLATE
)


if removed is not True:

    raise RuntimeError(
        "Mapping removal test failed."
    )


if get_template_mapping(
    store,
    TEMPLATE
) != {}:

    raise RuntimeError(
        "Mapping still exists after removal."
    )


# ============================================================================
# OUTPUT
# ============================================================================

print(
    "Template key:"
)

print(
    f" - {template_key}"
)


print()

print(
    "Test mapping:"
)


for svg_id, json_path in (
    EXPECTED_MAPPING.items()
):

    print(
        (
            f" - {svg_id} "
            f"-> "
            f"{json_path}"
        )
    )


print()

print(
    "Save / reload: OK"
)

print(
    "Remove: OK"
)

print()

print(
    "MAPPING STORE TEST: OK"
)