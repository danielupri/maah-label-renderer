from label_formats import (
    load_label_formats,
    list_active_formats,
    get_label_format,
    get_effective_geometry,
    get_slot_origin_mm,
    build_page_slot_plan,
    calculate_page_count
)


# ============================================================================
# LOAD
# ============================================================================

config = load_label_formats()


active_formats = list_active_formats(
    config
)


if len(
    active_formats
) != 2:

    raise RuntimeError(
        (
            "Expected exactly 2 "
            "active V1 formats."
        )
    )


# ============================================================================
# L7976
# ============================================================================

l7976 = get_label_format(
    config,
    "L7976"
)


if (
    l7976[
        "labelsPerSheet"
    ]
    != 8
):

    raise RuntimeError(
        "L7976 labelsPerSheet test failed."
    )


# ---------------------------------------------------------------------------
# SLOT 1
# ---------------------------------------------------------------------------

slot_1 = get_slot_origin_mm(
    l7976,
    1
)


if round(
    slot_1[
        "xMm"
    ],
    2
) != 5.90:

    raise RuntimeError(
        "L7976 slot 1 X failed."
    )


if round(
    slot_1[
        "yMm"
    ],
    2
) != 13.10:

    raise RuntimeError(
        "L7976 slot 1 Y failed."
    )


# ---------------------------------------------------------------------------
# SLOT 2
# ---------------------------------------------------------------------------

slot_2 = get_slot_origin_mm(
    l7976,
    2
)


if round(
    slot_2[
        "xMm"
    ],
    2
) != 105.00:

    raise RuntimeError(
        "L7976 slot 2 X failed."
    )


# ---------------------------------------------------------------------------
# SLOT 8
# ---------------------------------------------------------------------------

slot_8 = get_slot_origin_mm(
    l7976,
    8
)


if (
    slot_8[
        "row"
    ]
    != 4
):

    raise RuntimeError(
        "L7976 slot 8 row failed."
    )


if (
    slot_8[
        "column"
    ]
    != 2
):

    raise RuntimeError(
        "L7976 slot 8 column failed."
    )


if round(
    slot_8[
        "xMm"
    ],
    2
) != 105.00:

    raise RuntimeError(
        "L7976 slot 8 X failed."
    )


if round(
    slot_8[
        "yMm"
    ],
    2
) != 216.20:

    raise RuntimeError(
        "L7976 slot 8 Y failed."
    )


# ============================================================================
# PAGE ALLOCATION
# ============================================================================

plan = build_page_slot_plan(
    l7976,
    quantity=10,
    start_position=7
)


expected_plan = [

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


if plan != expected_plan:

    raise RuntimeError(
        (
            "Page allocation test failed.\n"
            f"Expected: {expected_plan}\n"
            f"Actual: {plan}"
        )
    )


if calculate_page_count(
    l7976,
    quantity=10,
    start_position=7
) != 2:

    raise RuntimeError(
        "Page count test failed."
    )


# ============================================================================
# L7970 DEFAULT CALIBRATION
# ============================================================================

l7970 = get_label_format(
    config,
    "L7970"
)


geometry_7970 = get_effective_geometry(
    l7970
)


if round(
    geometry_7970[
        "effectivePitchXMm"
    ],
    2
) != 65.90:

    raise RuntimeError(
        (
            "L7970 default Pitch X "
            "calibration failed."
        )
    )


l7970_slot_2 = get_slot_origin_mm(
    l7970,
    2
)


if round(
    l7970_slot_2[
        "xMm"
    ],
    2
) != 75.65:

    raise RuntimeError(
        (
            "L7970 calibrated "
            "slot 2 X failed."
        )
    )


# ============================================================================
# GUI-LIKE OVERRIDE TEST
# ============================================================================

OVERRIDES = {

    "offsetXmm":
        -0.5,

    "offsetYmm":
        0.25,

    "pitchXAdjustMm":
        2.7,

    "pitchYAdjustMm":
        0.1

}


override_geometry = (
    get_effective_geometry(
        l7970,
        OVERRIDES
    )
)


if round(
    override_geometry[
        "effectiveMarginLeftMm"
    ],
    2
) != 9.25:

    raise RuntimeError(
        "Offset X override failed."
    )


if round(
    override_geometry[
        "effectiveMarginTopMm"
    ],
    2
) != 13.15:

    raise RuntimeError(
        "Offset Y override failed."
    )


if round(
    override_geometry[
        "effectivePitchXMm"
    ],
    2
) != 66.20:

    raise RuntimeError(
        "Pitch X override failed."
    )


if round(
    override_geometry[
        "effectivePitchYMm"
    ],
    2
) != 34.00:

    raise RuntimeError(
        "Pitch Y override failed."
    )


override_slot_2 = get_slot_origin_mm(
    l7970,
    2,
    OVERRIDES
)


if round(
    override_slot_2[
        "xMm"
    ],
    2
) != 75.45:

    raise RuntimeError(
        (
            "Override slot position "
            "test failed."
        )
    )


# ============================================================================
# VERIFY DEFAULT WAS NOT MODIFIED
# ============================================================================

if (
    l7970[
        "offsetXmm"
    ]
    != 0.0
):

    raise RuntimeError(
        (
            "Calibration overrides "
            "modified the original format."
        )
    )


if (
    l7970[
        "pitchXAdjustMm"
    ]
    != 2.4
):

    raise RuntimeError(
        (
            "Calibration overrides "
            "modified the original "
            "Pitch X adjustment."
        )
    )


# ============================================================================
# OUTPUT
# ============================================================================

print(
    "Active formats:"
)


for item in active_formats:

    print(
        (
            f" - {item['formatCode']}: "
            f"{item['labelWidthMm']} x "
            f"{item['labelHeightMm']} mm "
            f"({item['labelsPerSheet']} / sheet)"
        )
    )


print()

print(
    "L7976:"
)

print(
    (
        f" - Slot 1: "
        f"X={slot_1['xMm']} "
        f"Y={slot_1['yMm']}"
    )
)

print(
    (
        f" - Slot 8: "
        f"X={slot_8['xMm']} "
        f"Y={slot_8['yMm']}"
    )
)

print(
    (
        f" - Page plan: "
        f"{plan}"
    )
)


print()

print(
    "L7970 default calibration:"
)

print(
    (
        " - Effective Pitch X: "
        f"{geometry_7970['effectivePitchXMm']} mm"
    )
)

print(
    (
        " - Slot 2 X: "
        f"{l7970_slot_2['xMm']} mm"
    )
)


print()

print(
    "Override test:"
)

print(
    (
        " - Margin Left: "
        f"{override_geometry['effectiveMarginLeftMm']} mm"
    )
)

print(
    (
        " - Margin Top: "
        f"{override_geometry['effectiveMarginTopMm']} mm"
    )
)

print(
    (
        " - Pitch X: "
        f"{override_geometry['effectivePitchXMm']} mm"
    )
)

print(
    (
        " - Pitch Y: "
        f"{override_geometry['effectivePitchYMm']} mm"
    )
)


print()

print(
    "Original format unchanged: OK"
)

print(
    "LABEL FORMATS TEST: OK"
)