# Copyright 2020 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import GObject, Gtk, Handy


class Font(GObject.Object):

    def __init__(self, path, data, **kwargs):
        super().__init__(**kwargs)

        self.path = path
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

