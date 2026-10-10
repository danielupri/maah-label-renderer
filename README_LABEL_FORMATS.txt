# MAAH LABEL RENDERER — LABEL FORMATS

This document explains how to add, modify, or calibrate label formats in
`label_formats.json`.

The system is designed so Avery label formats can be added or modified without
changing the Python code, as long as the structure documented here is preserved.

---

# 1. Main Configuration File

Label formats are stored in:

```text
label_formats.json
```

Example structure:

```json
{
  "schemaVersion": "1.0",
  "formats": {
    "L7976": {
      "displayName": "Avery L7976 - 99.1 x 67.7 mm",
      "pageWidthMm": 210.0,
      "pageHeightMm": 297.0,
      "labelWidthMm": 99.1,
      "labelHeightMm": 67.7,
      "columns": 2,
      "rows": 4,
      "marginLeftMm": 5.9,
      "marginTopMm": 13.1,
      "pitchXMm": 99.1,
      "pitchYMm": 67.7,
      "offsetXmm": 0.0,
      "offsetYmm": 0.0,
      "pitchXAdjustMm": 0.0,
      "pitchYAdjustMm": 0.0,
      "labelsPerSheet": 8,
      "active": true
    }
  }
}
```

---

# 2. Units

All physical dimensions are expressed in:

```text
millimeters (mm)
```

Do not use:

```text
pixels
inches
points
DPI conversions
```

The SVG artwork uses its own internal design units.

For example:

```text
512 x 512
```

inside the SVG does NOT mean:

```text
512 physical pixels
```

and it does not have a fixed conversion to millimeters.

The final physical size is determined by `label_formats.json`.

---

# 3. Format Fields

## Format Code

Example:

```json
"L7976"
```

This is the internal identifier of the label format.

It must be unique.

The GUI uses this code in the format selector:

```text
Format
[L7976 ▼]
```

---

## displayName

Example:

```json
"displayName": "Avery L7976 - 99.1 x 67.7 mm"
```

Human-readable description of the format.

It is currently informational.

---

## pageWidthMm

Physical width of the sheet.

For A4:

```json
"pageWidthMm": 210.0
```

---

## pageHeightMm

Physical height of the sheet.

For A4:

```json
"pageHeightMm": 297.0
```

---

## labelWidthMm

Physical width of each label.

Example:

```json
"labelWidthMm": 99.1
```

The GUI displays this value automatically.

---

## labelHeightMm

Physical height of each label.

Example:

```json
"labelHeightMm": 67.7
```

The GUI displays this value automatically.

For example:

```text
Format    [L7976 ▼]    99.1 x 67.7 mm
```

---

## columns

Number of label columns on the sheet.

Example:

```json
"columns": 2
```

---

## rows

Number of label rows on the sheet.

Example:

```json
"rows": 4
```

---

## labelsPerSheet

Total number of labels per physical sheet.

The following rule must always be true:

```text
labelsPerSheet = columns × rows
```

Example:

```text
2 × 4 = 8
```

Therefore:

```json
"labelsPerSheet": 8
```

If this value does not match, Python will reject the format.

---

# 4. Margins

## marginLeftMm

Distance from the left edge of the sheet to the nominal origin of the first
label.

Example:

```json
"marginLeftMm": 5.9
```

---

## marginTopMm

Distance from the top edge of the sheet to the nominal origin of the first
label.

Example:

```json
"marginTopMm": 13.1
```

---

# 5. Pitch

Pitch is NOT necessarily equal to the physical label size.

It represents the distance from the origin of one label to the origin of the
next label.

---

## pitchXMm

Horizontal distance between two consecutive label positions.

Example:

```json
"pitchXMm": 101.6
```

There may be horizontal spacing between labels even when:

```text
labelWidthMm = 99.1
```

---

## pitchYMm

Vertical distance between two consecutive rows.

Example:

```json
"pitchYMm": 67.7
```

---

# 6. Printer Calibration

Four calibration parameters are available:

```json
"offsetXmm": 0.0,
"offsetYmm": 0.0,
"pitchXAdjustMm": 0.0,
"pitchYAdjustMm": 0.0
```

These values represent the default calibration of the format.

The GUI allows the operator to override them temporarily.

---

## offsetXmm

Moves the entire print layout horizontally.

Example:

```text
+0.5 mm
```

moves all labels 0.5 mm to the right.

```text
-0.5 mm
```

moves all labels 0.5 mm to the left.

---

