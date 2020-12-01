# locader.py
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

import os

from fontTools.ttLib import TTFont

from .font import Font


class Loader(object):

    def __init__(self, window, model, files):
        self.window = window
        self.model = model
        self.files = files

    def load(self):
        self.window.processing = True

        for f in self.files:
            try:
                path = f.get_path()
                if os.path.exists(path):
                    ttfont = TTFont(path, lazy=True)
                    data = self._get_font_data(ttfont['name'].getDebugName)
                    ttfont.close()
                    font = Font(path, data)
                    self.model.append(font)

            except Exception as e:
                continue

        self.window.processing = False


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

        s = '-'
        data['name-slug'] = s.join(data['name'].split()).lower()
        data['family-slug'] = s.join(data['family'].split()).lower()

        ws = data_src(17) if data_src(17) else data_src(2)
        ws = ws.split()

        for s in ws:
            if s == 'Italic':
                data['style'] = 'italic'
            if s in weights:
                data['weight'] = weights[s]

        return data

