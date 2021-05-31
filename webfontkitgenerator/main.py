# Copyright 2020 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import gi

gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('Handy', '1')
gi.require_version('GtkSource', '4')

from gettext import gettext as _
from gi.repository import Gdk, Gio, GLib, GObject, Gtk, Handy

from webfontkitgenerator.actions import Actions
from webfontkitgenerator.window import Window


class Application(Gtk.Application, Actions):
    def __init__(self, version):
        super().__init__(application_id='com.rafaelmardojai.WebfontKitGenerator',
                         flags=Gio.ApplicationFlags.HANDLES_OPEN)
        GLib.set_application_name(_('Webfont Kit Generator'))

        self.version = version
        self.window = None

        Actions.__init__(self)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        Handy.init()

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

    def do_open(self, files, n_files, hint):
        # Activate window first
        self.activate()
        # Load fonts
        self.window.load_fonts(files)


def main(version):
    app = Application(version)
    return app.run(sys.argv)
