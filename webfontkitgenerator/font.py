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

    def __init__(self, font_data):
        super().__init__()

        self.set_title(font_data['name'])
        subtitle = ' / '.join((
            font_data['family'], font_data['style'], font_data['weight']
        ))
        self.set_subtitle(subtitle)

        btn_remove = Gtk.Button(valign=Gtk.Align.CENTER)
        btn_remove.set_icon_name('webfontkitgenerator-remove-symbolic')
        btn_remove.add_css_class('flat')
        btn_remove.add_css_class('circular')
        btn_remove.connect('clicked', self.remove_font)
        self.add_suffix(btn_remove) 
    
    def remove_font(self, _widget):
        self.activate_action('win.remove-font', GLib.Variant.new_uint32(self.get_index()))

