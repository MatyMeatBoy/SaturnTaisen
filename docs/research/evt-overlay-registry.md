# Registro de overlays EVT (T32)

La base AOT de 674.182 bloques cubría solo `EVT01`, `EVT02` y `EVT06`: medido contra ambos discos, los otros 25 overlays de eventos tenían apenas 60–220 posiciones comunes (código de biblioteca) frente a ~30.000 en los tres cubiertos. Eran la parte de la campaña sin traducir.

## Barrido de entradas (AOT estricto, 12.000 cuadros, ejecutable de 674.182)

| Entrada | Resultado |
| --- | --- |
| Capítulo 3 batalla 1; capítulos 4, 5, 6, 7; 8 ×2; 9 ×2; 10 batalla 1; público 7, 9 y Finale | 12.000 cuadros, sin bloque ausente |
| Capítulo 3 batalla 2 | falta bloque en `00204000` (cuadro 6.680): `EVT04` |
| Capítulo 3 batalla 3 | idem (6.679): `EVT05` |
| Capítulo 10 batalla 2 y batalla final | idem (6.685), disco 2: `EVT19` |

Atribución por coincidencia completa de bytes entre Low WRAM a `00204000` y el archivo del disco (`EVT04` 77.224 B, `EVT05` 76.672 B, `EVT19` 76.596 B). Con `EVT01/02/04/05/06/19` ya son seis observados con la misma base.

## Cambio

`tools/discover_registered_overlays.py` registra los 27 EVT distintos de ambos discos (`EVT01` es idéntico en los dos). Los tres nuevos observados llevan su evidencia; los otros 19 constan como inferidos por familia. El SDK compara el código del bloque con la memoria antes de ejecutarlo: una inferencia errónea no puede ejecutar código equivocado. Resultado local: 674.182 → 1.357.536 bloques candidatos (disco 1 +305.508, disco 2 +377.846).

Estado: estático, no ejecutado. Falta compilar, repetir el barrido y recorrer cada capítulo para observar los 19 inferidos. La base completa vive en `local/`; no se versiona.
