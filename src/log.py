# log.py
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

from gi.repository import Gtk


class Log(Gtk.TextView):

    def __init__(self, progressbar_label, **kwargs):
        super().__init__(**kwargs)

        self.progressbar_label = progressbar_label
        self.text_buffer = self.get_buffer()

        self.set_editable(False)
        self.set_monospace(True)
        self.props.hexpand = True
        self.props.margin = 20

        Gtk.StyleContext.add_class(self.get_style_context(), 'log')

    def append(self, text, bold=False, italic=False):
        end_iter = self.text_buffer.get_end_iter()
        text = '<b>' + text + '</b>' if bold else text
        text = '<i>' + text + '</i>' if italic else text
        text = text + '\n'
        self.text_buffer.insert_markup(end_iter, text, -1)
        self.progressbar_label.set_markup(text)

    def reset(self):
        startIter, endIter = self.text_buffer.get_bounds()
        self.text_buffer.delete(startIter, endIter)
        self.progressbar_label.set_text('')
        
