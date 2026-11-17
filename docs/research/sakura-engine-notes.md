# Sakura: conocimiento específico del motor

Estado de investigación, 17/11/2026. Fuente prioritaria: [herramientas del equipo traductor](https://github.com/NoahSteam/RomHackingTools/blob/master/SakuraTaisen/SakuraTaisen.cpp), versión fijada en `upstream-evidence.json`. No se copiaron recursos del juego.

## Material comprobado aquí

- Ambos discos son GS-9037 V1.005 (CD-1/2 y CD-2/2), región JT, con arranque en 0x06004000. Hay 1785 archivos en cada original y en cada traducción.
- El parche cambia 201 archivos del disco 1 y 199 del disco 2; `translation-code-impact.json` guarda tamaños y hashes de candidatos relevantes. SAKURA y LOGO.SH2 sí cambian: no basta con recompilar el japonés y sustituir imágenes.
- SAKURA4 y SAKURA5 son contenedores grandes sin extensión, no ejecutables monolíticos deducibles por su nombre. No se han clasificado todavía todas sus entradas.
- Se alcanzó el título inglés, y la entrada a la narración inicial, mediante scripts de mando. El vídeo y la presentación no prueban aún batalla, elecciones, minijuegos, guardado ni campaña completa.

## Aportaciones de las herramientas de traducción

`SakuraTaisen.cpp` contiene extracción/reinserción de texto, fuentes KNJ, paletas, gráficos comprimidos, caras FCE/FACE, menús WKL, eventos EVT y subtítulos. `FixupSakura` modifica instrucciones SH-2 de lectura y avance de caracteres, con direcciones anotadas para el arranque cargado en 0x06004000. Es información útil para nombrar funciones, comprobar el motor de texto traducido y localizar cambios, no una decompilación del motor completo.

Los nombres y offsets de otros parches o versiones no se aplican sin comprobar los bytes y el disco exactos. Los contenedores deben conservar sus tablas y llamadas; un mod de gráficos no se fuerza cambiando el tamaño de una celda de Saturn.

## Referencia independiente

Se descargó Beetle Saturn del buildbot oficial de Libretro para comparación, con hash SHA-256 `8e62cd7a513c0c0f95c8a18856a68cd37d09a43df3a68b898325ed8e79e1aaa0`. Usa las BIOS propias aportadas y los discos traducidos locales. Identifica la pista de audio del disco 1 en LBA 271118, consistente con el POSTGAP y PREGAP del CUE del parche.

El arranque por BIOS tiene un desplazamiento respecto al arranque HLE del runtime; comparar escenas por estado y contenido, no restando un número supuesto de frames. Beetle informa 59.8265 Hz para este modo; la velocidad final debe respetar el reloj guest y no depender del monitor o del coste de dibujar.

## Trabajo siguiente

1. Resolver todas las diferencias de estado entre AOT e interpretación de referencia del toolkit; mantener activo el rechazo de fallback.
2. Añadir color calculation de VDP2 y las funciones que el juego pida, contrastando con escenas/capturas de Beetle.
3. Descubrir código de ambos discos y contenedores de minijuegos/batalla; localizar la máquina de estados y el cambio de disco.
4. Establecer pruebas de elecciones con tiempo, diálogo/voz, batalla, minijuegos y guardado. Verificar esas mismas memorias al integrar RA.
