desktop_file = i18n.merge_file(
  input: 'com.rafaelmardojai.WebfontKitGenerator.desktop.in',
  output: 'com.rafaelmardojai.WebfontKitGenerator.desktop',
  type: 'desktop',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils,
    args: [desktop_file]
  )
endif

appstream_file = i18n.merge_file(
  input: 'com.rafaelmardojai.WebfontKitGenerator.metainfo.xml.in',
  output: 'com.rafaelmardojai.WebfontKitGenerator.metainfo.xml',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'metainfo')
)

appstreamcli = find_program('appstreamcli', required: false)
if appstreamcli.found()
  test('Validate appstream file', appstreamcli,
    args: ['validate', '--no-net', '--explain', appstream_file],
    workdir: meson.current_build_dir()
  )
endif

install_data('com.rafaelmardojai.WebfontKitGenerator.gschema.xml',
  install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
)

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file', compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()]
  )
endif

service_conf = configuration_data()
service_conf.set('bindir', join_paths(get_option('prefix') / get_option('bindir')))
configure_file(
  input: 'com.rafaelmardojai.WebfontKitGenerator.service.in',
  output: 'com.rafaelmardojai.WebfontKitGenerator.service',
  configuration: service_conf,
  install_dir: join_paths(get_option('datadir'), 'dbus-1/services')
)

install_data(
  'com.rafaelmardojai.WebfontKitGenerator.svg',
  install_dir: join_paths(get_option('datadir'), 'icons/hicolor/scalable/apps')
)

install_data(
  'com.rafaelmardojai.WebfontKitGenerator-symbolic.svg',
  install_dir: join_paths(get_option('datadir'), 'icons/hicolor/symbolic/apps')
)
