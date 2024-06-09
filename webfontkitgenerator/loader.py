# Copyright 2020 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from collections.abc import Sequence
from urllib.parse import urlparse, unquote

from gettext import gettext as _
from gi.repository import Adw, GLib
from fontTools.ttLib import TTFont

from webfontkitgenerator.font import Font, FontData

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
    def __init__(self, window, model):
        self.window = window
        self.model = model

    def load(self, files):
        self.window.processing = True

        for f in files:
            try:
                path = None
                if isinstance(f, str):
                    url_parsed = urlparse(f)
                    if url_parsed.scheme == 'file':
                        path = url_parsed.path
                    else:
                        continue
                else:
                    path = f.get_path()
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
        naming = tt_font['name']  # Font naming table
        variations = None
        if 'fvar' in tt_font:
            variations = tt_font['fvar']

        font_data = FontData(
            naming.getBestFullName(),  # type: ignore
            naming.getBestFamilyName(),  # type: ignore
            naming.getDebugName(5),  # type: ignore
        )

        # Variable font data
        if variations is not None:
            font_data.is_variable = True
            axes: dict[str, tuple[float, ...]] = variations.getAxes()  # type: ignore
            font_data.weight, font_data.width = self.__get_font_axis_ranges(
                axes['wght'], axes['wdth']
            )

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

    def __get_font_axis_ranges(
        self, weights: Sequence[float], widths: Sequence[float]
    ) -> tuple[str, str]:
        min_weight = min(weights)
        max_weight = max(weights)
        min_width = min(widths)
        max_width = max(widths)

        if min_weight == max_weight:
            weight = str(int(max_weight))
        else:
            weight = f"{int(min_weight)} {int(max_weight)}"

        if min_width == max_width:
            width = f"{max_width:g}%"
        else:
            width = f"{min_width:g}% {max_width:g}%"

        return (weight, width)
