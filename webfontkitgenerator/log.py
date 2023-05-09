# Copyright 2020 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk


class Log(Gtk.TextView):
    __gtype_name__ = 'Log'

    def __init__(self):
        super().__init__()

        self.text_buffer = self.get_buffer()

        self.props.editable = False
        self.props.monospace = True
        self.props.wrap_mode = Gtk.WrapMode.WORD_CHAR
        self.props.hexpand = True

        self.add_css_class('log')

    def append(self, text: str, bold: bool = False, italic: bool = False):
        """Append text to the log"""
        end_iter = self.text_buffer.get_end_iter()
        text = f'<b>{text}</b>' if bold else text
        text = f'<i>{text}</i>' if italic else text
        text = text + '\n'
        self.text_buffer.insert_markup(end_iter, text, -1)

    def reset(self):
        """Clear the log"""
        star, end = self.text_buffer.get_bounds()
        self.text_buffer.delete(star, end)
