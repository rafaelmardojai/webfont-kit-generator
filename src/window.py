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

import os

from threading import Thread
from gettext import gettext as _
from gi.repository import GLib, Gio, Gdk, Gtk, Handy
from fontTools.ttLib import TTFont

from .generator import Generator
from .loader import Loader
from .options import Options
from .log import Log
from .sourceview import SourceView
from .font import Font, FontWidget


@Gtk.Template(resource_path='/com/rafaelmardojai/WebfontKitGenerator/ui/window.ui')
class Window(Handy.ApplicationWindow):
    __gtype_name__ = 'Window'

    appstack = Gtk.Template.Child()

    progressbar = Gtk.Template.Child()
    progressbar_label = Gtk.Template.Child()
    cancel = Gtk.Template.Child()

    finished_stack = Gtk.Template.Child()
    import_html_frame = Gtk.Template.Child()
    import_css_frame = Gtk.Template.Child()
    log_column = Gtk.Template.Child()
    open_files = Gtk.Template.Child()

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
        self.outURI = None
        self.log = Log(self.progressbar_label)

        self.setup_widgets()

        self.options.browse.connect('clicked', self.set_outpath)

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

        self.open_files.connect('clicked', self.open_generation_dir)

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

        filechooser.connect('response', self.on_load)
        filechooser.run()

    def on_load(self, filechooser, response):
        if response == Gtk.ResponseType.ACCEPT:
            filenames = filechooser.get_filenames()

            if filenames:
                loader = Loader(self, self.model, filenames)
                loader.load()

    def on_generate(self, widget):
            generator = Generator(self, self.outpath, self.model,
                                  self.options.get_formats(),
                                  self.options.get_subsetting(),
                                  self.options.get_font_display())
            generator.run()

    def set_outpath(self, *args):
        filechooser = Gtk.FileChooserNative.new(
            _('Select output directory'),
            self,
            Gtk.FileChooserAction.SELECT_FOLDER,
            None,
            None)
        response = filechooser.run()

        if response == Gtk.ResponseType.ACCEPT:
            path = filechooser.get_filename()
            uri = filechooser.get_uri()
            name = os.path.basename(path)

            self.outpath = path
            self.outURI = uri
            self.options.directory.set_label(name)

            self._change_ready_state()
            filechooser.destroy()

        elif response == Gtk.ResponseType.REJECT:
            filechooser.destroy()

    def open_generation_dir(self, *args):
        uri = self.outURI
        Gtk.show_uri_on_window(self, uri, Gdk.CURRENT_TIME)
        print(uri)


    '''
    PRIVATE
    '''

    def _create_font_widget(self, font):
        widget = FontWidget(font, self.model)
        return widget

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

