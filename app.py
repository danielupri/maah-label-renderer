import json
import re
import sys
from pathlib import Path
import tkinter as tk
from tkinter import (
    ttk,
    filedialog,
    messagebox,
    colorchooser
)

from json_loader import (
    load_json,
    get_json_paths,
    get_value_by_path
)

from svg_loader import (
    load_svg,
    get_dynamic_text_ids,
    validate_square_artwork
)

from mapping_store import (
    load_mapping_store,
    get_template_mapping,
    set_template_mapping,
    save_mapping_store
)

from template_settings_store import (
    get_factory_artwork_defaults,
    load_template_settings_store,
    save_template_settings_store,
    get_global_settings,
    set_global_settings,
    get_template_settings,
    set_template_settings,
    remove_template_settings
)

from validator import (
    validate_render_inputs
)

from renderer import (
    render_artwork
)

from label_formats import (
    load_label_formats,
    list_active_formats,
    get_label_format,
    get_effective_geometry,
    build_page_slot_plan
)

from sheet_layout import (
    generate_sheet_svgs,
    validate_background_color,
    validate_bleed_mm,
    validate_artwork_scale_pct
)

from inkscape_exporter import (
    find_inkscape,
    export_sheet_pages_to_pdf
)


# ============================================================================
# APPLICATION BASE DIRECTORY
# ============================================================================

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent


# ============================================================================
# PATHS
# ============================================================================

CONFIG_PATH = BASE_DIR / "config.json"

LABEL_FORMATS_PATH = BASE_DIR / "label_formats.json"

MAPPINGS_PATH = BASE_DIR / "mappings.json"

TEMPLATE_SETTINGS_PATH = BASE_DIR / "template_settings.json"

ICON_PATH = BASE_DIR / "maah.ico"

INPUT_DEFAULT = BASE_DIR / "input"

TEMPLATES_DEFAULT = BASE_DIR / "templates"

OUTPUT_DEFAULT = BASE_DIR / "output"


# ============================================================================
# HELPERS
# ============================================================================

def load_app_config():

    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"config.json not found: {CONFIG_PATH}"
        )

    with CONFIG_PATH.open(
        "r",
        encoding="utf-8"
    ) as file:
        config = json.load(file)

    if not isinstance(config, dict):
        raise ValueError(
            "config.json root must be an object."
        )

    return config


def safe_filename_part(value):

    text = str(value).strip()

    text = re.sub(
        r'[<>:"/\\|?*]+',
        "_",
        text
    )

    text = text.strip(" .")

    if not text:
        raise ValueError(
            "Filename component is empty."
        )

    return text


def get_artwork_role(svg_path):

    stem = Path(svg_path).stem

    role = stem.split(
        "_",
        1
    )[0]

    return safe_filename_part(role)


# ============================================================================
# APPLICATION
# ============================================================================

