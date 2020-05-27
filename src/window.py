# window.py
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

import logging
import os

from threading import Thread
from gettext import gettext as _
from gi.repository import GLib, Gio, Gtk, Handy
from fontTools.ttLib import TTFont

from .options import Options
from .font import Font, FontWidget
from .generator import Generator
from .log import Log
from .sourceview import SourceView

LOGGER = logging.getLogger('storiestyper')


@Gtk.Template(resource_path='/com/rafaelmardojai/WebfontKitGenerator/ui/window.ui')
class Window(Handy.ApplicationWindow):
    __gtype_name__ = 'Window'

    appstack = Gtk.Template.Child()

    progressbar = Gtk.Template.Child()
    progressbar_label = Gtk.Template.Child()
    cancel = Gtk.Template.Child()

    import_html_frame = Gtk.Template.Child()
    import_css_frame = Gtk.Template.Child()
    log_column = Gtk.Template.Child()

    btn_generate = Gtk.Template.Child()
    btn_add_fonts = Gtk.Template.Child()

    stack = Gtk.Template.Child()
    fonts_stack = Gtk.Template.Child()
    fonts_list = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.processing = False
        self.options = Options()
        self.outpath = None
        self.log = Log(self.progressbar_label)

        self.setup_widgets()

        self.options.directory.connect('file-set', self._update_outpath)
        self.options.directory.connect('file-set', self._change_ready_state)

        self.model = Gio.ListStore.new(Font)
        self.model.connect('items-changed', self._change_ready_state)
        self.fonts_list.bind_model(self.model, self._create_font_widget)

        self.btn_generate.connect('clicked', self.on_generate)

    def setup_widgets(self):
        self.stack.add_titled(self.options, 'options', _('Output Options'))

        self.log_column.add(self.log)
        self.log.show_all()

        self.end_html = SourceView()
        self.end_html.set_language('html')
        self.import_html_frame.add(self.end_html)

        self.end_css = SourceView()
        self.end_css.set_language('css')
        self.import_css_frame.add(self.end_css)

    def open_fonts(self, _widget=None):
        otf_filter = Gtk.FileFilter()
        otf_filter.set_name(_('OTF Fonts'))
        otf_filter.add_mime_type('font/otf')
        otf_filter.add_pattern('.otf')
        ttf_filter = Gtk.FileFilter()
        ttf_filter.set_name(_('TTF Fonts'))
        ttf_filter.add_mime_type('font/ttf')
        ttf_filter.add_pattern('.ttf')

        filechooser = Gtk.FileChooserNative.new(
            _('Open font files'),
            self,
            Gtk.FileChooserAction.OPEN,
            None,
            None)
        filechooser.set_select_multiple(True)
        filechooser.add_filter(otf_filter)
        filechooser.add_filter(ttf_filter)
        response = filechooser.run()

        if response == Gtk.ResponseType.ACCEPT:
            filenames = filechooser.get_filenames()

            filechooser.destroy()

            if filenames:
                thread = Thread(target=self.load_fonts,
                                args=(filenames,))
                thread.daemon = True
                thread.start()

        elif response == Gtk.ResponseType.REJECT:
            filechooser.destroy()

    def load_fonts(self, filenames):
        for f in filenames:
            try:
                if os.path.exists(f):
                    ttfont = TTFont(f, lazy=True)
                    data = self._get_font_data(ttfont['name'].getDebugName)
                    ttfont.close()
                    font = Font(f, data)
                    GLib.idle_add(self.model.append, font)

            except Exception as e:
                LOGGER.warning('Error Reading File: %r' % e)

    def on_generate(self, widget):
            generator = Generator(self, self.outpath, self.model,
                                  self.options.get_formats(),
                                  self.options.get_subsetting(),
                                  self.options.get_font_display())
            generator.run()


    '''
    PRIVATE
    '''

    def _create_font_widget(self, font):
        widget = FontWidget(font, self.model)
        return widget

    def _update_outpath(self, chooser):
        self.outpath = chooser.get_filename()

    def _change_ready_state(self, *args, **kwargs):
        children = True if len(self.model) > 0 else False

        if children and self.outpath:
            self.btn_generate.set_sensitive(True)
        else:
            self.btn_generate.set_sensitive(False)

        if children:
            self.fonts_stack.set_visible_child_name('fonts')
        else:
            self.fonts_stack.set_visible_child_name('empty')

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

