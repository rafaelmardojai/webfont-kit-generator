# Copyright 2021 Rafael Mardojai CM
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import os
import re
from urllib.parse import urlparse, parse_qs

from gettext import gettext as _
from gi.repository import Adw, Gdk, Gio, GLib, Gtk, Soup


GOOGLE_API_URL = 'https://www.googleapis.com/webfonts/v1/webfonts?key={}'
XDG_DATA_DIR = os.path.join(GLib.get_user_data_dir(), 'webfont-kit-generator')
DATA_FILE = os.path.join(XDG_DATA_DIR, 'google-fonts.json')


@Gtk.Template(
    resource_path='/com/rafaelmardojai/WebfontKitGenerator/google.ui'
)
class GoogleDialog(Adw.Dialog):
    __gtype_name__ = 'GoogleDialog'

    stack: Gtk.Stack = Gtk.Template.Child()
    url_entry: Gtk.Entry = Gtk.Template.Child()
    error_revealer: Gtk.Revealer = Gtk.Template.Child()
    error_label: Gtk.Label = Gtk.Template.Child()
    download_btn: Gtk.Button = Gtk.Template.Child()
    progress: Adw.StatusPage = Gtk.Template.Child()
    progressbar: Gtk.ProgressBar = Gtk.Template.Child()

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)

        self.window = window
        self.settings = self.window.options.settings
        self.cancellable = Gio.Cancellable.new()
        self.session = Soup.Session()
        self.session.set_user_agent('Webfont Kit Generator')
        self.errors = []
        # Google Fonts
        self.google_sha = ''
        # Families to lockup
        self.families = {}
        # Progress
        self.total = 0
        self.pending = 0
        # Files to import
        self.files = []

    def load_fonts_data(self):
        # Loading feedback
        self.stack.set_visible_child_name('loading')
        self.progressbar.set_text('')
        self.progress.set_title(_('Loading Google Fonts Database'))
        GLib.timeout_add(50, self._on_progressbar_timeout, None)

        # Get data from Google
        api_key = self.settings.get_string('google-api-key')
        api_url = GOOGLE_API_URL.format(api_key)
        message = Soup.Message.new('GET', api_url)

        if self._local_data_exists():
            request_headers = message.get_request_headers()
            request_headers.append(
                'If-None-Match', self.settings.get_string('google-fonts-sha')
            )

        self.session.send_and_read_async(
            message, 0, self.cancellable, self.on_google_response, message
        )

    def on_google_response(self, session, result, message):
        failed = True
        try:
            response = session.send_and_read_finish(result)
            data = self._read_response(response)
            status = message.get_status()
            status_code = message.props.status_code
            response_headers = message.get_response_headers()

            print(f'Google Fonts Response Status {status.get_phrase(status_code)}')

            if status == Soup.Status.OK and 'kind' in data:
                try:
                    if not self._local_data_exists():
                        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

                    # Save to data file
                    with open(DATA_FILE, 'w') as outfile:
                        json.dump(data['items'], outfile, indent=2)

                    # Save ETag
                    self.settings.set_string(
                        'google-fonts-sha',
                        response_headers.get_one('ETag') or '',
                    )

                    self.find_on_data(data['items'])
                    failed = False
                except Exception as exc:
                    print(exc)

            elif (
                status == Soup.Status.NOT_MODIFIED or self._local_data_exists()
            ):
                self.find_on_data()
                failed = False

        except GLib.GError as exc:
            print(exc)

        if failed:
            error = _('Couldn’t download the Google Fonts data.')
            self.errors.append(error)
            self.terminate_dialog()

    def find_on_data(self, data=None):
        if not data:
            data = self._get_local_data()

        files = {}  # Where files to download will be stored
        for family in self.families:
            # Filter data with wanted families
            results = list(
                filter(lambda x: x['family'] == family['name'], data)
            )

            if results:
                results = results[0]  # Get first result
                for variant in family['variants']:  # Check for wanted variants
                    if variant in results['files']:  # If variant available
                        # Store variant files to download
                        if family['name'] not in files:
                            files[family['name']] = {}
                        name = ' '.join([family['name'], variant])
                        files[family['name']][name] = results['files'][variant]
                        # Increase count of total files to download
                        self.total += 1
                    else:  # If variant not available
                        # Save error to show it after dialog is terminated
                        error = _(
                            'Couldn’t find the {variant} variant for {family_name}.'  # noqa
                        )
                        error = error.format(
                            variant=variant, family_name=family['name']
                        )
                        self.errors.append(error)
            else:
                # If no family found, add error to list
                error = _('Couldn’t find the {family_name} font family.')
                error = error.format(family_name=family['name'])
                self.errors.append(error)

        if files:
            # Download found files
            self._download_files(files)
        else:
            # If not files found at all, show general error and terminate
            self.errors = [_('Couldn’t find any fonts for the given url.')]
            self.terminate_dialog()

    def parse_api_v1(self, query: str) -> list[dict[str, str | list[str]]]:
        result = []
        query: dict = parse_qs(query)

        if 'family' in query:
            families = query['family'][0].split('|')

            for family in families:
                family = family.split(':')

                if len(family) == 2:
                    name = family[0]
                    variants = family[1].split(',')

                    result.append({'name': name, 'variants': variants})

        return result

    def parse_api_v2(self, query: str) -> list[dict[str, str | list[str]]]:
        results = []
        query: dict = parse_qs(query)

        if 'family' in query:
            for family in query['family']:
                # Parse family_name, axis_tag_list, axis_tuple_list
                data = re.split(':|@', family)

                if len(data) == 1:
                    results.append({'name': data[0], 'variants': ['regular']})

                elif len(data) == 3:
                    result = {}
                    result['name'] = data[0]
                    # axis_tag_list = data[1].split(',')
                    variants = []

                    for variant in data[2].split(';'):
                        variant_data = variant.split(',')
                        variant_id = ''

                        # Variant only has weight data
                        if len(variant_data) == 1:
                            if variant_data[0] == '400':
                                variant_id = 'regular'
                            else:
                                variant_id = variant_data[0]

                        # Variant has weight and italic data
                        elif len(variant_data) == 2:
                            # Is italic
                            if variant_data[0] == '1':
                                if variant_data[1] == '400':
                                    variant_id = 'italic'
                                else:
                                    variant_id = variant_data[1] + 'italic'
                            else:
                                if variant_data[1] == '400':
                                    variant_id = 'regular'
                                else:
                                    variant_id = variant_data[1]
                        variants.append(variant_id)

                    result['variants'] = variants
                    results.append(result)
                else:
                    continue

        return results

    def invalid_url(self):
        self.url_entry.add_css_class('error')
        self.download_btn.set_sensitive(False)
        self.error_label.set_text(_('Please set a valid url'))
        self.error_revealer.set_reveal_child(True)

    def valid_url(self):
        self.url_entry.remove_css_class('error')
        self.error_revealer.set_reveal_child(False)
        self.download_btn.set_sensitive(True)

    def terminate_dialog(self, cancel=False):
        if not cancel:
            # Load downloaded files
            if self.files:
                self.window.load_fonts(self.files)

            # Show found errors
            for error in self.errors:
                error = Adw.Toast.new(error)
                self.window.toasts.add_toast(error)

        self.close()

    def _download_files(self, files):
        def on_file_downloaded(session, result, user_data):
            (family, name) = user_data
            progress_text = _('Downloading {name}')
            self.progress.set_title(progress_text.format(name=family))

            failed = True
            try:
                font_bytes = session.send_and_read_finish(result)
                if font_bytes:
                    (font, _iostream) = Gio.File.new_tmp(None)
                    outstream = font.replace(
                        None, False, Gio.FileCreateFlags.NONE, None
                    )
                    outstream.write_bytes_async(
                        font_bytes,
                        0,
                        self.cancellable,
                        on_file_writed,
                        (name, font),
                    )
                    failed = False
            except GLib.GError as exc:
                print(exc)
                self.pending -= 1

            if failed:
                error = _('Couldn’t download the font file for {name}.')
                error = error.format(name=name)
                self.errors.append(error)

        def on_file_writed(outstream, result, user_data):
            (name, font) = user_data
            failed = True
            self.pending -= 1
            try:
                outstream.write_bytes_finish(result)
                outstream.close()
                self.files.append(font)
                failed = False
            except GLib.GError as exc:
                print(exc)

            if failed:
                error = _('Couldn’t write the font file for {name}.')
                error = error.format(name=name)
                self.errors.append(error)

            if not self.pending:
                self.terminate_dialog()

        self.pending = self.total
        self.progressbar.set_text(None)

        for family, variants in files.items():
            for name, url in variants.items():
                message = Soup.Message.new('GET', url)
                self.session.send_and_read_async(
                    message,
                    0,
                    self.cancellable,
                    on_file_downloaded,
                    (family, name),
                )

    def _get_local_data(self):
        data = None
        try:
            with open(DATA_FILE) as json_file:
                data = json.load(json_file)
        except Exception as exc:
            print(exc)
        return data

    def _local_data_exists(self):
        return os.path.exists(DATA_FILE)

    @Gtk.Template.Callback()
    def _on_download_clicked(self, _button):
        url = self.url_entry.get_text()
        parsed = urlparse(url)

        families = []
        if parsed.path == '/css':
            families = self.parse_api_v1(parsed.query)
        elif parsed.path == '/css2':
            families = self.parse_api_v2(parsed.query)

        self.families = families
        if self.families:
            self.load_fonts_data()
        else:
            self.invalid_url()

    @Gtk.Template.Callback()
    def _on_entry_changed(self, _entry):
        url = self.url_entry.get_text()

        if url:
            self.url_entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, 'edit-clear-symbolic'
            )

            parsed = urlparse(url)
            if parsed.netloc == 'fonts.googleapis.com':
                if parsed.path == '/css' or parsed.path == '/css2':
                    self.valid_url()
                else:
                    # Unknown API path
                    self.invalid_url()
            else:
                # No API url
                self.invalid_url()
        else:
            self.url_entry.remove_css_class('error')
            self.error_revealer.set_reveal_child(False)
            self.url_entry.set_icon_from_icon_name(
                Gtk.EntryIconPosition.SECONDARY, 'edit-paste-symbolic'
            )

    @Gtk.Template.Callback()
    def _on_cancel_clicked(self, _button):
        if not self.cancellable.is_cancelled():
            self.cancellable.cancel()
            self.terminate_dialog(cancel=True)

    @Gtk.Template.Callback()
    def _on_entry_icon(self, _entry, pos):
        if pos == Gtk.EntryIconPosition.SECONDARY:
            text = self.url_entry.get_text()
            if text:
                self.url_entry.set_text('')
            else:
                self._paste_text()

    def _paste_text(self):
        clipboard = Gdk.Display.get_default().get_clipboard()

        def on_paste(clipboard, result):
            text = clipboard.read_text_finish(result)
            if text is not None:
                self.url_entry.set_text(text)

        clipboard.read_text_async(None, on_paste)

    def _on_progressbar_timeout(self, _data):
        if self.total and self.pending:
            progress = self.total - self.pending
            progress = progress / self.total
            self.progressbar.set_fraction(progress)
        else:
            self.progressbar.pulse()
        return True

    def _read_response(self, response):
        response_data = {}
        try:
            if response.get_data():
                response_data = json.loads(response.get_data()) if response else {}
        except Exception as exc:
            print('Read error:', exc)
        return response_data
