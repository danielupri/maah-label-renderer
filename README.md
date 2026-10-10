# MAAH Label Renderer

MAAH Label Renderer is a Windows desktop application for generating print-ready
Avery label sheets from structured JSON data and reusable SVG artwork templates.

## Features

- JSON-driven label generation
- Reusable SVG artwork templates
- Dynamic SVG text mapping using `field_*` IDs
- Avery A4 sheet layouts
- Printer calibration
- Artwork scaling
- Solid background colors
- Configurable bleed
- Per-artwork visual defaults
- Global defaults
- PDF generation through Inkscape
- Standalone Windows build

## Download

Normal users should download the latest Windows release from the GitHub Releases page.

Python is not required when using the Windows release.

Inkscape is required for PDF export.

## Requirements

### Windows Release

- Windows 10 or Windows 11
- Inkscape

### Development

- Python 3
- Tkinter
- PyInstaller
- Inkscape
- Git

## Basic Workflow

JSON Data
↓
SVG Artwork
↓
Field Mapping
↓
Dynamic Artwork
↓
Avery Sheet Layout
↓
PDF

## SVG Dynamic Fields

Dynamic text objects must use IDs beginning with:

`field_`

Example:

- `field_product_name`
- `field_frozen_status`
- `field_net_weight`

These IDs are mapped to JSON paths inside MAAH Label Renderer.

Example:

`field_product_name → product.labelName`

`field_net_weight → product.netWeightText`

## Documentation

See:

`MAAH_Label_Renderer_Documentation.html`

for the complete installation, architecture, SVG template, mapping,
configuration and troubleshooting documentation.

## Building From Source

Create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1