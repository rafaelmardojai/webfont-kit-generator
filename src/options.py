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


@Gtk.Template(resource_path='/com/rafaelmardojai/WebfontKitGenerator/ui/options.ui')
class Options(Gtk.Box):
    __gtype_name__ = 'Options'

    # Fonts format check buttons
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

    # CSS
    font_display = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings.new('com.rafaelmardojai.WebfontKitGenerator')

        self.setup()
        self.load_saved()

    def setup(self):
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
        list = []

        if not self.subsetting.get_enable_expansion():
            return None

        for (button, name) in self.subset_btns:
            if button.get_active():
                list.append(name)

        if len(list) == 0:
            return None
            print('no hay pe ctm 2')
        return list

    def get_font_display(self):
        return self.font_display.get_selected_index()
        
