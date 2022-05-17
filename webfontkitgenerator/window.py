# Copyright 2020-2021 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from gettext import gettext as _
from gi.repository import Adw, Gdk, Gio, GLib, GObject, Gtk

from webfontkitgenerator.generator import Generator
from webfontkitgenerator.google import GoogleDialog
from webfontkitgenerator.loader import Loader
from webfontkitgenerator.options import Options
from webfontkitgenerator.log import Log
from webfontkitgenerator.sourceview import SourceView
from webfontkitgenerator.font import Font, FontRow


@Gtk.Template(
    resource_path='/com/rafaelmardojai/WebfontKitGenerator/window.ui'
)
class Window(Adw.ApplicationWindow):
    __gtype_name__ = 'Window'

    processing = GObject.Property(type=bool, default=False)

    appstack = Gtk.Template.Child()

    progressbar = Gtk.Template.Child()
    progress = Gtk.Template.Child()
    cancel = Gtk.Template.Child()

    finished_viewstack = Gtk.Template.Child()
    import_html_box = Gtk.Template.Child()
    import_css_box = Gtk.Template.Child()
    log_column = Gtk.Template.Child()
    open_files = Gtk.Template.Child()

    viewstack = Gtk.Template.Child()
    fonts_box = Gtk.Template.Child()
    fonts_stack = Gtk.Template.Child()
    fonts_list = Gtk.Template.Child()
    path_revealer = Gtk.Template.Child()
    directory = Gtk.Template.Child()
    toasts = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.options = Options()
        self.outpath = None
        self.outuri = None
        self.log = Log()
        self.model = Gio.ListStore.new(Font)

        self.fontschooser = Gtk.FileChooserNative.new(
            _('Open Font Files'),
            self,
            Gtk.FileChooserAction.OPEN,
            None,
            None
        )
        self.outpathchooser = Gtk.FileChooserNative.new(
            _('Select Output Directory'),
            self,
            Gtk.FileChooserAction.SELECT_FOLDER,
            None,
            None
        )

        self.setup_widgets()
        self.setup_actions()

        self.style_manager = self.get_application().get_style_manager()
        self.style_manager.connect('notify::dark', self._on_dark_style)
        self._on_dark_style(None, None)

    def setup_widgets(self):
        # Setup view stack pages
        page = self.viewstack.add_titled(self.options, 'options', _('Options'))
        page.set_icon_name('emblem-system-symbolic')

        # Setup buttons
        self.open_files.connect('clicked', self.open_generation_dir)

        # Setup fonts list
        self.fonts_list.bind_model(self.model, self._create_font_row)
        self.model.connect(
            'items-changed',
            lambda _l, _p, _r, _a: self._check_ready_state()
        )

        # Setup log text view
        self.log_column.set_child(self.log)

        # Setup source views
        self.end_html = SourceView()
        self.end_html.set_language('html')
        self.import_html_box.append(self.end_html)
        self.end_css = SourceView()
        self.end_css.set_language('css')
        self.import_css_box.append(self.end_css)

        # Setup fonts file chooser
        fonts_filter = Gtk.FileFilter()
        fonts_filter.set_name(_('OTF & TTF'))
        fonts_filter.add_mime_type('font/otf')
        fonts_filter.add_pattern('.otf')
        fonts_filter.add_mime_type('font/ttf')
        fonts_filter.add_pattern('.ttf')
        self.fontschooser.add_filter(fonts_filter)
        self.fontschooser.set_select_multiple(True)
        self.fontschooser.connect('response', self._on_fontschooser_response)

        # Setup outpath folder chooser
        self.outpathchooser.connect(
            'response', self._on_outpathchooser_response
        )

        # Drag and drop
        drop_target = Gtk.DropTarget.new(Gdk.FileList, Gdk.DragAction.COPY)
        drop_target.connect("drop", self._on_drop)
        self.add_controller(drop_target)

    def setup_actions(self):
        remove_font = Gio.SimpleAction.new(
            'remove-font', GLib.VariantType.new('u')
        )
        remove_font.connect('activate', self._on_remove_font)
        self.add_action(remove_font)

        open_ = Gio.SimpleAction.new('open', None)
        open_.connect('activate', self._on_open)
        self.add_action(open_)

        google = Gio.SimpleAction.new('google', None)
        google.connect('activate', self._on_google)
        self.add_action(google)

        set_outpath = Gio.SimpleAction.new('set-outpath', None)
        set_outpath.connect('activate', self._on_set_outpath)
        self.add_action(set_outpath)

        generate = Gio.SimpleAction.new('generate', None)
        generate.connect('activate', self._on_generate)
        generate.set_enabled(False)
        self.add_action(generate)

        back = Gio.SimpleAction.new('back', None)
        back.connect('activate', self._on_back)
        self.add_action(back)

    def load_fonts(self, files):
        loader = Loader(self, self.model)
        loader.load(files)

    def open_generation_dir(self, _widget):
        Gio.app_info_launch_default_for_uri(self.outuri)

    def _on_open(self, _action, _param):
        if self.appstack.get_visible_child_name() == 'main':
            self.fontschooser.show()

    def _on_google(self, _action, _param):
        dialog = GoogleDialog(self)
        dialog.set_transient_for(self)
        dialog.set_modal(True)
        dialog.present()

    def _on_set_outpath(self, _action, _param):
        if self.appstack.get_visible_child_name() == 'main':
            self.outpathchooser.show()

    def _on_generate(self, _action, _param):
        generator = Generator(
            self, self.outpath, self.model,
            self.options.get_formats(),
            self.options.get_subsetting(),
            self.options.get_font_display()
        )
        generator.run()

    def _on_back(self, _action, _param):
        if not self.processing:
            self.appstack.set_visible_child_name('main')

    def _on_remove_font(self, _action, param):
        self.model.remove(param.get_uint32())

    def _on_fontschooser_response(self, dialog, response):
        dialog.hide()
        if response == Gtk.ResponseType.ACCEPT:
            files = dialog.get_files()
            if files:
                self.load_fonts(files)

    def _on_outpathchooser_response(self, dialog, response):
        dialog.hide()
        if response == Gtk.ResponseType.ACCEPT:
            path = dialog.get_file().get_path()
            uri = dialog.get_file().get_uri()
            name = os.path.basename(path)

            if os.access(path, os.W_OK):
                self.outpath = path
                self.outuri = uri
                self.directory.set_label(name)
                self._check_ready_state()
            else:
                error = Adw.Toast.new(
                    _("You don't have write access to the selected directory.")
                )
                self.toasts.add_toast(error)

    def _create_font_row(self, font):
        widget = FontRow(font.data)
        return widget

    def _on_drop(self, _target, value, _x, _y):
        if (
            isinstance(value, Gdk.FileList)
            and self.appstack.get_visible_child_name() == 'main'
        ):
            self.load_fonts(value.get_files())

    def _check_ready_state(self):
        items = self.model.get_n_items() > 0

        self.lookup_action('generate').set_enabled(items and self.outpath)
        self.path_revealer.set_reveal_child(items)

        if items:
            self.fonts_stack.set_visible_child_name('fonts')
        else:
            self.fonts_stack.set_visible_child_name('empty')

    def _on_dark_style(self, _obj, _pspec):
        dark = self.style_manager.get_dark()
        self.end_html.set_dark_scheme(dark)
        self.end_css.set_dark_scheme(dark)
