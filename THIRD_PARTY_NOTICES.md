# Components and licenses

SaturnTaisenFirst distributes its integration code under GPL-3.0-only. The research and modifications do not replace the licenses of its dependencies.

- **satrecomp**, Tommy McLeroy, GPL-3.0-only. Pinned commit and patches in `config/dependencies.json`.
- **recomp-common**, Tommy McLeroy, GPL-3.0-only; some parts of the launcher come from **wiiparty-recomp**, arelkair, GPL-3.0-or-later. Keep their author notices and `THIRD_PARTY_NOTICES.md` when distributing the launcher.
- **Dear ImGui**, Omar Cornut and contributors, MIT. Version and hash pinned by the launcher's CMake.
- **SDL3**, SDL authors, zlib. Its license is distributed alongside the library.
- **Inter**, Rasmus Andersson and contributors, SIL Open Font License 1.1. The font is embedded in the launcher; include its license.
- **zlib**, Jean-loup Gailly and Mark Adler, zlib.
- **GNU libiconv**, GNU authors, LGPL; dynamic library and `COPYING`/`COPYING.LIB` texts included when required by SDL.
- **Python**, Python Software Foundation License; **PyInstaller**, GPL with exception for packaged binaries. The packaged importer carries its notices in the distribution's licenses folder.

The development package must keep the license texts of the components it includes. The repository contains its own sources and reproducible patches; the game's original assets, BIOS, dumps, and saves remain local. Sakura Wars and its images belong to their rights holders; the project is not affiliated with SEGA.
