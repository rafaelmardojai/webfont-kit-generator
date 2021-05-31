# Copyright 2020-2021 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from urllib.parse import urlparse, unquote

from gettext import gettext as _
from gi.repository import Gtk
from fontTools.ttLib import TTFont

from webfontkitgenerator.font import Font


class Loader(object):

    def __init__(self, window, model, files):
        self.window = window
        self.model = model
        self.files = files

    def load(self):
        self.window.processing = True

        for f in self.files:
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
                    data = self._get_font_data(ttfont['name'].getDebugName)
                    ttfont.close()
                    font = Font(path, data)
                    self.model.append(font)
                else:
                    error_dialog = Gtk.MessageDialog(self.window, 0,
                                                     Gtk.MessageType.WARNING,
                                                     Gtk.ButtonsType.OK,
                                                     _('Font loading error'))
                    error_text = _("You don't have read access to {font} or it doesn't exists.")
                    error_dialog.format_secondary_text(error_text.format(font=path))
                    error_response = error_dialog.run()
                    if error_response == Gtk.ResponseType.OK:
                        error_dialog.destroy()

            except Exception as e:
                error_dialog = Gtk.MessageDialog(self.window, 0,
                                                 Gtk.MessageType.WARNING,
                                                 Gtk.ButtonsType.OK,
                                                 _('Font loading error'))
                error_text = _('Something happened when trying to load {font}.')
                error_text += '\n' + str(e)
                error_dialog.format_secondary_text(error_text.format(font=path))
                error_response = error_dialog.run()
                if error_response == Gtk.ResponseType.OK:
                    error_dialog.destroy()

        self.window.processing = False
        self.window.stack.set_visible_child_name('main')


    '''
    PRIVATE FUNCTIONS
    '''

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

        data['name-slug'] = '-'.join(data['name'].split()).lower()
        data['family-slug'] = '-'.join(data['family'].split()).lower()

        ws = data_src(17) if data_src(17) else data_src(2)
        ws = ws.split()

        for s in ws:
            if s == 'Italic':
                data['style'] = 'italic'
            if s in weights:
                data['weight'] = weights[s]

        return data

