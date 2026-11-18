# Filas de diálogo que conservan la fuente Saturn

Las filas señaladas en las escenas de Sumire y María conservan la fuente Saturn por la misma causa. En ambas, la última celda contiene un glifo válido de nueve píxeles de ancho con un avance de ocho. La tinta sobrepasa un píxel el límite de reconocimiento. El catálogo conserva las tres filas de cada registro.

## Reproducción

Desde `local/work/sakura/theater.state`, ejecutar `tests/theater-dialogues.movie` en disco 1 inglés. Los estados guardados antes de los fotogramas 1.499, 1.504 y 1.520 contienen las tres filas en Y=160, 172 y 184. La ejecución se hizo en el binario aislado con AOT estricto y cero bloques interpretados.

En los tres estados, la última letra de la fila Y=172 es una `w` en X=296. Su tile de 16×16 coincide byte por byte con el glifo inglés ASCII 119 del atlas comprobado `0100KNJ.BIN`. FNV-1a del tile `66BBC3BE84C1B486`. La fila tiene una sola entrada por X y todos sus demás glifos se reconocen. La `w` aporta exactamente dos píxeles fuera del límite de reconocimiento, en `(304,176)` y `(304,177)`. `NarrativeInkFits` exige X<304 y marca como inválida la fila entera. Las otras dos filas superan esta comprobación.

## Otro caso con el mismo límite

La fila final de María corresponde al registro `1:/SAKURA1/0100TBL.BIN:50064:498`. Desde `local/work/sakura/chapter1-continuous-47999.state`, ejecutar `tests/maria-click.movie`. Los estados guardados antes de 719, 839 y 959 conservan la misma elipsis final. El tile colocado en X=296, Y=184 coincide inequívocamente con CP1252 `0x85` (U+2026), FNV-1a `283D49C0BB2786CE`. Un solo píxel de tinta en `(304,194)` queda fuera de `NarrativeInkFits`. No hay posiciones duplicadas ni glifos desconocidos.

| Escena | Fila | Tile nativo | Tinta fuera de X<304 |
| --- | --- | --- | --- |
| Sumire, comedor | Y=172 | `w`, X=296 | `(304,176)` y `(304,177)` |
| María | Y=184 | U+2026, X=296 | `(304,194)` |

## Píxeles del borde y criterio de corrección

Las capturas sincronizadas muestran los tres píxeles fuera del área en RGB `232,232,232`, con la misma contribución de VDP1 en la salida final. En X=304, el plano de diálogo VDP2 ya está en el tono oscuro del borde `120,120,120`. En X=303 sigue siendo el relleno claro. La moldura de oro vecina en esa misma columna también pertenece a VDP1.

En Sumire también coinciden dos trazos de filas contiguas. El descendente de `p` en X=112, Y=160 y el ascendente de `h` en X=112, Y=172 comparten `(113,173)` y `(114,173)`. La restauración de esos píxeles debe incluir las dos filas y recuperar lo que había antes del primer glifo.

Para convertir todas las celdas a HD y mantener el recorte X<304, la placa debe restaurar con precisión el píxel VDP1 que había debajo de cada glifo. El buffer `underSprites` excluye toda la capa VDP1 y por sí solo no aporta esa restauración. La placa tendría que preservar la moldura anterior al glifo y las capas VDP2, y verificar orden de dibujo, coincidencia de tinta y alcance del desborde. Glifos desconocidos, posiciones duplicadas, oclusión o placa ausente deben conservar el fallback seguro. Se requiere validar la identidad del glifo y sus píxeles fuera del área antes de retirarlos.

Para probar la corrección, capturar ambas frases antes y después de que aparezca la última celda. La línea base de cada fila debe permanecer estable durante el revelado. Conservar el recorte de salida y comprobar el borde contra una placa sin tinta. Comparar asimismo los hashes con Original.

`local/work/hd-text-row-rejections` contiene los estados y el script de auditoría de comandos VDP1. En `frame1` y `maria-frame1` están las capturas sincronizadas de planos. El diagnóstico cubre ambas filas observadas.

## Verificación de la placa de glifos

El candidato probado registra el valor VDP1 anterior al primer glifo y los identificadores de hasta dos glifos que escriben el mismo píxel. Reutiliza el compositor nativo para recuperar la imagen anterior a la tinta. Si se superponen dos filas, valida todas sus celdas antes de restaurar la zona compartida. Las escrituras posteriores ajenas al glifo invalidan la captura, incluso cuando repiten el mismo valor. El recorte HD sigue en X<304.

En ambas escenas se tomaron capturas de 1600×900 con los mismos recursos y tres combinaciones: Original, Mejorada con texto HD y Mejorada con texto Saturn. La traza confirma placa válida y texto HD en Y=160 y Y=172 de Sumire y en Y=184 de María. En las tres posiciones que habían invadido la moldura, el gris nativo de la tinta se restaura al oro de la moldura: RGB `152,112,40` y `88,56,0` en Sumire y `152,112,40` en María. Las capturas de Original coinciden píxel a píxel con test.1. Coinciden los 12 hashes por escena en todos los perfiles probados, con cero bloques interpretados.

La prueba sintética `tests/test_glyph_plate.cpp` cubre una moldura bajo el glifo, dos escritores, una escritura ajena con el mismo valor, invalidación por escritura guest y la aplicación del ajuste de color nativo. La verificación visual se limita a estas dos muestras ya escritas. La sustitución de las opciones LIPS sigue siendo una aplicación posterior.
