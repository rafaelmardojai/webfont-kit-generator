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

import codecs
import locale
import logging
import os
import urllib

from gettext import gettext as _
from gi.repository import GLib, Gdk, Gtk, Handy
from threading import Thread

from .options import WfkgOptions
from .font_widget import WidgetFont
from .generator import Generator

LOGGER = logging.getLogger('storiestyper')


@Gtk.Template(resource_path='/com/rafaelmardojai/WebfontKitGenerator/ui/window.ui')
class WebfontkitgeneratorWindow(Handy.ApplicationWindow):
    __gtype_name__ = 'WebfontkitgeneratorWindow'

    appstack = Gtk.Template.Child()
    progressbar = Gtk.Template.Child()

    btn_generate = Gtk.Template.Child()
    btn_add_fonts = Gtk.Template.Child()

    stack = Gtk.Template.Child()
    fonts_stack = Gtk.Template.Child()
    fonts_list = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.processing = False
        self.setup_widgets()

        self.fonts_list.connect('add', self._on_fonts_list_changed)
        self.fonts_list.connect('remove', self._on_fonts_list_changed)

        self.btn_generate.connect('clicked', self.on_generate)

    def setup_widgets(self):
        options = WfkgOptions()

        self.stack.add_titled(options, 'options', _('Output Options'))

    def open_fonts(self, _widget=None):
        otf_filter = Gtk.FileFilter()
        otf_filter.set_name(_('OTF Fonts'))
        otf_filter.add_mime_type('font/otf')
        otf_filter.add_pattern('.otf')
        ttf_filter = Gtk.FileFilter()
        ttf_filter.set_name(_('TTF Fonts'))
        ttf_filter.add_mime_type('font/ttf')
        ttf_filter.add_pattern('.ttf')

        filechooser = Gtk.FileChooserNative()
        filechooser.set_select_multiple(True)
        filechooser.set_transient_for(self)
        #filechooser.set_modal(True)
        filechooser.add_filter(otf_filter)
        filechooser.add_filter(ttf_filter)
        response = filechooser.run()

        if response == Gtk.ResponseType.ACCEPT:
            filenames = filechooser.get_filenames()
            GLib.idle_add(self.load_fonts, filenames)
            #self.load_fonts(filenames)
            filechooser.destroy()
            return

        elif response == Gtk.ResponseType.REJECT:
            filechooser.destroy()

    def load_fonts(self, filenames=None):
        if filenames:
            filename = filenames.pop(0)
            try:
                if os.path.exists(filename):
                    #self.status.push(filename)
                    font_widget = WidgetFont()
                    font_widget.show_all()
                    font_widget.connect('loaded', self.on_loaded, filenames)
                    font_widget.load(filename)
                    self.fonts_list.add(font_widget)

            except Exception as e:
                LOGGER.warning('Error Reading File: %r' % e)

    def on_loaded(self, font_widget, filenames):
        self.load_fonts(filenames)

    def on_generate(self, widget):
        filechooser = Gtk.FileChooserNative()
        filechooser.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        filechooser.set_transient_for(self)
        filechooser.set_modal(True)
        response = filechooser.run()

        if response == Gtk.ResponseType.ACCEPT:
            path = filechooser.get_filename()
            generator = Generator(self, path, self.fonts_list)
            generator.run()
            filechooser.destroy()

        elif response == Gtk.ResponseType.REJECT:
            filechooser.destroy()

    def _on_fonts_list_changed(self, container, widget):
        children = self.fonts_list.get_children()
        children = True if children else False

        self.btn_generate.set_sensitive(children)

        if children:
            self.fonts_stack.set_visible_child_name('fonts')
        else:
            self.fonts_stack.set_visible_child_name('empty')

        
