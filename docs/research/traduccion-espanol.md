# Traducción al español (T25)

Primer objetivo: todos los menús y el capítulo 1. Las herramientas viven en `tools/es/`; el guion, los lotes, el japonés reconstruido y los archivos generados permanecen en `local/work/guion-es` y nunca se suben. `SAKURA_OWNER_ROOT` apunta a la copia que contiene `local/` (misma convención que las pruebas runtime).

## Método de traducción

1. **Japonés reconstruido**: las tablas japonesas `NNNNTBL.BIN` guardan códigos de 16 bits (`0` fin, `0x0A0D` salto, `c` = glifo `c-1` de `NNNNKNJ.BIN`, 16×16 a 4 bpp). Los glifos se identifican por MD5 y se transcriben una vez a mano; `tools/es/japones.py` regenera el guion alineado con el inglés (mismos IDs y número de registros). Capítulo 1: 3.971 registros, 1,2 % de glifos dudosos. Los combates (`SAKURA2/M##MES.BIN` + `.FNT`) usan el mismo esquema.
2. **Inglés v2.1** como adaptación de referencia, revisada por humanos.
3. **Español**: neutro (ustedes, sin voseo); giro leve de España solo si mejora el modismo. Pasos: traducción por lotes (~330 textos únicos en orden de guion), revisión línea a línea japonés → inglés → español, unificación de términos y trato en la guía de estilo privada, validación (`tools/es/validar_lote.py`). En el capítulo 1 la revisión con japonés cambió entre un 25 % y un 70 % de las líneas por lote y corrigió errores del inglés (休演日 = día sin función, 大将 = general de ejército, 人を呼びますわよ = «llamaré a alguien», dialecto de Osaka de Kohran, juego 舞台/部隊 resuelto con «compañía»).

## Diálogo y combate

- Fuentes del parche inglés: CP1252 completo con acentos (diálogo 16×16; combate 8×12, 255 glifos). No hace falta dibujar glifos.
- Límite: 30 caracteres × 4 líneas. Ajuste automático; solo LIPS y menús de elección llevan saltos explícitos.
- `tools/es/tablas.py`: cabecera `>II`, entradas `>II` (id, offset), registro `>HH` + texto CP1252 par terminado en `00 00`, pie de vocales de sincronía labial intacto. Reproduce byte a byte las 56 tablas inglesas.
- `tools/es/combate.py`: texto en palabras de 16 bits CP1252, salto `0x0A0D`; reproduce byte a byte las 13 tablas.
- `tools/es/iso.py`: copia la ISO inglesa preparada y mueve todas las `*TBL.BIN` y `*MES.BIN` a ranuras fijas de 128 KiB al final; los demás archivos se sustituyen en su sitio con el mismo tamaño. Los LBA no cambian entre builds, así que los savestates de una ISO española siguen valiendo. El juego localiza los archivos por el directorio ISO (el parche inglés ya reconstruyó la imagen).
- Un savestate contiene la tabla ya cargada: para ver texto nuevo hay que partir de un estado anterior a esa carga.

## Menús

Compresión LZ propia (rutina SH-2 `0x0600A164`), implementada en `tools/es/red_lz.py` y verificada con todos los flujos conocidos. Al reinsertar, un flujo solo puede ocupar su longitud original más el relleno de ceros que ya lo seguía: detrás suele haber paletas o tablas.

| Pantalla | Datos | Colocación |
| --- | --- | --- |
| Título (Program) | `LOGO.SH2`+0xFF20, tiles 16×16 4 bpp | Grupos de piezas `x,-8,16,16,char` en `LOGO.SH2`+0x6086 (punteros en +0x6234, contadores `08 05 08 07 07 08`); cada pieza apunta a cualquier tile. |
| Rótulos del título | Marco 8 bpp `LOGO.SH2`+0x10808; «Press Start» 4 bpp en `+0x25410`+81760 | Pintados: se recomponen con las letras del propio parche inglés (d = b reflejada; s dibujada igual). |
| Intermedio | `ICATALL.DAT`+0x2800 | Listas de tiles de longitud fija (5, 5, 6) en `SAKURA`+0x5F5C8. |
| Opciones y mandos | `SAKURA`+0x5B320 y +0x59878; marco +0x5AE38 | Tablas de piezas en `SAKURA` (~0x59C70–0x5ACB0): cada palabra española se dibuja en los mismos tiles que la inglesa. |
| Carga/guardado | Fuente de pares 8×16 (DTE) `SAKURA`+0x5C654, 144 tiles | Cadenas de tiles base 1 terminadas en 0 en `SAKURA`+0x5A09E..0x5A34A, casi todas con puntero (`0x0605xxxx`, carga en 0x06004000). Los botones usan ids fijos: Copy [90,4,95], Del [102,41], Yes [34,6], No [95,133,95]. |
| Estado (stats) | `ICATALL.DAT`+0x13800, 48 tiles (16×16 4 bpp) | Tiles 0-16: nombres de personaje (no se traducen). 17-18 High, 20-21 Spirits!, 22-24 Normal, 25-26 Mood, 27-29 Terrible, 30-31 Atk, 32-33 Def, 34-35 Mov; el resto son `+ - 0-9`. |
| Marco de carga (File/System RAM) | `SAKURA`+0x5E190..0x5EB4C (288×184, 4 bpp) rótulos pintados, no tiles | «File 1/2/3» en cajas (196,y,60,16) con y=40/80/120; «System RAM» en (2,162,108,16); mismo `rotulos.replace_text` que la pestaña «Options». |
| Barra de combate (solo WKL01, único escenario del capítulo 1) | `SAKURA2/WKL01.BIN`+0x339A8 (VRAM1 0x4000), sprites 4 bpp sin comprimir, 28 piezas de 16/24×16px | 25 palabras (los últimos 3 son iconos, intactos); fuente CENTURY.TTF a 9pt (la de 15pt usada en otras pantallas no entra en estas celdas), binarizada a 2 tonos (tinta índice 3, borde 1) porque el sprite no usa el degradado de 15 pasos de las tiras LZ. |

