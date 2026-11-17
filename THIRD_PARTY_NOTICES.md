# Componentes y licencias

SaturnTaisenFirst distribuye su código de integración bajo GPL-3.0-only. La investigación y las modificaciones no sustituyen las licencias de sus dependencias.

- **satrecomp**, Tommy McLeroy, GPL-3.0-only. Commit fijado y parches en `config/dependencies.json`.
- **recomp-common**, Tommy McLeroy, GPL-3.0-only; algunas partes del launcher proceden de **wiiparty-recomp**, arelkair, GPL-3.0-or-later. Conservar sus avisos de autor y `THIRD_PARTY_NOTICES.md` al distribuir el launcher.
- **Dear ImGui**, Omar Cornut y colaboradores, MIT. Versión y hash fijados por el CMake del launcher.
- **SDL3**, autores de SDL, zlib. Se distribuye su licencia junto a la biblioteca.
- **Inter**, Rasmus Andersson y colaboradores, SIL Open Font License 1.1. La fuente se integra en el launcher; incluir su licencia.
- **zlib**, Jean-loup Gailly y Mark Adler, zlib.
- **GNU libiconv**, autores de GNU, LGPL; biblioteca dinámica y textos `COPYING`/`COPYING.LIB` incluidos cuando la requiere SDL.
- **Python**, Python Software Foundation License; **PyInstaller**, GPL con excepción para binarios empaquetados. El importador empaquetado lleva sus avisos en la carpeta de licencias de la distribución.

El paquete de desarrollo debe conservar los textos de licencia de los componentes que incluya. El repositorio contiene las fuentes propias y parches reproducibles; los recursos originales del juego, BIOS, dumps y partidas permanecen locales. Sakura Wars y sus imágenes pertenecen a sus titulares; el proyecto no está afiliado a SEGA.
