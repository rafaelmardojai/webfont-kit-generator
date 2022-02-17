# Copyright 2020 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk


class Log(Gtk.TextView):
    __gtype_name__ = "Log"

    def __init__(self):
        super().__init__()

        self.text_buffer = self.get_buffer()

        self.set_editable(False)
        self.set_monospace(True)
        self.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.props.hexpand = True

        self.get_style_context().add_class('log')

    def append(self, text, bold=False, italic=False):
        end_iter = self.text_buffer.get_end_iter()
        text = f'<b>{text}</b>' if bold else text
        text = f'<i>{text}</i>' if italic else text
        text = text + '\n'
        self.text_buffer.insert_markup(end_iter, text, -1)

    def reset(self):
        startIter, endIter = self.text_buffer.get_bounds()
        self.text_buffer.delete(startIter, endIter)
