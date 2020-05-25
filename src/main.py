# main.py
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

import sys
import gi

gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('Handy', '1')
gi.require_version('GtkSource', '4')

from gettext import gettext as _
from gi.repository import GLib, GObject, Gdk, Gtk, Gio, Handy

from .actions import Actions
from .window import Window


class Application(Gtk.Application, Actions):
    def __init__(self):
        super().__init__(application_id='com.rafaelmardojai.WebfontKitGenerator',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        GLib.set_application_name(_('Webfont Kit Generator'))

        self.window = None

        GObject.type_register(Handy.Column)
        Actions.__init__(self)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        # Load CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_resource('/com/rafaelmardojai/WebfontKitGenerator/css/styles.css')
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def do_activate(self):
        self.window = self.props.active_window
        if not self.window:
            self.window = Window(application=self)
        self.window.present()


def main(version):
    app = Application()
    return app.run(sys.argv)
