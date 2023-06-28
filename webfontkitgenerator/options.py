# Copyright 2020 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gio, Gtk
from fontTools.subset import parse_unicodes


PRESET_RANGES = {
    'latin': 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,'
    + 'U+2000-206F,U+2074,U+20AC,U+2122,U+2212,U+2215',
    'latin-ext': 'U+0100-024F,U+0259,U+1E00-1EFF,U+20A0-20CF,U+2C60-2C7F,'
    + 'U+A720-A7FF',
    'cyrillic': 'U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116',
    'cyrillic-ext': 'U+0460-052F,U+1C80-1C88,U+20B4,U+2DE0-2DFF,U+A640-A69F,'
    + 'U+FE2E-FE2F',
    'greek': 'U+0370-03FF',
    'greek-ext': 'U+1F00-1FFF',
    'vietnamese': 'U+0102-0103,U+0110-0111,U+1EA0-1EF9,U+20AB',
    'devanagari': 'U+0900-097F,U+1CD0-1CF6,U+1CF8-1CF9,U+200B-200D,U+20A8,'
    + 'U+20B9,U+25CC,U+A830-A839,U+A8E0-A8FB',
}


@Gtk.Template(
    resource_path='/com/rafaelmardojai/WebfontKitGenerator/options.ui'
)
class Options(Adw.Bin):
    __gtype_name__ = 'Options'

    # Fonts format
    woff2: Gtk.Switch = Gtk.Template.Child()
    woff: Gtk.Switch = Gtk.Template.Child()

    # Subsetting
    subsetting: Adw.ExpanderRow = Gtk.Template.Child()
    latin: Gtk.Switch = Gtk.Template.Child()
    latin_ext: Gtk.Switch = Gtk.Template.Child()
    cyrillic: Gtk.Switch = Gtk.Template.Child()
    cyrillic_ext: Gtk.Switch = Gtk.Template.Child()
    greek: Gtk.Switch = Gtk.Template.Child()
    greek_ext: Gtk.Switch = Gtk.Template.Child()
    vietnamese: Gtk.Switch = Gtk.Template.Child()
    devanagari: Gtk.Switch = Gtk.Template.Child()
    custom: Gtk.Entry = Gtk.Template.Child()

    # CSS
    font_display: Adw.ComboRow = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # GSettings object
        self.settings = Gio.Settings.new(
            'com.rafaelmardojai.WebfontKitGenerator'
        )

        self.load_saved()

    def load_saved(self):
        # Generate list of toggle names
        toggles = ['woff2', 'woff']
        toggles.extend(PRESET_RANGES.keys())  # latin, latin_ext, etc

        for name in toggles:
            toggle = getattr(
                self, name.replace('-', '_')
            )  # Get Gtk.Switch name
            self.settings.bind(
                name, toggle, 'active', Gio.SettingsBindFlags.DEFAULT
            )  # Bind toggle with its corresponding GSetting

        self.settings.bind(
            'font-display',
            self.font_display,
            'selected',
            Gio.SettingsBindFlags.DEFAULT,
        )  # Bind font-display setting to combo row

        self.settings.bind(
            'subsetting',
            self.subsetting,
            'enable-expansion',
            Gio.SettingsBindFlags.DEFAULT,
        )  # Bind subsetting setting to expander row

    def get_formats(self) -> list[str]:
        """Get list of active formats"""
        formats = []

        if self.woff2.get_active():
            formats.append('woff2')
        if self.woff.get_active():
            formats.append('woff')

        if len(formats) == 0:
            formats = ['woff2']

        return formats

    def get_subsetting(self) -> dict[str, str] | None:
        """Get a dictionary with the active subsets and its unicode ranges"""

        if not self.subsetting.props.enable_expansion:
            return None

        ranges = {}

        # Add sunset if active
        for name in PRESET_RANGES.keys():
            toggle = getattr(self, name.replace('-', '_'))
            if toggle.get_active():
                ranges[name] = PRESET_RANGES[name]

        # Add custom subset
        try:
            if parse_unicodes(self.custom.get_text()):
                ranges['custom'] = self.custom.get_text()
        except Exception:
            pass

        if len(ranges) == 0:
            return None

        return ranges

    def get_font_display(self) -> str | None:
        if self.font_display.props.selected == 0:
            return None
        return (
            self.font_display.props.selected_item.props.string
        )  # Get string from StringObject

    @Gtk.Template.Callback()
    def _validate_subsetting(self, _entry):
        try:
            parse_unicodes(self.custom.get_text())
            if self.custom.has_css_class('error'):
                self.custom.remove_css_class('error')
        except Exception:
            if not self.custom.has_css_class('error'):
                self.custom.add_css_class('error')
