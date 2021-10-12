# Copyright 2020-2021 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

from gettext import gettext as _
from gi.repository import Adw, Gio, Gtk
from fontTools.subset import parse_unicodes


@Gtk.Template(resource_path='/com/rafaelmardojai/WebfontKitGenerator/options.ui')
class Options(Gtk.Box):
    __gtype_name__ = 'Options'

    # Fonts format
    format_woff2 = Gtk.Template.Child()
    format_woff  = Gtk.Template.Child()

    # Subsetting
    subsetting   = Gtk.Template.Child()
    latin        = Gtk.Template.Child()
    latin_ext    = Gtk.Template.Child()
    cyrillic     = Gtk.Template.Child()
    cyrillic_ext = Gtk.Template.Child()
    greek        = Gtk.Template.Child()
    greek_ext    = Gtk.Template.Child()
    vietnamese   = Gtk.Template.Child()
    devanagari   = Gtk.Template.Child()
    custom       = Gtk.Template.Child()

    # CSS
    font_display = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings.new('com.rafaelmardojai.WebfontKitGenerator')

        self.setup()
        self.load_saved()

    def setup(self):
        self.custom.connect('changed', self._validate_subsetting)

    def load_saved(self):
        self.subset_btns = [
            [self.latin,        'latin'],
            [self.latin_ext,    'latin-ext'],
            [self.cyrillic,     'cyrillic'],
            [self.cyrillic_ext, 'cyrillic-ext'],
            [self.greek,        'greek'],
            [self.greek_ext,    'greek-ext'],
            [self.vietnamese,   'vietnamese'],
            [self.devanagari,   'devanagari']
        ]
        toogle_btns = [
            [self.format_woff2, 'woff2'],
            [self.format_woff,  'woff']
        ]
        toogle_btns.extend(self.subset_btns)

        for (button, name) in toogle_btns:
            self.settings.bind(name, button, 'active',
                               Gio.SettingsBindFlags.DEFAULT)

        self.settings.bind('font-display', self.font_display, 'selected',
                           Gio.SettingsBindFlags.DEFAULT)

        self.settings.bind('subsetting', self.subsetting, 'enable-expansion',
                           Gio.SettingsBindFlags.DEFAULT)

    def get_formats(self):
        formats = []

        if self.format_woff2.get_active():
            formats.append('woff2')
        if self.format_woff.get_active():
            formats.append('woff')

        if len(formats) == 0:
            formats = ['woff2']

        return formats

    def get_subsetting(self):
        ranges = {}
        preset_ranges = {
            'latin':        'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,' +
                            'U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2212,U+2215',
            'latin-ext':    'U+0100-024F,U+0259,U+1E00-1EFF,U+20A0-20CF,U+2C60-2C7F,' +
                            'U+A720-A7FF',
            'cyrillic':     'U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116',
            'cyrillic-ext': 'U+0460-052F,U+1C80-1C88,U+20B4,U+2DE0-2DFF,' +
                            'U+A640-A69F,U+FE2E-FE2F',
            'greek':        'U+0370-03FF',
            'greek-ext':    'U+1F00-1FFF',
            'vietnamese':   'U+0102-0103,U+0110-0111,U+1EA0-1EF9,U+20AB',
            'devanagari':   'U+0900-097F,U+1CD0-1CF6,U+1CF8-1CF9,U+200B-200D,' +
                            'U+20A8,U+20B9,U+25CC,U+A830-A839,U+A8E0-A8FB'
        }

        if not self.subsetting.get_enable_expansion():
            return None

        for (button, name) in self.subset_btns:
            if button.get_active():
                ranges[name] = preset_ranges[name]

        try:
            if parse_unicodes(self.custom.get_text()):
                ranges['custom'] = self.custom.get_text()
        except Exception:
            pass

        if len(ranges) == 0:
            return None
        return ranges

    def get_font_display(self):
        return self.font_display.get_selected()

    def _validate_subsetting(self, _entry):
        try:
            parse_unicodes(self.custom.get_text())
            if self.custom.get_style_context().has_class('error'):
                self.custom.get_style_context().remove_class('error')
        except Exception:
            if not self.custom.get_style_context().has_class('error'):
                self.custom.get_style_context().add_class('error')
