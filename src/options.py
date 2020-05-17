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

    #appstack = Gtk.Template.Child()

    # Fonts format check buttons
    format_woff2 = Gtk.Template.Child()
    format_woff = Gtk.Template.Child()

    # Subsetting
    subsetting = Gtk.Template.Child()

    # CSS
    css_out = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.settings = Gio.Settings.new('com.rafaelmardojai.WebfontKitGenerator')

        self.setup_combos()
        self.load_saved()

    def setup_combos(self):

        subsetting_model = Gio.ListStore.new(Handy.ValueObject)
        subsetting_model.insert(0, Handy.ValueObject.new(_('Western languages')))
        subsetting_model.insert(1, Handy.ValueObject.new(_('Disabled')))
        subsetting_model.insert(2, Handy.ValueObject.new(_('Custom')))
        self.subsetting.bind_name_model(subsetting_model, Handy.ValueObject.dup_string)

        css_out_model = Gio.ListStore.new(Handy.ValueObject)
        css_out_model.insert(0, Handy.ValueObject.new(_('File per font family')))
        css_out_model.insert(1, Handy.ValueObject.new(_('Single file')))
        self.css_out.bind_name_model(css_out_model, Handy.ValueObject.dup_string)

    def load_saved(self):
        toogle_buttons = [
            [self.format_woff2, 'woff2'],
            [self.format_woff, 'woff']
        ]

        combos = [
            [self.subsetting, 'subsetting'],
            [self.css_out, 'cssfile']
        ]

        for (button, name) in toogle_buttons:
            button.set_active(self.settings.get_boolean(name))
            self.settings.bind(name, button, 'active',
                               Gio.SettingsBindFlags.DEFAULT)

        for (combo, name) in combos:
            combo.set_selected_index(self.settings.get_int(name))
            self.settings.bind(name, combo, 'selected-index',
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
        return self.subsetting.get_selected_index()

    def get_css_out(self):
        return self.css_out.get_selected_index()

    def _get_custom_subsetting(self):
        pass
