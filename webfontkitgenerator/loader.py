# Copyright 2020 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os
import typing
from collections.abc import Sequence
from gettext import gettext as _
from urllib.parse import unquote

from fontTools.ttLib import TTFont
from gi.repository import Adw, Gio, GLib

from webfontkitgenerator.font import Font, FontData

if typing.TYPE_CHECKING:
    from webfontkitgenerator.window import Window

WEIGHTS = {
    'thin': '100',
    'extralight': '200',
    'light': '300',
    'regular': '400',
    'medium': '500',
    'semibold': '600',
    'bold': '700',
    'extrabold': '800',
    'black': '900',
}

WIDTHS = {
    'ultracondensed': '50%',
    'extracondensed': '62.5%',
    'condensed': '75%',
    'semicondensed': '87.5%',
    'normal': '100%',
    'semiexpanded': '112.5%',
    'expanded': '125%',
    'extraexpanded': '150%',
    'ultraexpanded': '200%',
}


class Loader(object):
    def __init__(self, window: Window, model: Gio.ListStore):
        self.window = window
        self.model = model

    def load(self, files: Sequence[Gio.File]):
        self.window.processing = True

        for f in files:
            try:
                path = f.get_path()
                if path:
                    path = unquote(path)

                    if os.path.exists(path) and os.access(path, os.R_OK):
                        ttfont = TTFont(path, lazy=True)
                        data = self._get_font_data(ttfont)
                        ttfont.close()
                        font = Font(path, data)
                        GLib.idle_add(self.model.append, font)
                    else:
                        error_text = _(
                            'You don’t have read access to {font} or it doesn’t exists.'  # noqa
                        )
                        GLib.idle_add(
                            self._show_error, error_text.format(font=path)
                        )

            except Exception as exc:
                print(f'Error loading {path}')
                print(exc)
                error_text = _('Error: {error}.')
                GLib.idle_add(self._show_error, error_text.format(error=exc))

        self.window.processing = False

    def _show_error(self, text: str):
        error = Adw.Toast.new(text)
        self.window.toasts.add_toast(error)

    def _get_font_data(self, tt_font: TTFont) -> FontData:
        head = tt_font['head']
        naming = tt_font['name']  # Font naming table
        variations = None
        if 'fvar' in tt_font:
            variations = tt_font['fvar']

        font_data = FontData(
            naming.getBestFullName(),  # type: ignore
            naming.getBestFamilyName(),  # type: ignore
            naming.getDebugName(5),  # type: ignore
        )

        # Font macStyle bits
        mac_style_bitfield = [bool(int(b)) for b in bin(head.macStyle)[2:]]  # type: ignore
        mac_style_bitfield.reverse()

        # Get font bold or italic by macStyle
        if mac_style_bitfield[0]:
            font_data.weight = '700'  # Font is bold
        if len(mac_style_bitfield) > 1 and mac_style_bitfield[1]:
            font_data.style = 'italic'  # Font is italic

        # Variable font data
        if variations is not None:
            font_data.is_variable = True
            axes: dict[str, tuple[float, ...]] = variations.getAxes()  # type: ignore
            if wght := axes.get('wght'):
                font_data.weight = self.__get_font_weight_axis_range(wght)
            if wdth := axes.get('wdth'):
                font_data.weight = self.__get_font_width_axis_range(wdth)

        # Get local font name
        font_data.local.append('local("%s")' % naming.getDebugName(4))  # type: ignore
        if not naming.getDebugName(6) == naming.getDebugName(4):  # type: ignore
            font_data.local.append('local("%s")' % naming.getDebugName(6))  # type: ignore

        # Get style, weight and width
        # We try to guess this info from some name strings
        names = ' '.join(
            (
                naming.getDebugName(17) or naming.getDebugName(2),  # type: ignore
                naming.getDebugName(4),  # type: ignore
            )
        )
        ws = self.__normalize_names(names.split())

        for s in ws:
            if s == 'italic':
                font_data.style = 'italic'
            if variations is None:
                if s in WEIGHTS:
                    font_data.weight = WEIGHTS[s]
                elif s in WIDTHS:
                    font_data.width = WIDTHS[s]

        return font_data

    def __normalize_names(self, names: Sequence[str]) -> Sequence[str]:
        return list(
            map(lambda n: n.lower().replace('-', '').replace('_', ''), names)
        )

    def __get_font_weight_axis_range(self, weights: Sequence[float]) -> str:
        min_weight = min(weights)
        max_weight = max(weights)

        if min_weight == max_weight:
            weight = str(int(max_weight))
        else:
            weight = f"{int(min_weight)} {int(max_weight)}"

        return weight

    def __get_font_width_axis_range(self, widths: Sequence[float]) -> str:
        min_width = min(widths)
        max_width = max(widths)

        if min_width == max_width:
            width = f"{max_width:g}%"
        else:
            width = f"{min_width:g}% {max_width:g}%"

        return width
