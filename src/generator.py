# generator.py
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
from threading import Thread

from gi.repository import GLib, Gtk
from fontTools.ttLib import TTFont
from fontTools.subset import parse_unicodes, Subsetter

class Generator(object):

    def __init__(self, window, path, list, formats=['woff2', 'woff'], ranges=['latin', 'latin-ext', 'devanagari', 'vietnamese']):
        self.window = window
        self.path = path
        self.list = list
        self.formats = formats
        self.ranges = ranges
        self.css = {}
        self.css_styles = {
            'font-family': '',
            'font-style': '',
            'font-weight': '',
            'font-display': 'swap',
            'src': ''
        }

        self.total = (len(list) * len(formats)) * len(ranges)
        self.progress = 0

        self.replace_all = False
        #css_space = self.css[font.data['family-slug']]

    def run(self):
        self._update_progressbar(reset=True)

        thread = Thread(target=self.generate)
        thread.daemon = True
        thread.start()

    def generate(self):
        self.window.appstack.set_visible_child_name('generator')

        for font in self.list:
            slug = ''.join(font.data['family'].split()).lower()
            self._generate_font(font.filename, font.data, slug)

        self.window.appstack.set_visible_child_name('finish')

    def _generate_font(self, filename, data, slug):
        out_folder = os.path.join(self.path, slug)

        if not os.path.exists(out_folder):
            os.makedirs(out_folder)

        if self.ranges:
            for range in self.ranges:
                font = TTFont(filename)
                name = data['name'] + '-' + range
                subs = Subsetter()
                subs.populate(unicodes=parse_unicodes(self.__get_range(range)))
                subs.subset(font)

                self._write_font(font, out_folder, name, range=range)
                font.close()
        else:
            font = TTFont(filename)
            name = data['name']
            self._write_font(font, out_folder, name)
            font.close()

    def _write_font(self, font, out_folder, name, range=None):
        cmap = font.getBestCmap()

        if cmap:
            for format in self.formats:
                font.flavor = format
                outfile = os.path.join(out_folder, name + '.' + format)
                font.save(outfile)

                self.progress += 1
        else:
            self.progress += 1 * len(self.formats)
            text = range if range else name
            print('No glyphs where found for ' + text)

        # Update progressbar
        GLib.idle_add(self._update_progressbar)

    def _generate_css(self, styles, ranges):
        _CSS_TEMPLATE = '''
            @font-face {
              {styles}
            }
            '''.strip()


        return _CSS_TEMPLATE.format(**{
            'styles': _dict_to_styles(styles),
        })

    def __get_range(self, range):
        ranges = {
            'latin':        'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,' +
                            'U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2212,U+2215',
            'latin-ext':    'U+0100-024F,U+0259,U+1E00-1EFF,U+20A0-20CF,U+2C60-2C7F,' +
                            'U+A720-A7FF',
            'cyrillic':     'U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116',
            'cyrillic-ext': 'U+0460-052F,U+1C80-1C88,U+20B4,U+2DE0-2DFF,' +
                            'U+A640-A69F,U+FE2E-FE2F',
            'greek':        'U+0370-03FF',
            'greek-ext':    'U+1F00-1FFF',
            'vietnamese':   'U+0102-0103,U+0110-0111,U+1EA0-1EF9,U+20AB',
            'devanagari':   'U+0900-097F,U+1CD0-1CF6,U+1CF8-1CF9,U+200B-200D,' +
                            'U+20A8,U+20B9,U+25CC,U+A830-A839,U+A8E0-A8FB'
        }

        return ranges[range]

    def _dict_to_styles(self, style_dict):
        return '; '.join(['{}: {}'.format(k, v) for k, v in style_dict.items()])

    def _update_progressbar(self, reset=False):
        progress = 0 if reset else self.progress / self.total
        self.window.progressbar.set_fraction(progress)

