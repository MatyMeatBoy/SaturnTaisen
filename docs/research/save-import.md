# Importación de partidas de Saturn

Requisito autorizado: importar partidas de los distintos emuladores desde el launcher, conservar originales y probar puntos avanzados obtenidos públicamente. La interfaz del launcher permite elegir o pegar el archivo, detectar el formato, crear una copia, activarla y volver a la partida habitual. Se probó con pulsaciones reales de su modo de pruebas y después con una carga del episodio 8 desde el launcher; los originales permanecen intactos.

Primera herramienta local:

```powershell
python tools/import_saves.py partida.BUP
python tools/import_saves.py partida.BUP --output local/importada.bin
```

Sin `--output` inspecciona; con él crea una memoria interna nueva de 32 KiB con los archivos `SAKURA___*`. Rechaza un destino existente. No mezcla automáticamente con la partida activa, no copia otros juegos y no cambia datos de progreso ni de RetroAchievements.

## Formatos implementados

- BUP (`Vmem`), con tamaño declarado comprobado.
- SAROO individual (`SSAVERAW`), con tamaño y CRC comprobados cuando existe CRC.
- Memoria interna compacta de 32 KiB, bloques de 64 bytes.
- Memoria externa compacta de 512 KiB, bloques de 512 bytes.
- Volcados SH-2 de 64 KiB o 1 MiB: byte útil en posición impar.

El lector detecta el contenido, valida las cadenas de bloques y rechaza ciclos, solapamientos, tamaños imposibles y falta de espacio. Los estados de máquina y los formatos no reconocidos se rechazan. Todavía faltan, entre otros, XML/B64/SGM, contenedores SAROO completos y geometrías adicionales. No se afirma compatibilidad con todos los emuladores por aceptar una extensión.

Se leyeron muestras públicas Mednafen, SSF y Yabause del repositorio del conversor de Knight0fDragon. Varias se decodifican; otras revelan formatos aún pendientes o cadenas que requieren investigación. El detalle se conserva en `local/logs/save-format-samples.json`. No confundir decodificar una muestra con verificar que la partida funciona dentro de Sakura.

## Partidas públicas de Sakura

[Colección de Bucanero](https://github.com/bucanero/saturn-save-tools/tree/main/docs/sakura-wars), con créditos a privateye y Pimpeaux. Son dos partidas completadas con finales de Sakura y Sumire; se preservan localmente. Las parejas BUP/SAROO contienen los mismos metadatos y 5708 bytes de datos. La primera, importada en una copia para la referencia con el disco inglés 2, muestra episodios 8, 9 y Finale en sus tres casillas. La carga y ejecución de esas escenas en AOT todavía se están verificando.

Procedencia y hashes: `public-save-fixtures.json`. No se distribuyen las partidas en este repositorio.

## Referencias de formatos

- [Saturn Save Tools](https://github.com/bucanero/saturn-save-tools), `include/bup_header.h`, `include/sgm-types.h` y `src/ss-converter.c`.
- [SS Backup RAM Parser](https://github.com/hitomi2500/ss-save-parser), modo SH-2 con bytes intercalados y tablas de asignación.
- [Saturn Save Converter](https://github.com/knight0fdragon/SaturnSaveConverter), implementaciones y muestras por emulador.

El conversor del proyecto es código propio basado en las estructuras documentadas; no ejecuta los conversores descargados.
