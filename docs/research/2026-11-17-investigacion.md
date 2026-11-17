# Investigación inicial — 17 de noviembre de 2026

## Conclusión

Hay herramientas AOT SH-2 que permiten investigar una recompilación estática. No se ha encontrado un recomp público confirmado de Sakura Wars 1 para Saturn en las búsquedas realizadas. Sí existe una decompilación del port de Windows y herramientas de ingeniería inversa de la traducción de Saturn. La compatibilidad de cualquiera de los runtimes con Sakura Wars sigue sin probarse.

## Referencias prioritarias

| Proyecto | Tipo y utilidad | Límite relevante |
| --- | --- | --- |
| [NoahSteam/RomHackingTools](https://github.com/NoahSteam/RomHackingTools) | Herramientas del equipo traductor; contiene trabajo específico de Sakura Taisen y Saturn Explorer. Prioridad para entender formatos. | No es una decompilación completa ni un recomp del juego. Revisar licencia por componente. |
| [sakurayaku/re.sakurataisen](https://github.com/sakurayaku/re.sakurataisen) | Traducción francesa para Saturn basada en el trabajo inglés; extracción/inserción y documentación de recursos. | Confirmar licencias antes de reutilizar código. |
| [sakurayaku/sakurayaku-platform](https://github.com/sakurayaku/sakurayaku-platform) | Plataforma de traducción colaborativa. | Su README declara que no tiene licencia de código; no asumir permiso de copia. |
| [CalciumSigma/Sakura_Wars_1-PC-Decompilation](https://github.com/CalciumSigma/Sakura_Wars_1-PC-Decompilation) | Decompilación de ADVcore del port de Windows DVD 2006. Puede ayudar a entender la lógica. | Necesita el ejecutable de PC y herramientas antiguas. No consume directamente nuestros dumps Saturn ni su xdelta. Sus cifras son del autor, no verificadas aquí. |
| [vinheim3/sakuraWars1-disasm](https://github.com/vinheim3/sakuraWars1-disasm) | Desensamblado de Sakura Wars GB, según su README. | Game Boy Color, no el primer Sakura Wars de Saturn. |
| [vs-sr-dev/saturnkit](https://github.com/vs-sr-dev/saturnkit) | Análisis de discos, recompilador SH-2 a C++ y runtime compartido. | Experimental y dependiente de las necesidades de cada juego. Evaluar hardware y overlays usados por Sakura. |
| [callumjenkins/saturn-recomp](https://github.com/callumjenkins/saturn-recomp) | Fork con evolución independiente de saturnkit; AOT SH-2, C++20, SDL3 y comparación con Beetle Saturn. | Funciones VDP2 y hardware aún incompletas según README. MIT con componentes y opción GPL que requieren revisión. |
| [tmcleroy/satrecomp](https://github.com/tmcleroy/satrecomp) | AOT basado en bloques descubiertos mediante ejecución; runtime y herramientas de validación. | La cobertura de trazas no garantiza cubrir todas las ramas. Su README y los repos de ports pueden actualizarse en distinto momento. |
| [sonsegajp/SaturnRecomp](https://github.com/sonsegajp/SaturnRecomp) | Runtime de investigación e inspección de discos. | El README actual aclara que el camino jugable usa intérprete y que no hay emisor AOT público completo. No elegirlo como prueba de recomp estático terminado. |
| [mattkuhnQAAI/sfiii-native](https://github.com/mattkuhnQAAI/sfiii-native) | Referencia de RPG Saturn con perfiles de traducción, overlays y guardados. | El autor limita expresamente la validación de campañas completas. No extrapolar compatibilidad a Sakura. |
| [vs-sr-dev/pc-deepfear](https://github.com/vs-sr-dev/pc-deepfear) | Referencia de carga, streaming y un juego multidisco sobre saturnkit. | No se ha verificado aquí su cambio de disco ni juego completo. |
| [vs-sr-dev/pc-virtualhydlide](https://github.com/vs-sr-dev/pc-virtualhydlide) | Caso de recompilación con múltiples programas SH-2. | Aportación específica de otro juego. |
| [yaz0r/Azel](https://github.com/yaz0r/Azel) | Ingeniería inversa de Panzer Dragoon Saga en C++. | Reimplementación específica, no herramienta universal de recomp. |
| [Xeeynamo/sotn-decomp](https://github.com/Xeeynamo/sotn-decomp) | Decompilación multiplataforma con objetivo Saturn. | Separar progreso Saturn del de PSX/PSP. |
| [Panzer Dragoon Trilogy, devMiyax](https://www.yabasanshiro.com/pds-recompile) | Builder anunciado por el autor para la trilogía; incluye los cuatro discos de Saga. | Referencia de experiencia de usuario. Esta investigación no audita su implementación ni su compatibilidad. |

## Catálogo ampliado

`projects.json` conserva enlaces, categorías, descripciones y metadatos del repositorio consultados mediante GitHub. Incluye más ports Saturn y traducciones de otras versiones de Sakura. Estas últimas sirven como contexto de formatos, no como reemplazo de la versión Saturn. Las entradas sin lectura técnica detallada se identifican como descubrimiento; no se les atribuye compatibilidad comprobada.

## Material local observado

- Dos discos identificados por los nombres como edición japonesa 6M, cada uno con pista de datos MODE1/2352 y pista de audio CD-DA separada. El nombre no es verificación de edición; falta contrastar hashes y cabeceras.
- Pistas de datos: disco 1, 635917296 bytes; disco 2, 617896272 bytes. Pistas de audio: 5357856 bytes cada una.
- Dos xdelta y dos CUE del paquete etiquetado v2_1. El readme conserva historial hasta v2.01; no deducir la versión efectiva solamente de la carpeta.
- El readme indica extraer datos de usuario con IsoBuster antes de aplicar xdelta. Los CUE del parche usan MODE1/2048 y WAV.
- Hay notas de traducción ODT; todavía no se han inspeccionado.
- Los originales no se han modificado; aún no se ha aplicado ni validado el parche.

## Incertidumbres que deben resolverse experimentalmente

## BIOS aportadas después del inventario inicial

La carpeta local `Sega Saturn BIOS` contiene once archivos de 524288 bytes. Se calcularon sus hashes sin modificar los originales. `Bios Saturn 1.01 (J) [!].bin` coincide con la BIOS japonesa `sega_101.bin` de [la documentación oficial de Mednafen](https://mednafen.github.io/documentation/ss.html), SHA-256 `dcfef4b99605f872b6c3b6d05c045385cdea3d1b702906a0ed930df7bcb7deac`. También está presente el hash documentado para US/Europa. Esto verifica la identidad de esos archivos, no todavía el arranque del juego. No hace falta otro dump de BIOS para iniciar la referencia.

## Comprobaciones pendientes

1. Reconstrucción exacta de la entrada esperada por xdelta, incluidos sectores finales. No desactivar comprobaciones para hacer pasar un parche incompatible.
2. Código y overlays añadidos por el parche, no solo recursos traducidos.
3. Cobertura del runtime: dos SH-2, sincronización, VDP1/2, audio, vídeo, CD y guardado.
4. Proporción de pantalla y modos de resolución efectivamente usados por el juego; pixel aspect y píxeles cuadrados no son equivalentes automáticamente.
5. Mecanismo real del paso de disco 1 a 2: guardado, montaje, reinicio o lectura de continuación. No automatizar por temporizadores o capturas de texto.

## Método y alcance

Búsquedas web y GitHub: Sakura Taisen, SakuraWars, Sakura Saturn, Sakura reverse engineering/decompilation; Saturn recomp/decompilation y saturnkit. Se consultaron fuentes primarias y READMEs de los candidatos prioritarios. Las búsquedas no son prueba de inexistencia y no se ha auditado exhaustivamente el código de todos los repositorios. No se descargaron juegos ni BIOS de Internet.
