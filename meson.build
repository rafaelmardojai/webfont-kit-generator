project('webfontkitgenerator',
          version: '1.1.1',
    meson_version: '>= 0.60.0',
  default_options: [ 'warning_level=2',
                   ],
)

i18n = import('i18n')

dependency('glib-2.0')
dependency('gobject-introspection-1.0', version: '>= 1.35.0')
dependency('gtk4', version: '>= 4.12')
dependency('libadwaita-1', version: '>= 1.4')
dependency('libsoup-3.0')
dependency('gtksourceview-5')
dependency('pygobject-3.0', version: '>= 3.40')

subdir('data')
subdir('webfontkitgenerator')
subdir('po')

gnome.post_install(
  gtk_update_icon_cache: true,
  glib_compile_schemas: true,
  update_desktop_database: true,
)
