# Copyright 2020 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
from collections.abc import Sequence
from gettext import gettext as _

import gi

try:
    gi.require_version('Gdk', '4.0')
    gi.require_version('Gtk', '4.0')
    gi.require_version('Adw', '1')
    gi.require_version('GtkSource', '5')
    gi.require_version('Soup', '3.0')
    from gi.repository import Adw, Gio, GLib
except ImportError or ValueError as exc:
    print('Error: GIR dependencies not met.', exc)
    exit()

try:
    import fontTools  # noqa
    import brotli  # noqa
except ModuleNotFoundError as exc:
    print('Error: Python dependencies not met.', exc)
    exit()

from webfontkitgenerator.window import Window


class Application(Adw.Application):
    def __init__(self, version: str):
        super().__init__(
            application_id='com.rafaelmardojai.WebfontKitGenerator',
            flags=Gio.ApplicationFlags.HANDLES_OPEN,
        )
        GLib.set_application_name(_('Webfont Bundler'))

        self.version = version
        self.window: Window | None = None

        self.setup_actions()

    def do_startup(self):
        Adw.Application.do_startup(self)

    def do_activate(self):
        self.window = self.props.active_window  # type: ignore
        if not self.window:
            self.window = Window(application=self)
        self.window.present()

    def do_open(self, files: Sequence[Gio.File], _n_files, _hint):
        # Activate window first
        self.activate()
        # Load fonts
        if self.window:
            self.window.load_fonts(files)

    def setup_actions(self):
        about = Gio.SimpleAction.new('about', None)
        about.connect('activate', self._on_about)
        self.add_action(about)

        self.set_accels_for_action('win.open', ['<Ctl>o'])
        self.set_accels_for_action('win.google', ['<Ctl>g'])
        self.set_accels_for_action('win.set-dir', ['<Ctl>d'])
        self.set_accels_for_action('win.generate', ['<Ctl>Return'])
        self.set_accels_for_action('win.back', ['Escape'])

    def _on_about(self, _action, _param):
        dialog = Adw.AboutDialog.new_from_appdata(
            '/com/rafaelmardojai/WebfontKitGenerator/appdata.xml',
            str(self.version),
        )
        dialog.props.translator_credits = _("translator-credits")
        dialog.present(self.window)


def main(version):
    app = Application(version)
    return app.run(sys.argv)
