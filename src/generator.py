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

    def __init__(self, window, path, list, formats, ranges, font_display):
        self.window = window
        self.stop = False
        self.path = path
        self.list = list
        self.formats = formats
        self.ranges = ranges
        self.font_display = font_display
        self.css = {}

        total_ranges = len(ranges) if ranges else 1
        self.total = (len(list) * len(formats)) * total_ranges
        self.progress = 0

    def run(self):
        self._update_progressbar(reset=True)
        self.window.log.reset()
        self.window.cancel.connect('clicked', self.do_stop)

        thread = Thread(target=self.generate)
        thread.daemon = True
        thread.start()

    def do_stop(self, widget=None):
        self.stop = True
        self.window.processing = False
        self.window.appstack.set_visible_child_name('main')

    def generate(self):
        self.window.processing = True
        self.window.appstack.set_visible_child_name('progress')

        for font in self.list:
            if self.stop:
                return
            self._generate_font(font.filename, font.data)

        css = self._generate_css()
        self._end_code(css)
        self._append_log(_('Generation finished!'), bold=True)

        self.window.processing = False
        self.window.appstack.set_visible_child_name('finished')

    def _generate_font(self, filename, data):
        name = data['name-slug']
        self._append_log(_('Generating fonts for %s:' % data['name']), bold=True)

        if self.ranges:
            for range, unicodes in self.ranges.items():
                font = TTFont(filename)
                subs = Subsetter()

                subs.populate(unicodes=parse_unicodes(unicodes))
                subs.subset(font)
                self._write_font(font, data, range=range)
                font.close()
        else:
            font = TTFont(filename)
            self._write_font(font, data)
            font.close()

    def _write_font(self, font, data, range=None):
        cmap = font.getBestCmap()
        name = data['name-slug']
        name = '-'.join([name, range]) if range else name

        if cmap:
            slug = data['family-slug']
            self.css.setdefault(slug,{})

            css = {
                'font-family':  data['family'],
                'font-style':   data['style'],
                'font-weight':  data['weight'],
                'src':          list(data['local'])
            }

            for format in self.formats:
                count = len(font.getGlyphOrder()) - 1
                font.flavor = format

                filename = name + '.' + format
                filenameout = os.path.join(slug, filename)
                outfolder = os.path.join(self.path, slug)
                if not os.path.exists(outfolder):
                    os.makedirs(outfolder)

                font.save(os.path.join(self.path, filenameout))
                css['src'].append('url(%s) format("%s")' % (filename, format))

                self.progress += 1
                self._append_log(_('Generated <i>%s</i> with <i>%s</i> glyphs.' % (filenameout, count)))

            if range:
                css['unicode-range'] = self.ranges[range]
            if self.font_display > 0:
                css['font-display'] = self.__get_font_display(self.font_display)
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
                    'styles': self.__dict_to_styles(properties),
                })
                family_css += ff + '\n'
            families_css[family] = family_css

        for family, css in families_css.items():
            filename = os.path.join(family, family + '.css')
            css_sheets.append(filename)

            with open(os.path.join(self.path, filename), 'w') as f:
                print(css, file=f)

            self._append_log(_('Generated <i>%s</i>.' % filename))

        if len(css_sheets) == 0:
            self._append_log(_('There is no CSS to generate.'), italic=True)

        return css_sheets


    '''
    PRIVATE FUNCTIONS
    '''

    def _update_progressbar(self, reset=False):
        progress = 0 if reset else self.progress / self.total
        self.window.progressbar.set_fraction(progress)

    def _append_log(self, text, bold=False, italic=False):
        GLib.idle_add(self.window.log.append, text, bold, italic)

    def _end_code(self, sheets):
        html = []
        css = []

        for sheet in sheets:
            html.append('<link href="%s" rel="stylesheet">' % sheet)
            css.append('@import url("%s");' % sheet)

        self.window.end_html.set_text('\n'.join(html))
        self.window.end_css.set_text('\n'.join(css))


    '''
    SECRET HELP FUNCTIONS
    '''

    def __dict_to_styles(self, style_dict):
        properties = []

        for i, (k, v) in enumerate(style_dict.items()):
            v = ', '.join(v) if isinstance(v, list) else v
            properties.append('\t{}: {};'.format(k, v))

        return '\n'.join(properties)
        #return '; '.join(['{}: {}'.format(k, v) for k, v in style_dict.items()])

    def __get_font_display(self, fd):
        fds = ['auto', 'block', 'swap', 'fallback', 'optional']
        return fds[fd - 1]

