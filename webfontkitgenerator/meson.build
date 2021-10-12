subdir('resources')
pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'webfontkitgenerator')

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'webfontkitgenerator.in',
  output: 'webfontkitgenerator',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

webfontkitgenerator_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'font.py',
  'options.py',
  'generator.py',
  'loader.py',
  'log.py',
  'sourceview.py',
]

install_data(webfontkitgenerator_sources, install_dir: moduledir)
