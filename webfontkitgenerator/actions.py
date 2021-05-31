# Copyright 2020 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gio, GLib, Gtk


class Actions(object):

    def __init__(self):
        actions = [
            {
                'name'  : 'open',
                'func'  : self.on_open,
                'accels': ['<Ctl>o']
            },
            {
                'name'  : 'back',
                'func'  : self.on_back,
                'accels': ['Escape']
            },
            {
                'name'  : 'about',
                'func'  : self.on_about
            }
        ]

        for a in actions:
            if 'state' in a:
                action = Gio.SimpleAction.new_stateful(
                    a['name'], None, GLib.Variant.new_boolean(False))
                action.connect('change-state', a['func'])
            else:
                action = Gio.SimpleAction.new(a['name'], None)
                action.connect('activate', a['func'])

            self.add_action(action)

            if 'accels' in a:
                self.set_accels_for_action('app.' + a['name'], a['accels'])

    def on_open(self, action, param):
        if not self.window.processing:
            self.window.open_fonts()

    def on_back(self, action, param):
        if not self.window.processing:
            self.window.appstack.set_visible_child_name('main')

    def on_about(self, action, param):
        dialog = Gtk.Builder.new_from_resource(
            '/com/rafaelmardojai/WebfontKitGenerator/ui/about.ui'
        ).get_object('about')
        dialog.set_version(self.version)
        dialog.set_transient_for(self.window)
        dialog.set_modal(True)
        dialog.connect('response', lambda dialog, response: dialog.destroy())
        dialog.present()
 