class MaahLabelRenderer(tk.Tk):

    def __init__(self):

        super().__init__()

        # ====================================================================
        # WINDOW
        # ====================================================================

        self.title(
            "MAAH LABEL RENDERER"
        )

        self.set_window_icon()

        self.geometry(
            "1100x930"
        )

        self.minsize(
            980,
            790
        )

        # ====================================================================
        # DATA
        # ====================================================================

        self.app_config = (
            load_app_config()
        )

        self.label_formats_config = (
            load_label_formats(
                LABEL_FORMATS_PATH
            )
        )

        self.json_data = None
        self.json_paths = []

        self.svg_tree = None
        self.dynamic_svg_ids = []

        self.mapping_vars = {}
        self.mapping_preview_vars = {}

        # ====================================================================
        # VARIABLES
        # ====================================================================

        self.json_path_var = tk.StringVar()

        self.svg_path_var = tk.StringVar()

        self.output_folder_var = tk.StringVar(
            value=str(
                OUTPUT_DEFAULT
            )
        )

        self.format_var = tk.StringVar()

        self.format_dimensions_var = tk.StringVar(
            value=""
        )

        self.quantity_var = tk.StringVar(
            value="1"
        )

        self.start_position_var = tk.StringVar(
            value="1"
        )

        self.offset_x_var = tk.StringVar(
            value="0.0"
        )

        self.offset_y_var = tk.StringVar(
            value="0.0"
        )

        self.pitch_x_adjust_var = tk.StringVar(
            value="0.0"
        )

        self.pitch_y_adjust_var = tk.StringVar(
            value="0.0"
        )

        factory_defaults = (
            get_factory_artwork_defaults()
        )

        self.artwork_scale_var = tk.StringVar(
            value=str(
                factory_defaults[
                    "artworkScalePct"
                ]
            )
        )

        self.background_color_var = tk.StringVar(
            value=str(
                factory_defaults[
                    "backgroundColor"
                ]
            )
        )

        self.bleed_var = tk.StringVar(
            value=str(
                factory_defaults[
                    "bleedMm"
                ]
            )
        )

        self.status_var = tk.StringVar(
            value="Ready"
        )

        # ====================================================================
        # UI
        # ====================================================================

        self.build_ui()

        self.load_global_artwork_defaults()

        self.load_initial_format()


    # ========================================================================
    # WINDOW ICON
    # ========================================================================

    def set_window_icon(self):

        if not ICON_PATH.exists():
            return

        try:
            self.iconbitmap(
                default=str(
                    ICON_PATH
                )
            )

        except tk.TclError:
            pass


    # ========================================================================
    # UI
    # ========================================================================

    def build_ui(self):

        main = ttk.Frame(
            self,
            padding=16
        )

        main.pack(
            fill="both",
            expand=True
        )

        main.columnconfigure(
            0,
            weight=1
        )

        # ====================================================================
        # TITLE
        # ====================================================================

        ttk.Label(
            main,
            text="MAAH LABEL RENDERER",
            font=(
                "Segoe UI",
                16,
                "bold"
            )
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(
                0,
                12
            )
        )

        # ====================================================================
        # FILES
        # ====================================================================

        files_frame = ttk.LabelFrame(
            main,
            text="FILES",
            padding=12
        )

        files_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(
                0,
                10
            )
        )

        files_frame.columnconfigure(
            1,
            weight=1
        )

        ttk.Label(
            files_frame,
            text="JSON"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(
                0,
                10
            ),
            pady=4
        )

        ttk.Entry(
            files_frame,
            textvariable=self.json_path_var
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            pady=4
        )

        ttk.Button(
            files_frame,
            text="Browse",
            command=self.browse_json
        ).grid(
            row=0,
            column=2,
            padx=(
                10,
                0
            ),
            pady=4
        )

        ttk.Label(
            files_frame,
            text="Artwork SVG"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=(
                0,
                10
            ),
            pady=4
        )

        ttk.Entry(
            files_frame,
            textvariable=self.svg_path_var
        ).grid(
            row=1,
            column=1,
            sticky="ew",
            pady=4
        )

        ttk.Button(
            files_frame,
            text="Browse",
            command=self.browse_svg
        ).grid(
            row=1,
            column=2,
            padx=(
                10,
                0
            ),
            pady=4
        )

        ttk.Label(
            files_frame,
            text="Output Folder"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=(
                0,
                10
            ),
            pady=4
        )

        ttk.Entry(
            files_frame,
            textvariable=self.output_folder_var
        ).grid(
            row=2,
            column=1,
            sticky="ew",
            pady=4
        )

        ttk.Button(
            files_frame,
            text="Browse",
            command=self.browse_output_folder
        ).grid(
            row=2,
            column=2,
            padx=(
                10,
                0
            ),
            pady=4
        )

        # ====================================================================
        # MAPPING
        # ====================================================================

        mapping_frame = ttk.LabelFrame(
            main,
            text="MAPPING",
            padding=12
        )

        mapping_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(
                0,
                10
            )
        )

        mapping_frame.columnconfigure(
            0,
            weight=1
        )

        self.mapping_inner = ttk.Frame(
            mapping_frame
        )

        self.mapping_inner.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        self.mapping_inner.columnconfigure(
            1,
            weight=1
        )

        ttk.Label(
            self.mapping_inner,
            text=(
                "Select an Artwork SVG "
                "to detect dynamic fields."
            )
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        ttk.Button(
            mapping_frame,
            text="Save Mapping",
            command=self.save_mapping_action
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=(
                10,
                0
            )
        )

        # ====================================================================
        # PRINT LAYOUT
        # ====================================================================

        print_frame = ttk.LabelFrame(
            main,
            text="PRINT LAYOUT",
            padding=12
        )

        print_frame.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(
                0,
                10
            )
        )

        for column in range(4):
            print_frame.columnconfigure(
                column,
                weight=1
            )

        ttk.Label(
            print_frame,
            text="Format"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=4
        )

        active_formats = list_active_formats(
            self.label_formats_config
        )

        format_codes = [
            item["formatCode"]
            for item in active_formats
        ]

        format_controls = ttk.Frame(
            print_frame
        )

        format_controls.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(
                0,
                20
            ),
            pady=4
        )

        format_controls.columnconfigure(
            0,
            weight=1
        )

        self.format_combo = ttk.Combobox(
            format_controls,
            textvariable=self.format_var,
            values=format_codes,
            state="readonly"
        )

        self.format_combo.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        self.format_combo.bind(
            "<<ComboboxSelected>>",
            self.on_format_changed
        )

        ttk.Label(
            format_controls,
            textvariable=self.format_dimensions_var
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=(
                12,
                0
            )
        )

        ttk.Label(
            print_frame,
            text="Quantity"
        ).grid(
            row=0,
            column=2,
            sticky="w",
            pady=4
        )

        ttk.Entry(
            print_frame,
            textvariable=self.quantity_var
        ).grid(
            row=0,
            column=3,
            sticky="ew",
            pady=4
        )

        ttk.Label(
            print_frame,
            text="Start Position"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=4
        )

        ttk.Entry(
            print_frame,
            textvariable=self.start_position_var
        ).grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(
                0,
                20
            ),
            pady=4
        )

        ttk.Label(
            print_frame,
            text="Offset X (mm)"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=4
        )

        ttk.Entry(
            print_frame,
            textvariable=self.offset_x_var
        ).grid(
            row=2,
            column=1,
            sticky="ew",
            padx=(
                0,
                20
            ),
            pady=4
        )

        ttk.Label(
            print_frame,
            text="Offset Y (mm)"
        ).grid(
            row=2,
            column=2,
            sticky="w",
            pady=4
        )

        ttk.Entry(
            print_frame,
            textvariable=self.offset_y_var
        ).grid(
            row=2,
            column=3,
            sticky="ew",
            pady=4
        )

        ttk.Label(
            print_frame,
            text="Pitch X Adjust (mm)"
        ).grid(
            row=3,
            column=0,
            sticky="w",
            pady=4
        )

        ttk.Entry(
            print_frame,
            textvariable=self.pitch_x_adjust_var
        ).grid(
            row=3,
            column=1,
            sticky="ew",
            padx=(
                0,
                20
            ),
            pady=4
        )

        ttk.Label(
            print_frame,
            text="Pitch Y Adjust (mm)"
        ).grid(
            row=3,
            column=2,
            sticky="w",
            pady=4
        )

        ttk.Entry(
            print_frame,
            textvariable=self.pitch_y_adjust_var
        ).grid(
            row=3,
            column=3,
            sticky="ew",
            pady=4
        )

        # ====================================================================
        # ARTWORK / BACKGROUND
        # ====================================================================

        visual_frame = ttk.LabelFrame(
            main,
            text="ARTWORK / BACKGROUND",
            padding=12
        )

        visual_frame.grid(
            row=4,
            column=0,
            sticky="ew",
            pady=(
                0,
                10
            )
        )

        for column in range(4):
            visual_frame.columnconfigure(
                column,
                weight=1
            )

        ttk.Label(
            visual_frame,
            text="Artwork Scale (%)"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=4
        )

        ttk.Entry(
            visual_frame,
            textvariable=self.artwork_scale_var
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(
                0,
                20
            ),
            pady=4
        )

        ttk.Label(
            visual_frame,
            text="Background Color"
        ).grid(
            row=0,
            column=2,
            sticky="w",
            pady=4
        )

        background_controls = ttk.Frame(
            visual_frame
        )

        background_controls.grid(
            row=0,
            column=3,
            sticky="ew",
            pady=4
        )

        background_controls.columnconfigure(
            0,
            weight=1
        )

        self.background_color_entry = ttk.Entry(
            background_controls,
            textvariable=self.background_color_var
        )

        self.background_color_entry.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        self.background_color_entry.bind(
            "<KeyRelease>",
            self.on_background_color_typed
        )

        self.background_color_entry.bind(
            "<FocusOut>",
            self.on_background_color_typed
        )

        self.background_color_swatch = tk.Label(
            background_controls,
            width=3,
            height=1,
            relief="solid",
            borderwidth=1
        )

        self.background_color_swatch.grid(
            row=0,
            column=1,
            padx=(
                8,
                8
            )
        )

        ttk.Button(
            background_controls,
            text="Choose Color",
            command=self.choose_background_color
        ).grid(
            row=0,
            column=2
        )

        self.update_background_swatch()

        ttk.Label(
            visual_frame,
            text="Bleed (mm)"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=4
        )

        ttk.Entry(
            visual_frame,
            textvariable=self.bleed_var
        ).grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(
                0,
                20
            ),
            pady=4
        )

        ttk.Button(
            visual_frame,
            text="Save Artwork Defaults",
            command=self.save_artwork_defaults_action
        ).grid(
            row=1,
            column=2,
            sticky="ew",
            padx=(
                0,
                10
            ),
            pady=4
        )

        ttk.Button(
            visual_frame,
            text="Use Artwork Defaults",
            command=self.use_artwork_defaults_action
        ).grid(
            row=1,
            column=3,
            sticky="ew",
            pady=4
        )

        ttk.Button(
            visual_frame,
            text="Remove Artwork Defaults",
            command=self.remove_artwork_defaults_action
        ).grid(
            row=2,
            column=2,
            sticky="ew",
            padx=(
                0,
                10
            ),
            pady=4
        )

        ttk.Button(
            visual_frame,
            text="Use Global Defaults",
            command=self.use_global_defaults_action
        ).grid(
            row=2,
            column=3,
            sticky="ew",
            pady=4
        )

        ttk.Button(
            visual_frame,
            text="Save Global Defaults",
            command=self.save_global_defaults_action
        ).grid(
            row=3,
            column=2,
            sticky="ew",
            padx=(
                0,
                10
            ),
            pady=4
        )

        ttk.Button(
            visual_frame,
            text="Factory Defaults",
            command=self.factory_defaults_action
        ).grid(
            row=3,
            column=3,
            sticky="ew",
            pady=4
        )

        # ====================================================================
        # ACTIONS
        # ====================================================================

        actions_frame = ttk.Frame(
            main
        )

        actions_frame.grid(
            row=5,
            column=0,
            sticky="ew",
            pady=(
                4,
                10
            )
        )

        ttk.Button(
            actions_frame,
            text="Validate",
            command=self.validate_action
        ).pack(
            side="left"
        )

        ttk.Button(
            actions_frame,
            text="Generate Labels",
            command=self.generate_action
        ).pack(
            side="left",
            padx=10
        )

        # ====================================================================
        # STATUS
        # ====================================================================

        ttk.Separator(
            main,
            orient="horizontal"
        ).grid(
            row=6,
            column=0,
            sticky="ew",
            pady=(
                4,
                8
            )
        )

        ttk.Label(
            main,
            textvariable=self.status_var
        ).grid(
            row=7,
            column=0,
            sticky="w"
        )


    # ========================================================================
    # FORMAT
    # ========================================================================

    def load_initial_format(self):

        active_formats = list_active_formats(
            self.label_formats_config
        )

        if not active_formats:
            self.format_dimensions_var.set("")
            return

        codes = [
            item["formatCode"]
            for item in active_formats
        ]

        if "L7976" in codes:
            self.format_var.set("L7976")
        else:
            self.format_var.set(codes[0])

        self.apply_format_defaults()


    def on_format_changed(
        self,
        event=None
    ):

        self.apply_format_defaults()


    def apply_format_defaults(self):

        code = self.format_var.get()

        if not code:
            self.format_dimensions_var.set("")
            return

        try:

            format_data = get_label_format(
                self.label_formats_config,
                code
            )

            width_mm = float(
                format_data[
                    "labelWidthMm"
                ]
            )

            height_mm = float(
                format_data[
                    "labelHeightMm"
                ]
            )

            columns = int(
                format_data[
                    "columns"
                ]
            )

            rows = int(
                format_data[
                    "rows"
                ]
            )

            labels_per_sheet = int(
                format_data[
                    "labelsPerSheet"
                ]
            )

            self.format_dimensions_var.set(
                (
                    f"{width_mm:g} x {height_mm:g} mm"
                    f" · {columns} × {rows}"
                    f" · {labels_per_sheet}/page"
                )
            )

            self.offset_x_var.set(
                str(
                    format_data[
                        "offsetXmm"
                    ]
                )
            )

            self.offset_y_var.set(
                str(
                    format_data[
                        "offsetYmm"
                    ]
                )
            )

            self.pitch_x_adjust_var.set(
                str(
                    format_data[
                        "pitchXAdjustMm"
                    ]
                )
            )

            self.pitch_y_adjust_var.set(
                str(
                    format_data[
                        "pitchYAdjustMm"
                    ]
                )
            )

        except Exception as error:

            self.format_dimensions_var.set(
                "—"
            )

            messagebox.showerror(
                "Format Error",
                str(error)
            )


    # ========================================================================
    # VISUAL SETTINGS
    # ========================================================================

    def collect_visual_settings(self):

        artwork_scale = (
            validate_artwork_scale_pct(
                self.artwork_scale_var.get()
            )
        )

        background_color = (
            validate_background_color(
                self.background_color_var.get()
            )
        )

        bleed = (
            validate_bleed_mm(
                self.bleed_var.get()
            )
        )

        return {
            "artworkScalePct":
                artwork_scale,

            "backgroundColor":
                str(
                    background_color
                ).upper(),

            "bleedMm":
                bleed
        }


    def apply_artwork_settings(
        self,
        settings
    ):

        self.artwork_scale_var.set(
            str(
                settings[
                    "artworkScalePct"
                ]
            )
        )

        self.background_color_var.set(
            str(
                settings[
                    "backgroundColor"
                ]
            ).upper()
        )

        self.bleed_var.set(
            str(
                settings[
                    "bleedMm"
                ]
            )
        )

        self.update_background_swatch()


    # ========================================================================
    # GLOBAL DEFAULTS AT STARTUP
    # ========================================================================

    def load_global_artwork_defaults(self):

        try:

            store = (
                load_template_settings_store(
                    TEMPLATE_SETTINGS_PATH
                )
            )

            settings = (
                get_global_settings(
                    store
                )
            )

            self.apply_artwork_settings(
                settings
            )

            return "global"

        except Exception:

            factory_settings = (
                get_factory_artwork_defaults()
            )

            self.apply_artwork_settings(
                factory_settings
            )

            self.status_var.set(
                "Factory artwork defaults loaded."
            )

            return "factory"


    # ========================================================================
    # AUTOMATIC ARTWORK RESOLUTION
    # ========================================================================

    def load_artwork_defaults_for_template(
        self,
        template_path
    ):

        try:

            store = (
                load_template_settings_store(
                    TEMPLATE_SETTINGS_PATH
                )
            )

            artwork_settings = (
                get_template_settings(
                    store,
                    template_path
                )
            )

            if artwork_settings:

                self.apply_artwork_settings(
                    artwork_settings
                )

                return "artwork"

            global_settings = (
                get_global_settings(
                    store
                )
            )

            self.apply_artwork_settings(
                global_settings
            )

            return "global"

        except Exception as error:

            factory_settings = (
                get_factory_artwork_defaults()
            )

            self.apply_artwork_settings(
                factory_settings
            )

            messagebox.showwarning(
                "Artwork Defaults",
                (
                    "Saved artwork settings could not "
                    "be loaded.\n\n"
                    "Factory defaults will be used.\n\n"
                    f"{error}"
                )
            )

            return "factory"


    # ========================================================================
    # SAVE ARTWORK DEFAULTS
    # ========================================================================

    def save_artwork_defaults_action(self):

        try:

            template_path = (
                self.svg_path_var
                .get()
                .strip()
            )

            if not template_path:

                raise ValueError(
                    (
                        "Select an Artwork SVG "
                        "before saving artwork defaults."
                    )
                )

            settings = (
                self.collect_visual_settings()
            )

            store = (
                load_template_settings_store(
                    TEMPLATE_SETTINGS_PATH
                )
            )

            set_template_settings(
                store,
                template_path,
                settings
            )

            save_template_settings_store(
                store,
                TEMPLATE_SETTINGS_PATH
            )

            self.apply_artwork_settings(
                settings
            )

            self.status_var.set(
                "Artwork-specific defaults saved."
            )

            messagebox.showinfo(
                "Artwork Defaults",
                (
                    "Artwork-specific defaults saved.\n\n"
                    f"Template:\n"
                    f"{Path(template_path).name}\n\n"
                    f"Scale: "
                    f"{settings['artworkScalePct']}%\n"
                    f"Background: "
                    f"{settings['backgroundColor']}\n"
                    f"Bleed: "
                    f"{settings['bleedMm']} mm"
                )
            )

        except Exception as error:

            messagebox.showerror(
                "Artwork Defaults Error",
                str(error)
            )


    # ========================================================================
    # USE ARTWORK DEFAULTS
    # ========================================================================

    def use_artwork_defaults_action(self):

        try:

            template_path = (
                self.svg_path_var
                .get()
                .strip()
            )

            if not template_path:

                raise ValueError(
                    (
                        "Select an Artwork SVG "
                        "before loading artwork defaults."
                    )
                )

            store = (
                load_template_settings_store(
                    TEMPLATE_SETTINGS_PATH
                )
            )

            artwork_settings = (
                get_template_settings(
                    store,
                    template_path
                )
            )

            if artwork_settings:

                self.apply_artwork_settings(
                    artwork_settings
                )

                self.status_var.set(
                    "Artwork-specific defaults loaded."
                )

                return

            global_settings = (
                get_global_settings(
                    store
                )
            )

            self.apply_artwork_settings(
                global_settings
            )

            self.status_var.set(
                (
                    "No artwork-specific defaults found. "
                    "Global defaults loaded."
                )
            )

            messagebox.showinfo(
                "Artwork Defaults",
                (
                    "No artwork-specific defaults exist "
                    "for this template.\n\n"
                    "Global defaults were loaded instead."
                )
            )

        except Exception as error:

            messagebox.showerror(
                "Artwork Defaults Error",
                str(error)
            )


    # ========================================================================
    # REMOVE ARTWORK DEFAULTS
    # ========================================================================

    def remove_artwork_defaults_action(self):

        try:

            template_path = (
                self.svg_path_var
                .get()
                .strip()
            )

            if not template_path:

                raise ValueError(
                    (
                        "Select an Artwork SVG "
                        "before removing artwork defaults."
                    )
                )

            store = (
                load_template_settings_store(
                    TEMPLATE_SETTINGS_PATH
                )
            )

            artwork_settings = (
                get_template_settings(
                    store,
                    template_path
                )
            )

            if not artwork_settings:

                global_settings = (
                    get_global_settings(
                        store
                    )
                )

                self.apply_artwork_settings(
                    global_settings
                )

                self.status_var.set(
                    (
                        "No artwork-specific defaults exist. "
                        "Global defaults loaded."
                    )
                )

                messagebox.showinfo(
                    "Remove Artwork Defaults",
                    (
                        "This artwork has no "
                        "artwork-specific defaults.\n\n"
                        "Global defaults are already being used."
                    )
                )

                return

            confirmed = messagebox.askyesno(
                "Remove Artwork Defaults",
                (
                    "Remove the saved artwork-specific defaults "
                    "for this template?\n\n"
                    f"{Path(template_path).name}\n\n"
                    "This does not modify the SVG, mapping, "
                    "global defaults or other artwork templates.\n\n"
                    "After removal, this artwork will use "
                    "the current Global Defaults."
                ),
                parent=self
            )

            if not confirmed:
                return

            remove_template_settings(
                store,
                template_path
            )

            save_template_settings_store(
                store,
                TEMPLATE_SETTINGS_PATH
            )

            global_settings = (
                get_global_settings(
                    store
                )
            )

            self.apply_artwork_settings(
                global_settings
            )

            self.status_var.set(
                (
                    "Artwork-specific defaults removed. "
                    "Global defaults loaded."
                )
            )

            messagebox.showinfo(
                "Remove Artwork Defaults",
                (
                    "Artwork-specific defaults removed.\n\n"
                    f"Template:\n"
                    f"{Path(template_path).name}\n\n"
                    "This artwork now inherits "
                    "the current Global Defaults."
                )
            )

        except Exception as error:

            messagebox.showerror(
                "Remove Artwork Defaults Error",
                str(error)
            )


    # ========================================================================
    # SAVE GLOBAL DEFAULTS
    # ========================================================================

    def save_global_defaults_action(self):

        try:

            settings = (
                self.collect_visual_settings()
            )

            store = (
                load_template_settings_store(
                    TEMPLATE_SETTINGS_PATH
                )
            )

            set_global_settings(
                store,
                settings
            )

            save_template_settings_store(
                store,
                TEMPLATE_SETTINGS_PATH
            )

            self.apply_artwork_settings(
                settings
            )

            self.status_var.set(
                "Global artwork defaults saved."
            )

            messagebox.showinfo(
                "Global Defaults",
                (
                    "Global artwork defaults saved.\n\n"
                    f"Scale: "
                    f"{settings['artworkScalePct']}%\n"
                    f"Background: "
                    f"{settings['backgroundColor']}\n"
                    f"Bleed: "
                    f"{settings['bleedMm']} mm\n\n"
                    "Existing artwork-specific defaults "
                    "were not changed."
                )
            )

        except Exception as error:

            messagebox.showerror(
                "Global Defaults Error",
                str(error)
            )


    # ========================================================================
    # USE GLOBAL DEFAULTS
    # ========================================================================

    def use_global_defaults_action(self):

        try:

            store = (
                load_template_settings_store(
                    TEMPLATE_SETTINGS_PATH
                )
            )

            global_settings = (
                get_global_settings(
                    store
                )
            )

            self.apply_artwork_settings(
                global_settings
            )

            self.status_var.set(
                (
                    "Global defaults loaded "
                    "(temporary GUI values)."
                )
            )

        except Exception as error:

            messagebox.showerror(
                "Global Defaults Error",
                str(error)
            )


    # ========================================================================
    # FACTORY DEFAULTS
    # ========================================================================

    def factory_defaults_action(self):

        factory_settings = (
            get_factory_artwork_defaults()
        )

        self.apply_artwork_settings(
            factory_settings
        )

        self.status_var.set(
            (
                "Factory defaults loaded "
                "(temporary GUI values)."
            )
        )

        messagebox.showinfo(
            "Factory Defaults",
            (
                "Factory defaults loaded into the GUI.\n\n"
                "Scale: 95.0%\n"
                "Background: #FFFFFF\n"
                "Bleed: 1.0 mm\n\n"
                "Nothing has been saved."
            )
        )


    # ========================================================================
    # BACKGROUND COLOR
    # ========================================================================

    def choose_background_color(self):

        current_color = (
            self.background_color_var
            .get()
            .strip()
        )

        if not re.fullmatch(
            r"#[0-9A-Fa-f]{6}",
            current_color
        ):
            current_color = "#FFFFFF"

        rgb_value, hex_color = (
            colorchooser.askcolor(
                color=current_color,
                title="Choose Background Color",
                parent=self
            )
        )

        if hex_color is None:
            return

        self.background_color_var.set(
            hex_color.upper()
        )

        self.update_background_swatch()


    def on_background_color_typed(
        self,
        event=None
    ):

        self.update_background_swatch()


    def update_background_swatch(self):

        color = (
            self.background_color_var
            .get()
            .strip()
        )

        if re.fullmatch(
            r"#[0-9A-Fa-f]{6}",
            color
        ):
            swatch_color = color.upper()
        else:
            swatch_color = "#D9D9D9"

        self.background_color_swatch.configure(
            background=swatch_color
        )


    # ========================================================================
    # FILE BROWSERS
    # ========================================================================

    def browse_json(self):

        initial_directory = (
            INPUT_DEFAULT
            if INPUT_DEFAULT.exists()
            else BASE_DIR
        )

        path = filedialog.askopenfilename(
            title="Select MAAH Label Job JSON",
            initialdir=str(
                initial_directory
            ),
            filetypes=[
                (
                    "JSON files",
                    "*.json"
                ),
                (
                    "All files",
                    "*.*"
                )
            ]
        )

        if not path:
            return

        try:

            data = load_json(
                path
            )

            self.json_data = data

            self.json_paths = sorted(
                get_json_paths(
                    data
                )
            )

            self.json_path_var.set(
                path
            )

            self.apply_json_print_defaults()

            self.refresh_mapping_ui()

            self.status_var.set(
                (
                    "JSON loaded: "
                    f"{Path(path).name}"
                )
            )

        except Exception as error:

            messagebox.showerror(
                "JSON Error",
                str(error)
            )


    def browse_svg(self):

        initial_directory = (
            TEMPLATES_DEFAULT
            if TEMPLATES_DEFAULT.exists()
            else BASE_DIR
        )

        path = filedialog.askopenfilename(
            title="Select Artwork SVG",
            initialdir=str(
                initial_directory
            ),
            filetypes=[
                (
                    "SVG files",
                    "*.svg"
                ),
                (
                    "All files",
                    "*.*"
                )
            ]
        )

        if not path:
            return

        try:

            tree = load_svg(
                path
            )

            validate_square_artwork(
                tree
            )

            dynamic_ids = (
                get_dynamic_text_ids(
                    tree
                )
            )

            if not dynamic_ids:

                raise ValueError(
                    (
                        "Artwork contains no "
                        "dynamic field_* text objects."
                    )
                )

            self.svg_tree = tree

            self.dynamic_svg_ids = (
                dynamic_ids
            )

            self.svg_path_var.set(
                path
            )

            settings_source = (
                self.load_artwork_defaults_for_template(
                    path
                )
            )

            self.refresh_mapping_ui()

            if settings_source == "artwork":
                source_text = (
                    "artwork-specific defaults"
                )

            elif settings_source == "global":
                source_text = (
                    "global defaults"
                )

            else:
                source_text = (
                    "factory defaults"
                )

            self.status_var.set(
                (
                    f"Artwork loaded: "
                    f"{Path(path).name} "
                    f"({source_text})"
                )
            )

        except Exception as error:

            messagebox.showerror(
                "SVG Error",
                str(error)
            )


    def browse_output_folder(self):

        path = filedialog.askdirectory(
            title="Select Output Folder",
            initialdir=str(
                OUTPUT_DEFAULT
                if OUTPUT_DEFAULT.exists()
                else BASE_DIR
            )
        )

        if path:

            self.output_folder_var.set(
                path
            )


    # ========================================================================
    # JSON PRINT DEFAULTS
    # ========================================================================

    def apply_json_print_defaults(self):

        if not self.json_data:
            return

        try:

            format_code = get_value_by_path(
                self.json_data,
                "print.formatCode"
            )

            self.format_var.set(
                str(
                    format_code
                )
            )

            self.apply_format_defaults()

        except KeyError:
            pass

        try:

            quantity = get_value_by_path(
                self.json_data,
                "print.quantity"
            )

            self.quantity_var.set(
                str(
                    quantity
                )
            )

        except KeyError:
            pass

        try:

            start_position = get_value_by_path(
                self.json_data,
                "print.startPosition"
            )

            self.start_position_var.set(
                str(
                    start_position
                )
            )

        except KeyError:
            pass


    # ========================================================================
    # MAPPING UI
    # ========================================================================

    def refresh_mapping_ui(self):

        for widget in (
            self.mapping_inner.winfo_children()
        ):
            widget.destroy()

        self.mapping_vars = {}
        self.mapping_preview_vars = {}

        if not self.dynamic_svg_ids:

            ttk.Label(
                self.mapping_inner,
                text=(
                    "Select an Artwork SVG "
                    "to detect dynamic fields."
                )
            ).grid(
                row=0,
                column=0,
                sticky="w"
            )

            return

        self.mapping_inner.columnconfigure(
            0,
            weight=0
        )

        self.mapping_inner.columnconfigure(
            1,
            weight=1
        )

        self.mapping_inner.columnconfigure(
            2,
            weight=2
        )

        ttk.Label(
            self.mapping_inner,
            text="SVG ID",
            font=(
                "Segoe UI",
                9,
                "bold"
            )
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(
                0,
                20
            ),
            pady=(
                0,
                6
            )
        )

        ttk.Label(
            self.mapping_inner,
            text="JSON Field",
            font=(
                "Segoe UI",
                9,
                "bold"
            )
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=(
                0,
                20
            ),
            pady=(
                0,
                6
            )
        )

        ttk.Label(
            self.mapping_inner,
            text="Value Preview",
            font=(
                "Segoe UI",
                9,
                "bold"
            )
        ).grid(
            row=0,
            column=2,
            sticky="w",
            pady=(
                0,
                6
            )
        )

        stored_mapping = {}

        if self.svg_path_var.get():

            try:

                store = load_mapping_store(
                    MAPPINGS_PATH
                )

                stored_mapping = (
                    get_template_mapping(
                        store,
                        self.svg_path_var.get()
                    )
                )

            except Exception:
                stored_mapping = {}

        for row_index, svg_id in enumerate(
            self.dynamic_svg_ids,
            start=1
        ):

            ttk.Label(
                self.mapping_inner,
                text=svg_id
            ).grid(
                row=row_index,
                column=0,
                sticky="w",
                padx=(
                    0,
                    20
                ),
                pady=4
            )

            mapping_variable = tk.StringVar(
                value=stored_mapping.get(
                    svg_id,
                    ""
                )
            )

            self.mapping_vars[
                svg_id
            ] = mapping_variable

            combo = ttk.Combobox(
                self.mapping_inner,
                textvariable=mapping_variable,
                values=self.json_paths,
                state="readonly"
            )

            combo.grid(
                row=row_index,
                column=1,
                sticky="ew",
                padx=(
                    0,
                    20
                ),
                pady=4
            )

            preview_variable = tk.StringVar(
                value="—"
            )

            self.mapping_preview_vars[
                svg_id
            ] = preview_variable

            ttk.Label(
                self.mapping_inner,
                textvariable=preview_variable,
                wraplength=350,
                justify="left"
            ).grid(
                row=row_index,
                column=2,
                sticky="w",
                pady=4
            )

            combo.bind(
                "<<ComboboxSelected>>",
                (
                    lambda event,
                    current_svg_id=svg_id:
                    self.update_mapping_preview(
                        current_svg_id
                    )
                )
            )

            self.update_mapping_preview(
                svg_id
            )


    # ========================================================================
    # MAPPING VALUE PREVIEW
    # ========================================================================

    def update_mapping_preview(
        self,
        svg_id
    ):

        if svg_id not in self.mapping_preview_vars:
            return

        preview_variable = (
            self.mapping_preview_vars[
                svg_id
            ]
        )

        if self.json_data is None:

            preview_variable.set(
                "—"
            )

            return

        mapping_variable = (
            self.mapping_vars.get(
                svg_id
            )
        )

        if mapping_variable is None:

            preview_variable.set(
                "—"
            )

            return

        json_path = (
            mapping_variable
            .get()
            .strip()
        )

        if not json_path:

            preview_variable.set(
                "—"
            )

            return

        try:

            value = get_value_by_path(
                self.json_data,
                json_path
            )

            if value is None:

                preview_variable.set(
                    "[EMPTY]"
                )

                return

            if isinstance(
                value,
                (dict, list)
            ):

                preview_variable.set(
                    "[NOT A TEXT VALUE]"
                )

                return

            text_value = str(
                value
            ).strip()

            if not text_value:

                preview_variable.set(
                    "[EMPTY]"
                )

                return

            preview_variable.set(
                text_value
            )

        except Exception:

            preview_variable.set(
                "[FIELD NOT FOUND]"
            )


    # ========================================================================
    # MAPPING
    # ========================================================================

    def collect_mapping(self):

        mapping = {}

        for svg_id, variable in (
            self.mapping_vars.items()
        ):

            json_path = (
                variable
                .get()
                .strip()
            )

            if json_path:

                mapping[
                    svg_id
                ] = json_path

        return mapping


    def save_mapping_action(self):

        try:

            if not self.svg_path_var.get():

                raise ValueError(
                    "Select an Artwork SVG first."
                )

            if not self.mapping_vars:

                raise ValueError(
                    "No dynamic SVG fields detected."
                )

            mapping = (
                self.collect_mapping()
            )

            missing = [
                svg_id
                for svg_id in self.dynamic_svg_ids
                if svg_id not in mapping
            ]

            if missing:

                raise ValueError(
                    (
                        "All dynamic SVG fields "
                        "must be mapped.\n\n"
                        "Missing:\n"
                        +
                        "\n".join(
                            missing
                        )
                    )
                )

            store = load_mapping_store(
                MAPPINGS_PATH
            )

            set_template_mapping(
                store,
                self.svg_path_var.get(),
                mapping
            )

            save_mapping_store(
                store,
                MAPPINGS_PATH
            )

            self.status_var.set(
                "Mapping saved."
            )

            messagebox.showinfo(
                "Mapping",
                "Mapping saved successfully."
            )

        except Exception as error:

            messagebox.showerror(
                "Mapping Error",
                str(error)
            )


    # ========================================================================
    # CALIBRATION
    # ========================================================================

    def collect_calibration_overrides(self):

        try:

            return {
                "offsetXmm":
                    float(
                        self.offset_x_var.get()
                    ),

                "offsetYmm":
                    float(
                        self.offset_y_var.get()
                    ),

                "pitchXAdjustMm":
                    float(
                        self.pitch_x_adjust_var.get()
                    ),

                "pitchYAdjustMm":
                    float(
                        self.pitch_y_adjust_var.get()
                    )
            }

        except ValueError as error:

            raise ValueError(
                (
                    "Offset and Pitch Adjust "
                    "values must be numeric."
                )
            ) from error


    # ========================================================================
    # FULL VALIDATION
    # ========================================================================

    def validate_all(self):

        if self.json_data is None:

            raise ValueError(
                "Select a valid JSON file."
            )

        if self.svg_tree is None:

            raise ValueError(
                "Select a valid Artwork SVG."
            )

        validate_square_artwork(
            self.svg_tree
        )

        mapping = (
            self.collect_mapping()
        )

        render_validation = (
            validate_render_inputs(
                self.json_data,
                self.svg_tree,
                mapping
            )
        )

        format_code = (
            self.format_var
            .get()
            .strip()
        )

        format_data = (
            get_label_format(
                self.label_formats_config,
                format_code
            )
        )

        try:

            quantity = int(
                self.quantity_var.get()
            )

            start_position = int(
                self.start_position_var.get()
            )

        except ValueError as error:

            raise ValueError(
                (
                    "Quantity and Start Position "
                    "must be integers."
                )
            ) from error

        page_plan = (
            build_page_slot_plan(
                format_data,
                quantity,
                start_position
            )
        )

        calibration = (
            self.collect_calibration_overrides()
        )

        get_effective_geometry(
            format_data,
            calibration
        )

        visual_settings = (
            self.collect_visual_settings()
        )

        output_text = (
            self.output_folder_var
            .get()
            .strip()
        )

        if not output_text:

            raise ValueError(
                "Output Folder is required."
            )

        output_folder = Path(
            output_text
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        if not output_folder.is_dir():

            raise ValueError(
                "Output path is not a directory."
            )

        try:

            lot_id = get_value_by_path(
                self.json_data,
                "lot.lotId"
            )

        except KeyError as error:

            raise ValueError(
                (
                    "Required JSON field "
                    "is missing: lot.lotId"
                )
            ) from error

        try:

            label_id = get_value_by_path(
                self.json_data,
                "labelId"
            )

        except KeyError as error:

            raise ValueError(
                (
                    "Required JSON field "
                    "is missing: labelId"
                )
            ) from error

        lot_id = safe_filename_part(
            lot_id
        )

        label_id = safe_filename_part(
            label_id
        )

        configured_inkscape = (
            self.app_config
            .get(
                "inkscape",
                {}
            )
            .get(
                "executablePath",
                ""
            )
            .strip()
        )

        inkscape_path = (
            find_inkscape(
                configured_inkscape
                if configured_inkscape
                else None
            )
        )

        return {
            "mapping":
                mapping,

            "renderValidation":
                render_validation,

            "formatCode":
                format_code,

            "formatData":
                format_data,

            "quantity":
                quantity,

            "startPosition":
                start_position,

            "pagePlan":
                page_plan,

            "calibration":
                calibration,

            "artworkScalePct":
                visual_settings[
                    "artworkScalePct"
                ],

            "backgroundColor":
                visual_settings[
                    "backgroundColor"
                ],

            "bleedMm":
                visual_settings[
                    "bleedMm"
                ],

            "outputFolder":
                output_folder,

            "lotId":
                lot_id,

            "labelId":
                label_id,

            "inkscapePath":
                inkscape_path
        }


    # ========================================================================
    # VALIDATE
    # ========================================================================

    def validate_action(self):

        try:

            result = (
                self.validate_all()
            )

            self.status_var.set(
                (
                    "Validation OK - "
                    f"{len(result['pagePlan'])} "
                    "sheet(s) required."
                )
            )

            messagebox.showinfo(
                "Validation",
                (
                    "Validation successful.\n\n"
                    f"Format: "
                    f"{result['formatCode']}\n"
                    f"Quantity: "
                    f"{result['quantity']}\n"
                    f"Sheets: "
                    f"{len(result['pagePlan'])}"
                )
            )

        except Exception as error:

            self.status_var.set(
                "Validation failed."
            )

            messagebox.showerror(
                "Validation Error",
                str(error)
            )


    # ========================================================================
    # GENERATE
    # ========================================================================

    def generate_action(self):

        try:

            settings = (
                self.validate_all()
            )

            template_path = Path(
                self.svg_path_var.get()
            )

            role = get_artwork_role(
                template_path
            )

            base_name = (
                f"{settings['lotId']}"
                f"__"
                f"{settings['labelId']}"
                f"__"
                f"{role}"
            )

            rendered_artwork_path = (
                settings[
                    "outputFolder"
                ]
                /
                f"{base_name}.svg"
            )

            render_artwork(
                template_path=template_path,
                resolved_values=(
                    settings[
                        "renderValidation"
                    ][
                        "values"
                    ]
                ),
                output_path=rendered_artwork_path
            )

            sheet_result = (
                generate_sheet_svgs(
                    rendered_artwork_svg=(
                        rendered_artwork_path
                    ),
                    format_data=(
                        settings[
                            "formatData"
                        ]
                    ),
                    quantity=(
                        settings[
                            "quantity"
                        ]
                    ),
                    start_position=(
                        settings[
                            "startPosition"
                        ]
                    ),
                    output_folder=(
                        settings[
                            "outputFolder"
                        ]
                    ),
                    artwork_scale_pct=(
                        settings[
                            "artworkScalePct"
                        ]
                    ),
                    background_color=(
                        settings[
                            "backgroundColor"
                        ]
                    ),
                    bleed_mm=(
                        settings[
                            "bleedMm"
                        ]
                    ),
                    calibration_overrides=(
                        settings[
                            "calibration"
                        ]
                    )
                )
            )

            pdf_results = (
                export_sheet_pages_to_pdf(
                    pages=(
                        sheet_result[
                            "pages"
                        ]
                    ),
                    inkscape_path=(
                        settings[
                            "inkscapePath"
                        ]
                    )
                )
            )

            self.status_var.set(
                (
                    "Generation complete - "
                    f"{len(pdf_results)} "
                    "PDF page(s)."
                )
            )

            messagebox.showinfo(
                "Generation Complete",
                (
                    "Labels generated successfully.\n\n"
                    f"Artwork:\n"
                    f"{rendered_artwork_path.name}\n\n"
                    f"Sheets: "
                    f"{len(sheet_result['pages'])}\n"
                    f"PDFs: "
                    f"{len(pdf_results)}\n\n"
                    f"Output:\n"
                    f"{settings['outputFolder']}"
                )
            )

        except Exception as error:

            self.status_var.set(
                "Generation failed."
            )

            messagebox.showerror(
                "Generation Error",
                str(error)
            )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    app = MaahLabelRenderer()

    app.mainloop()