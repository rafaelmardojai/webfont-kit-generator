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

from gi.repository import GObject, Gtk, Handy


class Font(GObject.Object):

    def __init__(self, filename, data, **kwargs):
        super().__init__(**kwargs)

        self.filename = filename
        self.data = data


class FontWidget(Handy.ActionRow):

    def __init__(self, font, model, **kwargs):
        super().__init__(**kwargs)

        self.model = model

        self.set_activatable(False)
        self.set_title(font.data['name'])
        subtitle = ' / '.join((
            font.data['family'], font.data['style'], font.data['weight']
        ))
        self.set_subtitle(subtitle)

        icon = Gtk.Image.new_from_icon_name('edit-delete-symbolic', Gtk.IconSize.MENU)
        btn_remove = Gtk.Button(valign=Gtk.Align.CENTER)
        btn_remove.add(icon)
        btn_remove.get_style_context().add_class('image-button')
        btn_remove.connect('clicked', self.remove_font)
        self.add(btn_remove)

        self.show_all()

    def remove_font(self, widget):
        self.model.remove(self.get_index())

