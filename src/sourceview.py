# Copyright 2020 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later


from threading import Thread
from gi.repository import GLib, Gtk, GtkSource


class SourceView(GtkSource.View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_show_line_numbers(True)
        self.set_monospace(True)
        self.set_editable(False)
        self.set_wrap_mode(Gtk.WrapMode.CHAR)

        self.text_buffer = self.get_buffer()
        self.text_buffer.set_highlight_matching_brackets(False)

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
        self.show_all()
        
