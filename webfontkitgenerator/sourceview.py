# Copyright 2020 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, GObject, Gtk, GtkSource


class SourceView(GtkSource.View):
    __gtype_name__ = 'SourceView'

    def __init__(self):
        super().__init__()

        self.props.show_line_numbers = True
        self.props.monospace = True
        self.props.editable = False
        self.props.wrap_mode = Gtk.WrapMode.WORD_CHAR
        self.props.hexpand = True

        self._language = ''
        self._lm = GtkSource.LanguageManager()

        self.text_buffer = self.get_buffer()
        self.text_buffer.set_highlight_matching_brackets(False)

        ssm = GtkSource.StyleSchemeManager()
        self._adwaita = ssm.get_scheme('Adwaita')
        self._adwaita_dark = ssm.get_scheme('Adwaita-dark')

        style_manager = Adw.StyleManager.get_default()
        style_manager.connect('notify::dark', self._on_dark_style)
        self._on_dark_style(style_manager)

    @GObject.Property(type=str)
    def language(self):
        return self._language

    @language.setter
    def language(self, value):
        self._language = value
        language = self._lm.get_language(value)
        self.text_buffer.set_language(language)

    def set_text(self, text):
        self.text_buffer.set_text(text)

    def _on_dark_style(self, style_manager, *args):
        if style_manager.props.dark:
            self.text_buffer.set_style_scheme(self._adwaita_dark)
        else:
            self.text_buffer.set_style_scheme(self._adwaita)
