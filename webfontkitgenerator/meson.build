pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'webfontkitgenerator')

python = import('python')
gnome = import('gnome')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

blueprints = custom_target('blueprints',
  input: files(
    'google.blp',
    'options.blp',
    'window.blp',
    'gtk/help-overlay.blp',
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources('webfontkitgenerator',
  'webfontkitgenerator.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: blueprints,
)

webfontkitgenerator_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'font.py',
  'options.py',
  'generator.py',
  'google.py',
  'loader.py',
  'log.py',
  'sourceview.py',
]

install_data(webfontkitgenerator_sources, install_dir: moduledir)

configure_file(
  input: 'webfontkitgenerator.in',
  output: 'webfontkitgenerator',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)
