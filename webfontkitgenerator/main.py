# Copyright 2020 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import gi

gi.require_version('Gdk', '4.0')
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('GtkSource', '5')
gi.require_version('Soup', '3.0')

from gettext import gettext as _
from gi.repository import Adw, Gdk, Gio, GLib, GObject, Gtk

from webfontkitgenerator.window import Window


class Application(Adw.Application):
    def __init__(self, version):
        super().__init__(application_id='com.rafaelmardojai.WebfontKitGenerator',
                         flags=Gio.ApplicationFlags.HANDLES_OPEN)
        GLib.set_application_name(_('Webfont Kit Generator'))

        self.version = version
        self.window = None

        self.setup_actions()

    def do_startup(self):
        Adw.Application.do_startup(self)

    def do_activate(self):
        self.window = self.props.active_window
        if not self.window:
            self.window = Window(application=self)
        self.window.present()

    def do_open(self, files, _n_files, _hint):
        # Activate window first
        self.activate()
        # Load fonts
        self.window.load_fonts(files)

    def setup_actions(self):
        about = Gio.SimpleAction.new('about', None)
        about.connect('activate', self._on_about)
        self.add_action(about)

        self.set_accels_for_action('win.open', ['<Ctl>o'])
        self.set_accels_for_action('win.set-outpath', ['<Ctl>d'])
        self.set_accels_for_action('win.generate', ['<Ctl>Return'])
        self.set_accels_for_action('win.back', ['Escape'])


    def _on_about(self, _action, _param):
        dialog = Gtk.Builder.new_from_resource(
            '/com/rafaelmardojai/WebfontKitGenerator/about.ui'
        ).get_object('about')
        dialog.set_version(self.version)
        dialog.set_transient_for(self.window)
        dialog.set_modal(True)
        dialog.present()
 

def main(version):
    app = Application(version)
    return app.run(sys.argv)
