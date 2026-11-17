# Saturn / PC / HD: alcance solicitado

El usuario añadió este alcance el 17/11/2026 durante el desarrollo de v0.2 y confirmó explícitamente reutilizar y adaptar la traducción inglesa Saturn.

## Experiencia deseada

- Un launcher permite elegir la recompilación Saturn o la versión PC.
- Al importar ambas versiones compatibles, ofrece Saturn con un pack HD adaptado de los recursos PC.
- Traducción inglesa, pack HD y fuente nítida son opciones independientes. Mantener japonés/original disponibles y configuraciones/partidas separadas por plataforma.
- Mantener los créditos de la traducción existente: este trabajo adapta su texto a PC, no lo presenta como una traducción nueva de autoría propia.
- Extender con generación de imágenes todas las variantes decorativas KABE, respetando sus motivos y paletas, con escalado entero en la presentación.
- Extender también los fondos procedentes de PC cuando se carguen sus recursos: tanto en la ruta PC como en Saturn con el pack HD de PC. Usar la imagen PC como referencia y conservar su detalle propio; no asignar automáticamente la extensión Saturn de menor resolución. La extensión es parte del modo mejorado y la presentación original conserva el encuadre original.
- Mantener vídeo, personajes y caja de diálogo separados del fondo extendido, con sus anclajes y sombras. Escalar cada conjunto verificado en enteros y recortar únicamente el exceso decorativo necesario según la resolución.

## Decisiones de implementación

Trabajar primero con importación local y manifiestos de identidad, dimensiones, formato, correspondencia y cobertura. No sustituir un recurso por parecido de nombre. La presencia de ambos dumps es necesaria, pero por sí sola no demuestra que un asset PC sea compatible o tenga mayor resolución útil.

Propuesta técnica del implementador: packs locales con correspondencias explícitas y fallback Saturn por recurso. Mantener imágenes/ejecutables originales, recursos extraídos, guiones completos y vídeos fuera del repositorio y de la distribución. Distribuir herramientas, manifiestos y adaptaciones reproducibles; generar el pack con los datos del propietario.

Reutilizar texto inglés solo cuando la correspondencia de escena/línea y los controles del guion estén verificados. Conservar elecciones LIPS, tiempos, nombres variables y subtítulos. Registrar líneas sin equivalencia para revisión y no rellenarlas inventando una traducción automática.

## Evidencia inicial del dump PC

`Sakura Taisen PC/SAKURA.mdf` es una imagen de 1.461.485.568 bytes con ISO9660/UDF y sectores de 2048 bytes. El instalador se identifica como japonés (0x0011), InstallShield 11.0.0.28844; el Readme está fechado en 2006. El ejecutable de entrada es ADVcore.exe. El soporte contiene DrvMgt.dll y SECDRV.SYS: aún no se ha verificado que el ejecutable funcione en Windows actual. No ejecutar instaladores ni instalar controladores antiguos para extraer recursos; usar lectura de archivos/CAB.

La extracción y el análisis no equivalen a soporte PC jugable, pack HD completo ni traducción terminada. Publicar cobertura real en cada hito.

## Orden de trabajo

1. Completar y verificar la presentación Saturn en curso, conservando v0.1.0.
2. Inventariar los recursos PC y sus contenedores sin modificar el dump.
3. Construir una tabla de equivalencias PC/Saturn con ejemplos visuales y tamaños reales.
4. Probar un pack pequeño de fondos/retratos y una escena PC traducida antes de ampliar cobertura.
5. Incorporar selección de plataforma al launcher cuando cada ruta pueda validar sus entradas y fallos; no mostrar una ruta no implementada como jugable.
6. Ampliar traducción y pack por escenas, incluyendo gameplay, menús y vídeos; validar partidas y ejecución aparte en cada plataforma.
