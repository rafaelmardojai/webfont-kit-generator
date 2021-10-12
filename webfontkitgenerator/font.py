# Copyright 2020 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, GObject, GLib, Gtk


class Font(GObject.Object):
    __gtype_name__ = "Font"

    path = GObject.Property(type=str)

    def __init__(self, path, data):
        super().__init__()

        self.path = path
        self.data = data


class FontRow(Adw.ActionRow):
    __gtype_name__ = "FontRow"

    position = GObject.Property(type=int)

    def __init__(self):
        super().__init__()

        btn_remove = Gtk.Button(valign=Gtk.Align.CENTER)
        btn_remove.set_icon_name('edit-delete-symbolic')
        btn_remove.connect('clicked', self.remove_font)
        self.add_suffix(btn_remove)

    def set_data(self, data):
        self.set_title(data['name'])
        subtitle = ' / '.join((
            data['family'], data['style'], data['weight']
        ))
        self.set_subtitle(subtitle)
    
    def remove_font(self, _widget):
        self.activate_action('win.remove-font', GLib.Variant.new_uint32(self.position))

