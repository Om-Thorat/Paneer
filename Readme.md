# Paneer 🍲

A framework to build desktop applications using web technologies and Python 🐍.

Uses the internal webview to render UI and python for the logic layer. Currently in **very very** early stages of development.

## Quick Start

1. **Install**
   Dependencies needed for your platform:

   - Fedora:  `sudo dnf install python3-devel gobject-introspection-devel pkgconf-pkg-config cairo-gobject-devel gtk4 webkitgtk6.0`

   - Arch Linux: `sudo pacman -S python gobject-introspection pkgconf cairo gtk4 webkitgtk-6.0`

   - Debian:  `sudo apt install python3-dev libgirepository1.0-dev pkg-config libcairo2-dev libgtk-4-dev libwebkit2gtk-6.0-dev`

   > Note: NodeJS, NPM must be installed beforehand.

   Then install paneer via pip:
   ```bash
   pip install paneer
   ```

2. **Create a project**
   ```bash
   paneer create
   ```

3. **Run in development**
   ```bash
   paneer run
   ```

4. **Build for release**
   ```bash
   paneer build
   ```

## Supported Platforms

- **Linux**: support for creating windows and building executables
- **Windows**: support for creating windows and building executables
- **macOS**: Not yet supported

> basically plans to be [Tauri](https://github.com/tauri-apps/tauri) but for Python with much less features and much less stability!