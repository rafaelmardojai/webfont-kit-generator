# Copyright 2020 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from gettext import gettext as _

from gi.repository import Adw, Gdk, Gio, GLib, GObject, Gtk

from webfontkitgenerator.font import Font, FontRow
from webfontkitgenerator.generator import Generator
from webfontkitgenerator.google import GoogleDialog
from webfontkitgenerator.loader import Loader
from webfontkitgenerator.log import Log
from webfontkitgenerator.options import Options
from webfontkitgenerator.sourceview import SourceView


@Gtk.Template(
    resource_path='/com/rafaelmardojai/WebfontKitGenerator/window.ui'
)
class Window(Adw.ApplicationWindow):
    __gtype_name__ = 'Window'

    processing: bool = GObject.Property(type=bool, default=False)

    # Main app stack
    appstack: Gtk.Stack = Gtk.Template.Child()

    # Progress View
    progressbar: Gtk.ProgressBar = Gtk.Template.Child()
    progress: Adw.StatusPage = Gtk.Template.Child()
    cancel: Gtk.Button = Gtk.Template.Child()

    # Finished View
    finished_stack: Gtk.Stack = Gtk.Template.Child()
    src_html: SourceView = Gtk.Template.Child()
    src_css: SourceView = Gtk.Template.Child()
    log: Log = Gtk.Template.Child()

    # Fonts list and options view
    split: Adw.OverlaySplitView = Gtk.Template.Child()
    toolbar_view: Adw.ToolbarView = Gtk.Template.Child()
    fonts_stack: Gtk.Stack = Gtk.Template.Child()
    fonts_list: Gtk.ListBox = Gtk.Template.Child()
    options: Options = Gtk.Template.Child()
    directory: Gtk.Label = Gtk.Template.Child()
    toasts: Adw.ToastOverlay = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setup_actions()

        # Out directory chooser
        self.out_dir: Gio.File | None = None  # Store selected dir
        self.out_dir_chooser = Gtk.FileDialog()
        self.out_dir_chooser.props.title = _('Select Output Directory')

        # Fonts chooser
        self.fonts_chooser = Gtk.FileDialog()
        self.fonts_chooser.props.title = _('Open Font Files')

        fonts_filter = Gtk.FileFilter()
        fonts_filter.set_name(_('OTF & TTF'))
        fonts_filter.add_mime_type('font/otf')
        fonts_filter.add_pattern('.otf')
        fonts_filter.add_mime_type('font/ttf')
        fonts_filter.add_pattern('.ttf')

        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(fonts_filter)
        self.fonts_chooser.props.filters = filters

        # Setup fonts list
        self.model = Gio.ListStore.new(Font)
        self.model.connect(
            'items-changed', lambda _l, _p, _r, _a: self._check_ready_state()
        )
        self.fonts_list.bind_model(self.model, self._create_font_row)
        self.loader = Loader(self, self.model)  # Load fonts to the list model

        # Drag and drop
        drop_target = Gtk.DropTarget.new(Gdk.FileList, Gdk.DragAction.COPY)
        drop_target.connect('drop', self._on_drop)
        self.add_controller(drop_target)

    def setup_actions(self):
        remove_font = Gio.SimpleAction.new(
            'remove-font', GLib.VariantType.new('u')
        )
        remove_font.connect('activate', self._on_remove_font)
        self.add_action(remove_font)

        set_dir = Gio.SimpleAction.new('set-dir', None)
        set_dir.connect('activate', self._on_set_dir)
        self.add_action(set_dir)

        open_ = Gio.SimpleAction.new('open', None)
        open_.connect('activate', self._on_open)
        self.add_action(open_)

        google = Gio.SimpleAction.new('google', None)
        google.connect('activate', self._on_google)
        self.add_action(google)

        generate = Gio.SimpleAction.new('generate', None)
        generate.connect('activate', self._on_generate)
        generate.set_enabled(False)
        self.add_action(generate)

        back = Gio.SimpleAction.new('back', None)
        back.connect('activate', self._on_back)
        self.add_action(back)

    def load_fonts(self, files):
        self.loader.load(files)

    @Gtk.Template.Callback()
    def _open_generation_dir(self, _button):
        def on_launched(launcher, result):
            launcher.launch_finish(result)

        launcher = Gtk.FileLauncher(file=self.out_dir)
        launcher.launch(self, None, on_launched)

    @Gtk.Template.Callback()
    def _on_appstack_changes(self, stack, _pspec):
        file_choosers = stack.props.visible_child_name == 'main'

        self.lookup_action('open').set_enabled(file_choosers)
        self.lookup_action('set-dir').set_enabled(file_choosers)

    def _on_open(self, _action, _param):
        def on_selected(chooser, result):
            try:
                files = chooser.open_multiple_finish(result)

                if files is not None:
                    self.load_fonts(files)

            except GLib.Error as e:
                if e.code == Gtk.DialogError.FAILED:
                    print(e.code)

        self.fonts_chooser.open_multiple(self, None, on_selected)

    def _on_set_dir(self, _action, _param):
        def on_selected(chooser, result):
            try:
                selected: Gio.File = chooser.select_folder_finish(result)

                if selected is not None:
                    if os.access(selected.get_path(), os.W_OK):
                        self.out_dir = selected
                        self.directory.set_label(selected.get_basename())
                        self._check_ready_state()
                    else:
                        self.toasts.add_toast(
                            Adw.Toast.new(
                                _(
                                    'You don’t have write access to the selected directory.'  # noqa
                                )
                            )
                        )
            except GLib.Error as e:
                if e.code == Gtk.DialogError.FAILED:
                    print(e.code)

        self.out_dir_chooser.select_folder(self, None, on_selected)

    def _on_google(self, _action, _param):
        dialog = GoogleDialog(self)
        dialog.props.transient_for = self
        dialog.props.modal = True
        dialog.present()

    def _on_generate(self, _action, _param):
        generator = Generator(
            self,
            self.out_dir.get_path(),
            self.model,
            self.options.get_formats(),
            self.options.get_subsetting(),
            self.options.get_font_display(),
        )
        generator.run()

    def _on_back(self, _action, _param):
        if not self.processing:
            self.appstack.set_visible_child_name('main')

    def _on_remove_font(self, _action, param):
        self.model.remove(param.get_uint32())

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
        has_items = self.model.get_n_items() > 0

        self.lookup_action('generate').set_enabled(has_items and self.out_dir)
        self.split.props.show_sidebar = has_items
        self.toolbar_view.props.reveal_bottom_bars = has_items

        if has_items:
            self.fonts_stack.set_visible_child_name('fonts')
            self.toolbar_view.props.top_bar_style = Adw.ToolbarStyle.RAISED
        else:
            self.fonts_stack.set_visible_child_name('empty')
            self.toolbar_view.props.top_bar_style = Adw.ToolbarStyle.FLAT
