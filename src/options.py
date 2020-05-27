# options.py
#
# Copyright 2020 Rafael Mardojai CM
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gettext import gettext as _
from gi.repository import GLib, GObject, Gio, Gtk, Handy
from fontTools.subset import parse_unicodes


@Gtk.Template(resource_path='/com/rafaelmardojai/WebfontKitGenerator/ui/options.ui')
class Options(Gtk.Box):
    __gtype_name__ = 'Options'

    directory_row = Gtk.Template.Child()

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
        # Setup directory file chooser button
        self.directory = Gtk.FileChooserButton.new(
            _('Select output directory'),
            Gtk.FileChooserAction.SELECT_FOLDER)
        self.directory.props.valign = Gtk.Align.CENTER
        self.directory.show_all()
        self.directory_row.add(self.directory)

        # Setup font_display combo row
        model = Gio.ListStore.new(Handy.ValueObject)
        options = [_('Disabled'), 'auto', 'block', 'swap', 'fallback', 'optional']
        for i, o in enumerate(options):
            model.insert(i, Handy.ValueObject.new(o))
        self.font_display.bind_name_model(model, Handy.ValueObject.dup_string)

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

        self.settings.bind('font-display', self.font_display, 'selected-index',
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
        dict = {}
        ranges = {
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
                dict[name] = ranges[name]

        try:
            if parse_unicodes(self.custom.get_text()):
                dict['custom'] = self.custom.get_text()
        except ValueError:
            pass

        if len(dict) == 0:
            return None
        return dict

    def get_font_display(self):
        return self.font_display.get_selected_index()
        
