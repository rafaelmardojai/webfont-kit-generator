# sourceview.py
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
        
