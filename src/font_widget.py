# font_widget.py
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

from gi.repository import GLib, GObject, Gtk, Handy
from fontTools.ttLib import TTFont

from threading import Thread


class WidgetFont(Handy.ActionRow):
    __gsignals__ = {
        'loaded': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_activatable(False)

        self.font = None
        self.filename = None
        self.data = None

        icon = Gtk.Image.new_from_icon_name('edit-delete-symbolic', Gtk.IconSize.MENU)
        btn_remove = Gtk.Button(valign=Gtk.Align.CENTER)
        btn_remove.add(icon)
        btn_remove.get_style_context().add_class('destructive-action')
        btn_remove.get_style_context().add_class('flat')
        self.add(btn_remove)
        btn_remove.connect('clicked', self.remove_font)

    def load(self, filename):
        thread = Thread(target=self.load_data,
                        args=(filename,))
        thread.daemon = True
        thread.start()

    def load_data(self, filename):
        self.filename = filename
        font = TTFont(filename, lazy=True)
        data = self._get_font_data(font['name'].getDebugName)
        font.close()

        GLib.idle_add(self.setup, data)

    def setup(self, data):
        self.data = data
        self.set_title(self.data['name'])
        subtitle = self.data['family'] + ' / ' + self.data['style'] + ' / ' + self.data['weight']
        self.set_subtitle(subtitle)

        self.emit('loaded')

    def remove_font(self, widget):
        self.get_parent().remove(self)

    def _get_font_data(self, data_src):
        data = {}
        weights = {
            'Thin':        '100',
            'Extra-light': '200',
            'Light':       '300',
            'Regular':     '400',
            'Medium':      '500',
            'Semi-bold':   '600',
            'Bold':        '700',
            'Extra-bold':  '800',
            'Black':       '900',
        }

        # Data used by UI
        data['name'] = data_src(4)
        data['version'] = data_src(5)
        data['family'] = data_src(16) if data_src(16) else data_src(1)
        data['style'] = 'normal'
        data['weight'] = '400'

        data['local'] = ['local("%s")' % data_src(4)]
        if not data_src(6) == data_src(4):
            data['local'].append('local("%s")' % data_src(6))

        ws = data_src(17) if data_src(17) else data_src(2)
        ws = ws.split()

        for s in ws:
            if s == 'Italic':
                data['style'] = 'italic'
            if s in weights:
                data['weight'] = weights[s]

        return data
