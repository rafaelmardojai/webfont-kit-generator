pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'webfontkitgenerator')

python = import('python')
gnome = import('gnome')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

gnome.compile_resources('webfontkitgenerator',
  'webfontkitgenerator.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
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
