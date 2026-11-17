# Referencias del hilo de cheviman

Revisión solicitada por el usuario el 17 de noviembre de 2026. [Hilo original](https://www.reddit.com/r/decomps/comments/1xyt6gy/everything_im_building_arcade_decompilation_lan/). Se leyeron los repositorios públicos, sus fuentes seleccionadas y licencias; los anuncios de resultados no se consideran pruebas ejecutadas en Sakura. No se incorporó código de estos proyectos.

|Proyecto|Revisión consultada|Uso concreto en SaturnTaisenFirst|
|---|---|---|
|[htmlsaturn](https://github.com/cheviman/htmlsaturn/tree/d7e4798da9ea49f2604d0cb7acdad146aeec4287)|`d7e4798da9ea49f2604d0cb7acdad146aeec4287`|SH-2, diagnóstico de esperas y separación de render por instantáneas/filas.|
|[arcade-decomp](https://github.com/cheviman/arcade-decomp/tree/ec413d6eb04bc419f1677ee132358dc65efe0785)|`ec413d6eb04bc419f1677ee132358dc65efe0785`|Escenarios reproducibles, comparación estado/imagen/sonido y selección de regresiones.|
|[console-decomp](https://github.com/cheviman/console-decomp/tree/b9380842a84f0a09438add3083c808a662b054b7)|`b9380842a84f0a09438add3083c808a662b054b7`|Referencia de modelado de consola; su backend público es Mega Drive.|
|[arcade-lan](https://github.com/cheviman/arcade-lan/tree/ad5dfe746c13a1dc18ce3b89d9ed6803e4db0b52)|`ad5dfe746c13a1dc18ce3b89d9ed6803e4db0b52`|No necesario para la campaña individual; no se añade dependencia de red.|

## Aplicación inmediata

htmlsaturn separa VDP1 y VDP2 en trabajadores. En `vdp2-worker.js`, cada trabajador posee una instancia del chip, lee una instantánea estable y escribe líneas intercaladas que no se solapan. El campo de entrelazado se transmite desde el dueño para evitar que un trabajador desfasado dibuje el campo contrario. Su diagnóstico compara píxeles y mide el coste de una ronda vacía. Es una guía para investigar, no una mejora trasladable directamente: nuestro `RenderLine` se invoca durante el frame y observa el estado de ese momento. Antes de paralelizar hay que preservar escrituras por línea, prioridades, sombras y planos usados por el compositor mejorado.

La preparación de fondos CPU de patch21 ya separa trabajos independientes sin tocar estado invitado. La composición final usa Direct3D11. El nuevo hallazgo no demuestra que nuestro rasterizador sea GPU o que más hilos siempre aceleren una escena.

`diag/sh2-oracle.mjs` señala un caso concreto de acumulación MAC.L con saturación: interpretar los bits activos del acumulador. Se contrastará el generador nativo y el intérprete propios con el [manual oficial de Renesas, sección6.1.31](https://www.renesas.com/en/document/mas/sh-1sh-2sh-dsp-software-manual). No se deduce que explique un fallo observado en Sakura sin reproducirlo.

El comentario de carga de `cd.js` ilustra cómo una lectura todavía en progreso puede parecer un bloqueo. Su tasa comentada se contrastará con documentación de Saturn; no se adopta como valor de hardware. Para nuestras optimizaciones se medirá por separado lectura del host, entrega de sectores, posición de CPU y finalización de DMA/CD. Acelerar el SSD no autoriza eliminar esperas de sincronización del juego.

`arcade-decomp` aporta una metodología de comparación por escenarios y hashes y análisis de cambios. Sus frontends públicos consultados son V60/V70, Z80 y68000; no es un sustituto SH-2 listo para este juego. `console-decomp` documenta pendientes en la independencia de su referencia gráfica: reutilizar su metodología exige vigilar que referencia y cambio no compartan el mismo error.

## Disponibilidad y licencias

El anuncio presenta saturn-fullset, una SGL abierta sobre libyaul y recompilación Saturn hacia ejecutables nativos. El propio autor indica que ese repositorio no era público en el anuncio; no hay implementación pública revisada en esta investigación. Se conserva como referencia futura, sin cambiar el SDK actual ni depender de promesas.

Los repositorios arcade/console/lan consultados declaran BSD3-Clause. htmlsaturn declara GPLv2 o posterior y componentes de varios orígenes; cualquier incorporación futura deberá conservar las atribuciones y revisar el archivo concreto. Por ahora solo se toman ideas y casos a contrastar. cranker-llm es una herramienta de lectura para agentes, no una aceleración del ejecutable de Sakura, y no se instala como parte del juego.

## Resultado concreto de esta revisión

La pista MAC.L permitió reproducir un defecto en las dos rutas propias. Se corrigieron intérprete y generador, se regeneró la AOT y pasaron68 pruebas. [Reproducción, matriz de casos y límites](macl-48bit-regression.md). No se ha incorporado código externo ni cambiado el SDK por saturn-fullset.