Reglas de texto en menús: misma letra que el inglés (Century para la serif, Georgia Bold comprimida para el título); cuatro niveles de tinta [1, 5, 9, 13] para que cada flujo quepa; si una palabra exige comprimirla por debajo del 85 %, se usa su abreviatura («Cancel.», «Habl.», «Cop.», «Bor.»).

## Pruebas

- `tests/test_es_herramientas.py`: LZ de ida y vuelta, tablas y combate sintéticos, y reconstrucción exacta de todas las tablas del disco del propietario si está disponible.
- `tests/test_es_output_safety.py`: prueba límites de la ISO, escritura atómica y conservación de discos, estados y perfiles de entrada con datos sintéticos.
- `tools/es/parchear_estado.py`: aplica los datos españoles a la RAM/VRAM de un savestate inglés para revisar un menú en segundos; no sustituye a un arranque real.
- Verificado en el runtime (AOT estricto, 0 interpretados): prólogo y encuentro con Sakura en español desde la ISO española, combate del capítulo 1 en español, título y pantalla de carga desde arranque en frío; intermedio y opciones mediante estados parcheados.

## Modo español en el launcher

Ya funciona sin tocar código: `tools/es/construir_disco_es.py` genera `local/prepared/disc1-es` y `tools/es/perfil_es.py` crea un perfil aparte (`local/profiles/espanol`, copia del perfil base con `[game] disc=` apuntando al disco español) y el acceso local «Jugar en español.bat». Verificado con la build `v0.2-ch1-preview`: el launcher arranca el disco español y el título muestra «Pulsa Start».

Las herramientas de línea de comandos guardan los discos, estados de prueba y perfiles bajo `SAKURA_OWNER_ROOT/local`. El constructor verifica la ISO en un archivo temporal antes de publicar la imagen. Al repetir la creación del perfil se actualiza solo `[game] disc` en el INI del launcher y se conservan los ajustes y partidas del perfil. El acceso de Windows usa UTF-8 y admite rutas con espacios y caracteres Unicode; para reproducciones automatizadas con límite de tiempo, ejecuta el runtime directamente con `--disc`, `--settings` y `--backup`.

Opción integrada propuesta para el launcher (dependencia, requiere coordinar propiedad del SDK):

- Selector «Idioma: English / Español» en la tarjeta del disco; se guarda en `launcher.ini` (`[game] language=es`).
- Con `es`, `find_nearby` prueba primero `local/prepared/disc1-es/game.cue`, `game/disc1-es/game.cue` y `disc1-es/game.cue`; si no existe, el selector aparece desactivado con el texto «Falta el disco en español (tools/es/construir_disco_es.py)».
- `check_disc` acepta el disco español: el código del juego es idéntico al inglés; solo cambian tablas, menús y el programa principal en zonas de datos.
- Partidas: el formato no cambia; compartir o separar carpetas es decisión del propietario (el perfil separado de `perfil_es.py` las separa).
- El release público nunca incluye el disco español: es una salida local del propietario, igual que el disco inglés preparado.

## Pendiente

Barra de combate de los escenarios 2–22 (`WKL02..WKL22.BIN`: el offset del bloque de sprites no es el mismo que en WKL01 y falta ubicarlo por archivo), rótulo de episodio (`TITLE1.BIN`), pantalla LOADING (ambos son arte VDP2 pintado a mano, no tiles de texto), menú extra (`OMALL.DAT`: 271 tiles de pares DTE con tablas de punteros propias, es un lote de traducción nuevo), revisión del texto HD con el español y opción de idioma en el launcher. Los capítulos 2–10 siguen el mismo método.
