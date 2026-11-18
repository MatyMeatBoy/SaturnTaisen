# Parches de idioma de SaturnTaisen

El launcher los aplica en tu PC sobre una copia de **tus propios discos** (Sakura Taisen, Sega Saturn, Japón, GS-9037 V1.005; originales o ya parcheados con la traducción inglesa v2.1, que se reconoce y se usa tal cual). No se distribuyen discos, BIOS ni archivos del juego: cada parche solo contiene diferencias y no sirve sin tus discos.

| Capa | Archivos | Qué hace |
| --- | --- | --- |
| Inglés v0.1 Taisen | `ingles-v0.1-discN.xdelta` | Disco original → base inglesa. |
| Español v0.1 Taisen | `espanol-v0.1-discN.xdelta` | Base inglesa → español. No depende de los vídeos: se aplica igual con el contenedor original o con el subtitulado. |
| Vídeos subtitulados | `videos-en-v0.1-discN.xdelta` | Opcional: sustituye en su sitio el contenedor de vídeo `/SAKURA4` por el subtitulado en inglés. Sirve para los dos idiomas. |

`parches.json` guarda los SHA-256 de entrada y salida de cada capa; `preparar-juego.exe` los comprueba todos.

## Inglés v0.1 Taisen

Es la **traducción inglesa v2.1 de Sakura Wars para Saturn**, reempaquetada para este port: el resultado es idéntico al de aquel parche salvo que el contenedor de vídeo conserva los bytes originales (de ahí su tamaño reducido); con la capa de vídeos subtitulados el disco resultante es byte a byte el del parche v2.1. Todo el mérito de esa traducción es de su equipo:

- **Dirección del proyecto:** NoahSteam
- **Hacking:** NoahSteam, TrekkiesUnite118
- **Edición principal:** cj_iwakura, BowlOfLentils
- **Edición:** CrouchingMouse, Schlomo, MatatabiMitsu
- **Dirección de traducción:** MatatabiMitsu, Schlomo, CrouchingMouse, Nezumi
- **Equipo de traducción:** Kate Robinson, Eien Ni Hen, Cal Hampton, Eben Williams, Margie Obendorf, Sarah Dopierala, Mason van Dyk
- **Gráficos:** Joqu, Ibnu, NoahSteam, TrekkiesUnite118
- **Pruebas:** BowlOfLentils, cj_iwakura, CrouchingMouse, PsionicStorm, Paragonias, burntends

SaturnTaisen no está afiliado a ese equipo. Si formas parte de él y prefieres que esta base no se incluya, abre una incidencia en el repositorio y se retirará.

## Español v0.1 Taisen

Traducción al español de SaturnTaisen (MatyMeatBoy, con asistencia de IA declarada): diálogos de los diez capítulos de ambos discos, textos de combate y menús redibujados (título, opciones, cargar/guardar, estado y barra de órdenes). Se tradujo desde el inglés y se revisó contra el japonés reconstruido para hablante, tratamiento, género, términos y chistes. Siguen en inglés los rótulos de episodio, la pantalla LOADING, el menú de extras y los subtítulos de vídeo. Método y límites: `docs/research/traduccion-espanol.md`.

## Herramientas incluidas

- **xdelta3** 3.2.2 (Joshua MacDonald y colaboradores, Apache-2.0) aplica las capas y verifica sus sumas.
- **unshield** 1.6.2 (David Eriksson y colaboradores, MIT) lee los cabinets de la edición de PC para el mod HD.

Sakura Wars / Sakura Taisen es obra de SEGA y RED; sus marcas e imágenes pertenecen a sus titulares.
