<img src="brand/icon.svg" alt="Webfont Kit Generator" width="128" height="128" align="left"/> 

# Webfont Kit Generator

Create @font-face kits easily

<br/>

[![Please do not theme this app](https://stopthemingmy.app/badge.svg)](https://stopthemingmy.app) 
[![GNMOME Circle](https://gitlab.gnome.org/Teams/Circle/-/raw/master/assets/button/badge.svg)](https://circle.gnome.org/)

[![GitHub](https://img.shields.io/github/license/rafaelmardojai/WebfontKitGenerator.svg)](https://github.com/rafaelmardojai/WebfontKitGenerator/blob/master/COPYING)
[![Donate](https://img.shields.io/badge/PayPal-Donate-gray.svg?style=flat&logo=paypal&colorA=0071bb&logoColor=fff)](https://paypal.me/RafaelMardojaiCM)
[![Liberapay](https://img.shields.io/liberapay/receives/rafaelmardojai.svg?logo=liberapay)](https://liberapay.com/rafaelmardojai/donate)


## Description
**Webfont Kit Generator** is a simple utility that allows you to generate **woff**, **woff2** and the necessary CSS boilerplate from non-web font formats (otf & ttf).

Webfont Kit Generator also includes a tool to Download fonts from Google Fonts for self-hosting.

Webfont Kit Generator uses [fontTools](https://github.com/fonttools/fonttools) python library under the hood.

## Install
<a href="https://flathub.org/apps/details/com.rafaelmardojai.WebfontKitGenerator"><img width="240" alt="Download on Flathub" src="https://flathub.org/api/badge?svg&locale=en"/></a>

### Third Party Packages

| Distribution | Package | Maintainer |
|:-:|:-:|:-:|
| Ubuntu (PPA) | [`Stable Releases`](https://launchpad.net/~apandada1/+archive/ubuntu/webfontkitgenerator), [`Daily Builds`](https://launchpad.net/~apandada1/+archive/ubuntu/webfontkitgenerator-daily) | [Archisman Panigrahi](https://github.com/apandada1) |
| Arch Linux (AUR) | [`webfontkitgenerator-git`](https://aur.archlinux.org/packages/webfontkitgenerator-git/) | [Archisman Panigrahi](https://github.com/apandada1) |
| Fedora Linux (Copr) | [`webfont-kit-generator`](https://copr.fedorainfracloud.org/coprs/xfgusta/webfont-kit-generator/) | [Gustavo Costa](https://github.com/xfgusta)|

## Building

### Requirements

- Python 3 `python`
- PyGObject `python-gobject`
- GTK4 (>= 4.12.0) `gtk4`
- libadwaita (>= 1.4.0) `libadwaita`
- libsoup (>= 3.0) `libsoup3`
- gtksourceview (>= 5.0) `gtksourceview5`
- Meson `meson`
- Ninja `ninja`
- fontTools `python-fontTools`
- brotli `python-brotli`

Clone and run from GNOME Builder.
Alternatively, you can build with `meson`.
```bash
meson builddir --prefix=/usr/local
sudo ninja -C builddir install
```

### Collect Python deps for flatpak

```bash
build-aux/flatpak-pip-generator  --requirements-file requirements.txt --output=build-aux/python3-requirements
```

## Screenshots

<p align="center">
  <img src="brand/screenshots/1.png"/>
  <img src="brand/screenshots/2.png"/>
  <img src="brand/screenshots/3.png"/>
  <img src="brand/screenshots/4.png"/>
  <img src="brand/screenshots/5.png"/>
</p>

## Translations
Webfont Kit Generator is translated into several languages. If your language is missing or incomplete, please help to [translate Webfont Kit Generator in Transifex](https://www.transifex.com/rafaelmardojai/webfont-kit-generator/).

## Credits
Developed by **[Rafael Mardojai CM](https://github.com/rafaelmardojai)** and [contributors](https://github.com/rafaelmardojai/WebfontKitGenerator/graphs/contributors).

## Donate
If you want to support my work, you can donate me, [here you can find how](https://rafaelmardojai.com/donate/).
