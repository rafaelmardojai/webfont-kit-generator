# Copyright 2020 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from gettext import gettext as _
from gi.repository import Gdk, Gio, GLib, Gtk, Handy

from webfontkitgenerator.generator import Generator
from webfontkitgenerator.loader import Loader
from webfontkitgenerator.options import Options
from webfontkitgenerator.log import Log
from webfontkitgenerator.sourceview import SourceView
from webfontkitgenerator.font import Font, FontWidget


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
        self.outuri = None
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
        font_filter = Gtk.FileFilter()
        font_filter.set_name(_('OTF & TTF'))
        font_filter.add_mime_type('font/otf')
        font_filter.add_pattern('.otf')
        font_filter.add_mime_type('font/ttf')
        font_filter.add_pattern('.ttf')

        filechooser = Gtk.FileChooserNative.new(
            _('Open font files'),
            self,
            Gtk.FileChooserAction.OPEN,
            None,
            None)
        filechooser.set_select_multiple(True)
        filechooser.add_filter(font_filter)

        response = filechooser.run()

        if response == Gtk.ResponseType.ACCEPT:
            files = filechooser.get_files()
            if files:
                self.load_fonts(files)

    def load_fonts(self, files):
        loader = Loader(self, self.model, files)
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
            self.outuri = uri
            self.options.directory.set_label(name)

            self._change_ready_state()
            filechooser.destroy()

        elif response == Gtk.ResponseType.REJECT:
            filechooser.destroy()

    def open_generation_dir(self, *args):
        uri = self.outURI
        Gtk.show_uri_on_window(self, uri, Gdk.CURRENT_TIME)


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

