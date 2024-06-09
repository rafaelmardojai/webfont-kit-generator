# Copyright 2020 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass, field

from gi.repository import Adw, GObject, GLib, Gtk


@dataclass
class FontData:
    name: str
    family: str
    version: str
    style: str = 'normal'
    weight: str = '400'
    width: str = '100%'
    is_variable: bool = False
    local: list[str] = field(default_factory=lambda: [])

    @property
    def name_slug(self) -> str:
        return '-'.join(self.name.split()).lower()

    @property
    def family_slug(self) -> str:
        return '-'.join(self.family.split()).lower()


class Font(GObject.Object):
    """Object representing a font"""

    __gtype_name__ = 'Font'

    path: str = GObject.Property(type=str)
    data: FontData

    def __init__(self, path: str, data: FontData):
        super().__init__()

        self.path = path
        self.data = data


class FontRow(Adw.ActionRow):
    __gtype_name__ = 'FontRow'

    def __init__(self, font_data: FontData):
        super().__init__()

        self.props.title = font_data.name
        self.props.subtitle = ' / '.join(
            (
                font_data.family,
                font_data.style,
                font_data.weight.replace(' ', '-'),
                font_data.width.replace(' ', '-'),
            )
        )

        btn_remove = Gtk.Button(valign=Gtk.Align.CENTER)
        btn_remove.props.icon_name = 'webfontkitgenerator-remove-symbolic'
        btn_remove.add_css_class('flat')
        btn_remove.add_css_class('circular')
        btn_remove.connect('clicked', self.remove_font)
        self.add_suffix(btn_remove)

    def remove_font(self, _widget):
        self.activate_action(
            'win.remove-font', GLib.Variant.new_uint32(self.get_index())
        )
