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
import re

from gettext import gettext as _
from threading import Thread
from gi.repository import GLib
from fontTools.ttLib import TTFont
from fontTools.subset import parse_unicodes, Subsetter


class Generator(object):

    def __init__(self, window, path, list, formats, ranges, css_out):
        self.window = window
        self.path = path
        self.list = list
        self.formats = formats
        self.ranges = []
        self.css_out = css_out
        self.css = {}

        if ranges == 0:
            self.ranges = ['latin', 'latin-ext', 'cyrillic', 'cyrillic-ext', 'greek', 'greek-ext']
        elif ranges == 2:
            self.ranges = []

        total_ranges = 1 if not len(self.ranges) > 0 else len(self.ranges)
        self.total = (len(list) * len(formats)) * total_ranges
        self.progress = 0

    def run(self):
        self._update_progressbar(reset=True)
        self.window.log.reset()

        thread = Thread(target=self.generate)
        thread.daemon = True
        thread.start()

    def generate(self):
        self.window.toggle_generation(True)

        for font in self.list:
            self._generate_font(font.filename, font.data)

        css = self._generate_css()
        self._append_log(_('Generation finished!'), bold=True)

        self.window.toggle_generation(False)

    def _generate_font(self, filename, data):
        slug = data['family-slug']
        name = data['name-slug']
        out_folder = os.path.join(self.path, slug)

        self._append_log(_('Generating fonts for %s:' % data['name']), bold=True)

        if len(self.ranges) >= 1:
            for range in self.ranges:
                font = TTFont(filename)
                subs = Subsetter()

                range_name = '-'.join([name, range])
                unicode_range =  self.__get_range(range)

                subs.populate(unicodes=parse_unicodes(unicode_range))
                subs.subset(font)
                self._write_font(font, data, out_folder, range_name, range=range)
                font.close()
        else:
            font = TTFont(filename)
            self._write_font(font, data, out_folder, name)
            font.close()

    def _write_font(self, font, data, out_folder, name, range=None):
        cmap = font.getBestCmap()

        if cmap:
            slug  = data['family-slug']
            self.css.setdefault(slug,{})

            css = {
                'font-family':  data['family'],
                'font-style':   data['style'],
                'font-weight':  data['weight'],
                'font-display': 'swap',
                'src':          list(data['local'])
            }

            for format in self.formats:
                count = len(font.getGlyphOrder()) - 1
                font.flavor = format
                outfile = name + '.' + format
                outpath = os.path.join(out_folder, outfile)

                if not os.path.exists(out_folder):
                    os.makedirs(out_folder)

                font.save(outpath)
                prefix = slug + '/' if self.css_out >= 1 else ''
                css['src'].append('url(%s%s) format("%s")' % (prefix, outfile, format))

                self.progress += 1
                self._append_log(_('Generated %s with %s glyphs.' % (outfile, count)))

            if range:
                css['unicode-range'] = self.__get_range(range)
            self.css[slug][name] = css

        else:
            self.progress += 1 * len(self.formats)
            text = range if range else name
            self._append_log(_('No glyphs where found for %s. Skipping.' % text), italic=True)

        # Update progressbar
        GLib.idle_add(self._update_progressbar)

    def _generate_css(self):
        ff_template = '''
            /* {comment} */
            @font-face {{
              {styles}
            }}
            '''.strip()
        ff_template = re.sub(r'^\s+|\s+$', '', ff_template, 0, re.MULTILINE)

        css_sheets = []
        families_css = {}

        self._append_log(_('Generating CSS:'), bold=True)

        for family, subset in self.css.items():
            family_css = ''

            for font, properties in subset.items():
                ff = ff_template.format(**{
                    'comment': font,
                    'styles': self._dict_to_styles(properties),
                })

                family_css += ff

            families_css[family] = family_css

        if self.css_out == 0:
            for family, css in families_css.items():
                cssfile = os.path.join(self.path, family, family + '.css')
                css_sheets.append(cssfile)
                with open(cssfile, 'w') as file:
                    print(css, file=file)
            return css_sheets
        elif self.css_out == 1:
            css_sheet = ''
            for family, css in families_css.items():
                css_sheet += css

            cssfile = os.path.join(self.path, 'stylesheet.css')
            css_sheets.append(cssfile)
            with open(cssfile, 'w') as file:
                print(css_sheet, file=file)

            return css_sheets
        elif self.css_out == 2:
            css_sheet = ''
            for family, css in families_css.items():
                css_sheet += css

            return css_sheet

        self._append_log(_('Generated %s.' % cssfile))
    def _dict_to_styles(self, style_dict):
        properties = []

        for i, (k, v) in enumerate(style_dict.items()):
            v = ', '.join(v) if isinstance(v, list) else v
            properties.append('\t{}: {};'.format(k, v))

        return '\n'.join(properties)
        #return '; '.join(['{}: {}'.format(k, v) for k, v in style_dict.items()])

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

    def _update_progressbar(self, reset=False):
        progress = 0 if reset else self.progress / self.total
        self.window.progressbar.set_fraction(progress)

    def _append_log(self, text, bold=False, italic=False):
        GLib.idle_add(self.window.log.append, text, bold, italic)

