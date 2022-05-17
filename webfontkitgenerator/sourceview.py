# Copyright 2020 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

from threading import Thread
from gi.repository import Gtk, GtkSource


class SourceView(GtkSource.View):
    __gtype_name__ = "SourceView"

    def __init__(self):
        super().__init__()

        self.set_show_line_numbers(True)
        self.set_monospace(True)
        self.set_editable(False)
        self.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.props.hexpand = True

        self.text_buffer = self.get_buffer()
        self.text_buffer.set_highlight_matching_brackets(False)

        ssm = GtkSource.StyleSchemeManager()
        self.adwaita = ssm.get_scheme('Adwaita')
        self.adwaita_dark = ssm.get_scheme('Adwaita-dark')

    def set_language(self, language):
        thread = Thread(target=self.load_language,
                        args=(language,))
        thread.daemon = True
        thread.start()

    def load_language(self, language):
        lm = GtkSource.LanguageManager()
        language = lm.get_language(language)
        self.text_buffer.set_language(language)

    def set_text(self, text):
        self.text_buffer.set_text(text)

    def set_dark_scheme(self, state):
        if state:
            self.text_buffer.set_style_scheme(self.adwaita_dark)
        else:
            self.text_buffer.set_style_scheme(self.adwaita)
