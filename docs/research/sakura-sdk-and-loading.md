# SDK de Sakura y cargas: evidencia para v0.2

## Componentes identificados

El inventario reproducible `tools/audit_sdk.py` lee las cuatro imágenes locales sin extraer ni modificar archivos. Los resultados están en `sakura-sdk-inventory.json` y distinguen componentes embebidos de ejecución confirmada.

- `/SAKURA`, cargado inicialmente en `06004000`, contiene `GFS_SBL Version 2.10 1996-02-01` y `CPK Version 1.23 1996-04-09`.
- `/SAKURA2/CPK.BIN` contiene CPK 1.20; su presencia no demuestra que sustituya al reproductor residente en una escena concreta.
- `SLG.BIN`, su alias `0SLG.BIN` y varios minijuegos contienen GFS_SBL 2.10.
- `EVT01.BIN` contiene 292 entradas de símbolos `.text`, incluidas funciones CDC, GFS, DMA y nombres propios del motor; `EVT18.BIN` del disco 2 contiene otras 136. Son listados conservados dentro de recursos, **no símbolos autenticados de la revisión activa**. Sus direcciones requieren cotejo antes de usarlas como hooks.

Esto fundamenta estudiar SBL/GFS y Cinepak. El nombre `SLG.BIN` no prueba uso de la biblioteca SGL: es un módulo del juego, no una identificación de SDK.

## Contratos que deben conservarse

El [manual de GFS de Sega](https://antime.kapsi.fi/sega/files/ST-136-R2-093094.pdf) diferencia número de sectores solicitado, máximo de bytes del destino y avance del puntero. `GFS_NwFread` solicita trabajo; `GFS_NwExecServer` progresa las solicitudes, por orden. La [referencia de funciones](https://www.infochunk.com/saturn/segahtml_en/prgg/prg1/file/hon/p08_14.htm) describe finalización/error del servidor. No convertir una operación asíncrona en un éxito inmediato sin verificar sus consumidores.

La [documentación histórica de Sega](https://docs.exodusemulator.com/Archives/SegaDTSMirror/software/soft.htm) distingue SBL y SGL. Los toolchains modernos que adaptan SGL a GCC no demuestran qué versión enlazó Sakura.

## Casos de otros proyectos

- [Fighters Megamix](https://github.com/tmcleroy/fighters-megamix-recomp/releases): restauró Fread por la unidad guest tras fallos de efectos de sonido con lectura inmediata; las cargas aumentaron aproximadamente dos segundos según su autor. No ejecutar ese juego ni presentar sus cifras como mediciones de Sakura.
- Deep Fear: la documentación ya fijada en `2026-11-17-casos-recomp.md` describe una paleta sobrescrita antes de VBlank por un CD demasiado rápido.
- Hyper Duel: las correcciones de GFS/CD-DA documentadas allí distinguen pista, FAD, pregap y 588 muestras por sector de audio.

## Primera optimización local

Caché del host de hasta cuatro bloques de 64 KiB, asignados bajo demanda; conserva comandos, planificación, tiempos guest y contenido de sectores. Serializa las operaciones seek/read, invalida al abrir otra imagen y mantiene datos WAV fuera del PCM entregado. El modo `SATRECOMP_DISC_CACHE=0` proporciona comparación sin caché. `SATRECOMP_DISC_IO_STATS=1` informa solicitudes, aciertos, lecturas físicas de biblioteca, bytes y tiempo de I/O del host. No confundir estas lecturas con accesos físicos al SSD: el sistema operativo también mantiene su propia caché.

La prueba sintética sirve 80 sectores con tres lecturas de biblioteca y comprueba concurrencia, límites y reapertura. Esto **no demuestra aún una reducción del tiempo de carga percibido en Sakura**; requiere comparaciones repetidas y hashes con la caché activada/desactivada. Acelerar el reloj CD queda pendiente de investigación específica por escena.

## Fuente inglesa

Las herramientas de [NoahSteam](https://github.com/NoahSteam/RomHackingTools/blob/master/SakuraTaisen/SakuraTaisen.cpp) documentan índices ASCII, espaciado 8×12 y tiles narrativos 16×16; la traducción de SLG usa tiles 8×12. Los 56 KNJ del disco inglés 1 tienen el mismo SHA-256 `7d373f80bb217b153a7ba0c94d948a41192acffbf38cfeb0ea13df586e6eca57`. Una captura real de Iris confirma sprites 16×16 con avance de 8 píxeles y códigos de textura consistentes con esa tabla. Usar comprobación exacta de atlas/tiles y comandos reales; no OCR por fotograma ni inferencias basadas únicamente en el color de los píxeles.
