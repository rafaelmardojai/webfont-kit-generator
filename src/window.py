# Copyright 2020-2021 Rafael Mardojai CM
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
    fonts_box = Gtk.Template.Child()
    fonts_stack = Gtk.Template.Child()
    fonts_list = Gtk.Template.Child()
    browse = Gtk.Template.Child()
    directory = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.processing = False
        self.options = Options()
        self.outpath = None
        self.outuri = None
        self.log = Log(self.progressbar_label)

        self.setup_widgets()

        self.browse.connect('clicked', self.set_outpath)

        self.model = Gio.ListStore.new(Font)
        self.model.connect('items-changed', self._change_ready_state)
        self.fonts_list.bind_model(self.model, self._create_font_widget)

        self.btn_generate.connect('clicked', self.on_generate)

    def setup_widgets(self):
        self.stack.add_titled(self.options, 'options', _('Options'))
        self.stack.child_set_property(self.options, 'icon-name', 'emblem-system-symbolic')

        self.log_column.add(self.log)
        self.log.show_all()

        self.end_html = SourceView()
        self.end_html.set_language('html')
        self.import_html_frame.add(self.end_html)

        self.end_css = SourceView()
        self.end_css.set_language('css')
        self.import_css_frame.add(self.end_css)

        self.open_files.connect('clicked', self.open_generation_dir)

        # Drag and drop
        targetentry = Gtk.TargetEntry.new('text/plain', Gtk.TargetFlags(4), 0)
        self.drag_dest_set(Gtk.DestDefaults.ALL, [targetentry], Gdk.DragAction.COPY)
        self.connect('drag-data-received', self.on_drag_and_drop)

    def on_drag_and_drop(self, _widget, _drag_context, _x, _y, data, _info, _time):
        if self.appstack.get_visible_child_name() == 'main':
            filenames = data.get_text()
            filenames = filenames.split()
            self.load_fonts(filenames)

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
            filechooser.destroy()

            if os.access(path, os.W_OK):
                self.outpath = path
                self.outuri = uri
                self.directory.set_label(name)
                self._change_ready_state()
            else:
                error_dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING,
                    Gtk.ButtonsType.OK, _('Output directory error'))
                error_dialog.format_secondary_text(
                    _("You don't have write access to the selected directory."))
                error_response = error_dialog.run()
                if error_response == Gtk.ResponseType.OK:
                    error_dialog.destroy()

        elif response == Gtk.ResponseType.REJECT:
            filechooser.destroy()

    def open_generation_dir(self, *args):
        Gio.app_info_launch_default_for_uri(self.outuri)

        '''
        fd = os.open(self.outuri, os.O_RDONLY)
        # PyGObject
        bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        proxy = Gio.DBusProxy.new_sync(bus, Gio.DBusProxyFlags.NONE, None,
                                   'org.freedesktop.portal.Desktop',
                                   '/org/freedesktop/portal/desktop',
                                   'org.freedesktop.portal.OpenURI', None)

        proxy.OpenDirectory('(sha{sv})', '', fd, {})
        # dbus-python
        bus = dbus.SessionBus()
        portal = bus.get_object(
            'org.freedesktop.portal.Desktop',
            '/org/freedesktop/portal/desktop'
        )
        iface = dbus.Interface(portal, 'org.freedesktop.portal.OpenURI')
        self._request_path = iface.OpenDirectory(
            '', dbus.types.UnixFd(fd), dbus.Dictionary(signature='sv')
        )
        '''


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