## offsetYmm

Moves the entire print layout vertically.

Positive value:

```text
moves downward
```

Negative value:

```text
moves upward
```

---

## pitchXAdjustMm

Corrects progressive horizontal drift between columns.

Effective geometry:

```text
Effective Pitch X =
pitchXMm + pitchXAdjustMm
```

Example:

```text
pitchXMm = 63.5
pitchXAdjustMm = 2.4

Effective Pitch X = 65.9 mm
```

---

## pitchYAdjustMm

Corrects progressive vertical drift between rows.

```text
Effective Pitch Y =
pitchYMm + pitchYAdjustMm
```

---

# 7. Position Formula Used by Python

For every label:

```text
X =
marginLeftMm
+ offsetXmm
+ column × (pitchXMm + pitchXAdjustMm)
```

```text
Y =
marginTopMm
+ offsetYmm
+ row × (pitchYMm + pitchYAdjustMm)
```

Internally:

```text
column
```

and:

```text
row
```

start at `0`.

The operator-facing slot numbers start at `1`.

Example for a two-column sheet:

```text
1  2
3  4
5  6
7  8
```

---

# 8. active

Each format contains:

```json
"active": true
```

If:

```json
"active": true
```

the format appears in the GUI.

If:

```json
"active": false
```

the format remains configured but cannot be selected in the GUI.

---

# 9. Adding a New Format

Suppose a fictional format exists:

```text
MAAH_TEST
```

with:

```text
70 x 40 mm
2 columns
6 rows
12 labels
```

Add the following object inside `"formats"`:

```json
"MAAH_TEST": {
  "displayName": "MAAH TEST - 70 x 40 mm",
  "pageWidthMm": 210.0,
  "pageHeightMm": 297.0,
  "labelWidthMm": 70.0,
  "labelHeightMm": 40.0,
  "columns": 2,
  "rows": 6,
  "marginLeftMm": 10.0,
  "marginTopMm": 10.0,
  "pitchXMm": 90.0,
  "pitchYMm": 45.0,
  "offsetXmm": 0.0,
  "offsetYmm": 0.0,
  "pitchXAdjustMm": 0.0,
  "pitchYAdjustMm": 0.0,
  "labelsPerSheet": 12,
  "active": true
}
```

IMPORTANT:

JSON objects must be separated by commas.

Example:

```json
{
  "formats": {
    "L7976": {
      ...
    },

    "MAAH_TEST": {
      ...
    }
  }
}
```

Do not place a comma after the final format object.

---

# 10. Validate label_formats.json

After any modification, run:

```powershell
python -m json.tool label_formats.json > $null
```

If the JSON syntax is valid:

```text
PowerShell returns to the prompt without displaying an error.
```

If the JSON contains a syntax error, Python will report the relevant line.

---

# 11. Test the Configuration in Python

After validating the JSON:

```powershell
python app.py
```

The new format should appear automatically in:

```text
Format
```

No modification is required in:

```text
app.py
label_formats.py
sheet_layout.py
```

as long as the existing format schema is preserved.

---

# 12. What Python Handles Automatically

`label_formats.py`:

```text
1. Loads label_formats.json
2. Validates schemaVersion
3. Validates all required fields
4. Checks columns × rows
5. Calculates physical slot positions
6. Applies Offset
7. Applies Pitch Adjust
```

`app.py`:

```text
1. Automatically detects active formats
2. Adds them to the Format dropdown
3. Displays labelWidthMm x labelHeightMm
4. Loads default calibration values
```

`sheet_layout.py`:

```text
1. Creates the physical sheet
2. Positions Avery slots
3. Generates the background
4. Applies bleed
5. Scales the artwork
6. Centers the artwork
```

---

# 13. Changes That Do NOT Require Python Modifications

The following values may be changed directly:

```text
displayName
pageWidthMm
pageHeightMm
labelWidthMm
labelHeightMm
columns
rows
marginLeftMm
marginTopMm
pitchXMm
pitchYMm
offsetXmm
offsetYmm
pitchXAdjustMm
pitchYAdjustMm
labelsPerSheet
active
```

The existing property names must remain unchanged.

---

# 14. Changes That DO Require Python Modifications

Changing the JSON structure requires code changes.

For example, changing:

```text
labelWidthMm
```

to:

```text
width
```

would require updates to:

```text
label_formats.py
sheet_layout.py
app.py
```

Do not rename existing fields without a technical reason.

Adding new concepts would also require code changes, for example:

