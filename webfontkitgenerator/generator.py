# Copyright 2020 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import os
import re
from gettext import gettext as _
from io import BytesIO
from threading import Thread

from fontTools.subset import Subsetter, parse_unicodes
from fontTools.ttLib import TTFont
from gi.repository import GLib

from webfontkitgenerator.font import Font, FontData


class Generator(object):
    def __init__(
        self,
        window,
        path: str,
        fonts_list: list[Font],
        formats: list[str],
        ranges: dict[str, str] | None,
        base64: bool,
        font_display: str | None,
    ):
        self.window = window
        self.stop = False
        self.path = path
        self.list = fonts_list
        self.formats = formats
        self.ranges = ranges
        self.base64 = base64
        self.font_display = font_display
        self.css: dict[str, dict[str, dict[str, str | list[str]]]] = {}

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
        self.window.finished_stack.set_visible_child_name('info')

        return

    def _generate_font(self, filename, data: FontData):
        # name = data['name-slug']
        log_text = _('Generating fonts for {name}:')
        self._append_log(log_text.format(name=data.name), bold=True)
        progress_text = _('Generating {name}')
        self._set_progressbar_text(progress_text.format(name=data.family))

        if self.ranges:
            for char_range, unicodes in self.ranges.items():
                font = TTFont(filename)
                subs = Subsetter()

                subs.populate(unicodes=parse_unicodes(unicodes))
                subs.subset(font)
                self._write_font(font, data, char_range=char_range)
                font.close()
                del font
        else:
            font = TTFont(filename)
            self._write_font(font, data)
            font.close()

    def _write_font(
        self, font: TTFont, data: FontData, char_range: str | None = None
    ):
        cmap = font.getBestCmap()
        name = data.name_slug
        name = '-'.join([name, char_range]) if char_range else name

        if cmap:
            slug = data.family_slug
            self.css.setdefault(slug, {})

            css = {
                'font-family': f'"{data.family}"',
                'font-style': data.style,
                'font-weight': data.weight,
                'font-stretch': data.width,
                'src': list(data.local),
            }

            for format in self.formats:
                count = len(font.getGlyphOrder()) - 1
                font.flavor = format

                filename = name + '.' + format
                filenameout = os.path.join(slug, filename)
                outfolder = os.path.join(self.path, slug)
                if not os.path.exists(outfolder):
                    os.makedirs(outfolder)

                if self.base64:
                    output_io = BytesIO()
                    font.save(output_io)
                    output = base64.b64encode(output_io.getvalue())
                    output = output.decode("utf-8")
                    css['src'].append(
                        f'url(data:font/{format};charset=utf-8;base64,{output}) format("{format}")'
                    )
                else:
                    font.save(os.path.join(self.path, filenameout))
                    css['src'].append(f'url({filename}) format("{format}")')

                self._step_done()
                gen_text = _(
                    'Generated <i>{filename}</i> with <i>{count}</i> glyphs.'
                )
                gen_text = gen_text.format(filename=filenameout, count=count)
                self._append_log(gen_text)

            if char_range and self.ranges:
                css['unicode-range'] = self.ranges[char_range]
            if self.font_display is not None:
                css['font-display'] = self.font_display
            self.css[slug][name] = css

        else:
            self._step_done(1 * len(self.formats))
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

    def _step_done(self, increment=1):
        def do_progress(progress):
            self.window.progressbar.props.fraction = progress

        self.progress += increment
        GLib.idle_add(do_progress, self.progress / self.total)

    def _set_progressbar_text(self, text: str):
        GLib.idle_add(self.window.progress.set_title, text)

    def _append_log(self, text: str, bold=False, italic=False):
        GLib.idle_add(self.window.log.append, text, bold, italic)

    def _end_code(self, sheets):
        html = []
        css = []

        for sheet in sheets:
            html.append(f'<link href="{sheet}" rel="stylesheet">')
            css.append(f'@import url("{sheet}");')

        self.window.src_html.set_text('\n'.join(html))
        self.window.src_css.set_text('\n'.join(css))

    def _dict_to_styles(self, style_dict: dict[str, str | list[str]]):
        properties = []

        for k, v in style_dict.items():
            v = ', '.join(v) if isinstance(v, list) else v
            properties.append(f'\t{k}: {v};')

        return '\n'.join(properties)
