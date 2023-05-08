# Copyright 2020 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import re

from gettext import gettext as _
from threading import Thread
from gi.repository import GLib
from fontTools.ttLib import TTFont
from fontTools.subset import parse_unicodes, Subsetter


class Generator(object):
    def __init__(
        self, window, path, fonts_list, formats, ranges, font_display
    ):
        self.window = window
        self.stop = False
        self.path = path
        self.list = fonts_list
        self.formats = formats
        self.ranges = ranges
        self.font_display = font_display
        self.css = {}

        total_ranges = len(ranges) if ranges else 1
        self.total = (len(fonts_list) * len(formats)) * total_ranges
        self.progress = 0

    def run(self):
        self.window.progressbar.set_fraction(0)
        self.window.progress.set_title('')
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
        GLib.timeout_add(50, self._on_progressbar_timeout, None)
        self.window.processing = True
        self.window.appstack.set_visible_child_name('progress')

        for font in self.list:
            if self.stop:
                return
            self._generate_font(font.path, font.data)

        css = self._generate_css()
        self._end_code(css)
        self._append_log(_('Generation finished!'), bold=True)

        self.window.processing = False
        self.window.appstack.set_visible_child_name('finished')
        self.window.finished_viewstack.set_visible_child_name('info')

        return

    def _generate_font(self, filename, data):
        # name = data['name-slug']
        log_text = _('Generating fonts for {name}:')
        self._append_log(log_text.format(name=data['name']), bold=True)
        progress_text = _('Generating {name}')
        self._set_progressbar_text(progress_text.format(name=data['family']))

        if self.ranges:
            for range, unicodes in self.ranges.items():
                font = TTFont(filename)
                subs = Subsetter()

                subs.populate(unicodes=parse_unicodes(unicodes))
                subs.subset(font)
                self._write_font(font, data, range=range)
                font.close()
                del font
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
            self.css.setdefault(slug, {})

            css = {
                'font-family': data['family'],
                'font-style': data['style'],
                'font-weight': data['weight'],
                'src': list(data['local']),
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
                css['src'].append(f'url({filename}) format("{format}")')

                self.progress += 1
                gen_text = _(
                    'Generated <i>{filename}</i> with <i>{count}</i> glyphs.'
                )
                gen_text = gen_text.format(filename=filenameout, count=count)
                self._append_log(gen_text)

            if range:
                css['unicode-range'] = self.ranges[range]
            if self.font_display > 0:
                css['font-display'] = self._get_font_display(self.font_display)
            self.css[slug][name] = css

        else:
            self.progress += 1 * len(self.formats)
            text = range if range else name
            gen_text = _('No glyphs where found for {range}. Skipping.')
            self._append_log(gen_text.format(range=text), italic=True)

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
        self._set_progressbar_text(_('Finishing'))

        for family, subset in self.css.items():
            family_css = ''
            for font, properties in subset.items():
                ff = ff_template.format(
                    **{
                        'comment': font,
                        'styles': self._dict_to_styles(properties),
                    }
                )
                family_css += ff + '\n'
            families_css[family] = family_css

        for family, css in families_css.items():
            filename = os.path.join(family, family + '.css')
            css_sheets.append(filename)

            with open(os.path.join(self.path, filename), 'w') as f:
                print(css, file=f)

            gen_text = _('Generated <i>{filename}</i>.')
            self._append_log(gen_text.format(filename=filename))

        if len(css_sheets) == 0:
            self._append_log(_('There is no CSS to generate.'), italic=True)

        return css_sheets

    def _on_progressbar_timeout(self, _data):
        progress = self.progress / self.total
        self.window.progressbar.set_fraction(progress)
        return progress != 1

    def _set_progressbar_text(self, text):
        GLib.idle_add(self.window.progress.set_title, text)

    def _append_log(self, text, bold=False, italic=False):
        GLib.idle_add(self.window.log.append, text, bold, italic)

    def _end_code(self, sheets):
        html = []
        css = []

        for sheet in sheets:
            html.append(f'<link href="{sheet}" rel="stylesheet">')
            css.append(f'@import url("{sheet}");')

        self.window.src_html.set_text('\n'.join(html))
        self.window.src_css.set_text('\n'.join(css))

    def _dict_to_styles(self, style_dict):
        properties = []

        for i, (k, v) in enumerate(style_dict.items()):
            v = ', '.join(v) if isinstance(v, list) else v
            properties.append('\t{}: {};'.format(k, v))

        return '\n'.join(properties)

    def _get_font_display(self, fd):
        fds = ['auto', 'block', 'swap', 'fallback', 'optional']
        return fds[fd - 1]