```text
format-specific rotation
non-rectangular labels
automatic orientation
multiple page geometries inside one format
individual per-slot offsets
```

These features are outside the V1 schema.

---

# 15. Recommended Physical Calibration Process

When adding a new format:

```text
1. Enter the official manufacturer geometry
2. Set Offset X = 0
3. Set Offset Y = 0
4. Set Pitch X Adjust = 0
5. Set Pitch Y Adjust = 0
6. Generate the sheet
7. Print at 100% / Actual Size
8. Measure the physical deviation
9. Correct Offset if the complete sheet is shifted
10. Correct Pitch Adjust if the error increases progressively
```

Do not modify:

```text
margin
label size
manufacturer pitch
```

just to compensate for a printer-specific alignment error when that error can be
corrected with:

```text
offset
pitch adjustment
```

---

# 16. Geometry vs Calibration

PHYSICAL PRODUCT GEOMETRY:

```text
labelWidthMm
labelHeightMm
columns
rows
marginLeftMm
marginTopMm
pitchXMm
pitchYMm
```

These values describe the physical Avery sheet.

PRINTER CALIBRATION:

```text
offsetXmm
offsetYmm
pitchXAdjustMm
pitchYAdjustMm
```

These values correct printing behavior.

Keep these two concepts separate.

---

# 17. Artwork Scale Does NOT Belong to the Avery Format

Do not add the following values to `label_formats.json`:

```text
artworkScalePct
backgroundColor
bleedMm
```

These values belong to:

```text
config.json
```

and/or can be modified through the GUI.

The Avery format describes physical sheet geometry, not visual design decisions.

---

# 18. Compiled Application (.exe)

The distributed application uses:

```text
MAAH Label Renderer/
├── MAAH Label Renderer.exe
├── label_formats.json
├── config.json
├── mappings.json
└── ...
```

`label_formats.json` remains external to the executable.

Therefore, it can technically be modified directly at:

```text
dist\MAAH Label Renderer\label_formats.json
```

After changing it:

```text
close the application
modify the JSON
reopen the application
```

The `.exe` does not need to be rebuilt for new or modified label formats.

---

# 19. Development vs Distribution

## Development

Edit:

```text
MAAH_LABEL_RENDERER_V1\label_formats.json
```

Then run:

```powershell
python app.py
```

---

## Distributed Application

Edit:

```text
dist\MAAH Label Renderer\label_formats.json
```

Then restart:

```text
MAAH Label Renderer.exe
```

---

# 20. IMPORTANT: build.bat Behavior

`build.bat` copies:

```text
label_formats.json
```

from the source project into:

```text
dist\MAAH Label Renderer\
```

Therefore:

```text
the project's label_formats.json
```

must be treated as the master version.

If a final printer calibration is made directly in the distributed application,
copy those calibrated values back into the project's:

```text
label_formats.json
```

Otherwise, a future build may overwrite the calibrated distribution file.

---

# 21. Checklist Before Accepting a New Format

Check the following:

```text
[ ] Format code is unique

[ ] Measurements come from reliable manufacturer documentation

[ ] All physical units are in mm

[ ] pageWidthMm / pageHeightMm are correct

[ ] labelWidthMm / labelHeightMm are correct

[ ] columns is correct

[ ] rows is correct

[ ] columns × rows = labelsPerSheet

[ ] marginLeftMm is correct

[ ] marginTopMm is correct

[ ] pitchXMm is correct

[ ] pitchYMm is correct

[ ] Offset normally starts at 0

[ ] Pitch Adjust normally starts at 0

[ ] active = true

[ ] JSON passes python -m json.tool

[ ] Format appears in the GUI

[ ] GUI displays the correct label dimensions

[ ] SVG sheet generation succeeds

[ ] PDF generation succeeds

[ ] Physical print is tested at 100% / Actual Size

[ ] Calibration is applied only if necessary
```

---

# 22. Main Rule

`label_formats.json` should represent:

```text
PHYSICAL GEOMETRY
+
PRINT CALIBRATION
```

It must not become a general application configuration file.

The correct separation is:

```text
label_formats.json
→ Avery formats + physical geometry + print calibration

config.json
→ general renderer defaults

mappings.json
→ SVG IDs ↔ JSON fields

SVG
→ visual design

MAAH SYSTEM JSON
→ production data
```

Keeping this separation prevents unnecessary coupling and allows new Avery
formats to be added without changing the Python rendering engine.