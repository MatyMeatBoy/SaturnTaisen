# Segundo lote de retratos HD del capítulo 1

Se revisaron tres expresiones de Sumire. Las diferencias de boca y ojos distinguen las dos poses cercanas `0040` y `0041`. En `0045` se ve la boca abierta. Comparar el vestuario de la base permitió descartar las alternativas PC 90, 91 y 95, que comparten las tiras y visten otra variante.

| ID Saturn | Candidato PC | RMSE base | Primera tira | Segunda tira | Observado en juego |
| --- | ---: | ---: | ---: | ---: | --- |
| `0040` | 63 | 0,058700 | 0,057460 | 0,056257 | Primera tira en Y=16 |
| `0041` | 64 | 0,058665 | 0,057952 | 0,056752 | Primera tira en Y=16 |
| `0045` | 68 | 0,059924 | 0,059211 | 0,056777 | Base |

El análisis comparó la cuadrícula Saturn de 40×80 con una reducción de área del atlas PC de 80×160. En las tres regiones de cada retrato, el error fue menor con `dx=0` y `dy=0` que al desplazar un píxel nativo. La máscara Saturn se conservó exactamente con 3.200 píxeles opacos a 1× y 12.800 a 2×, sin huecos. La segunda tira y las dos tiras juntas siguen pendientes de observación en juego. `0095` conserva dos candidatos cercanos sin evidencia concluyente para elegir. `0169` conserva diferencias de composición y tiras que requieren revisión adicional.

## Reproducción

El [registro de revisiones](../../config/hd-portrait-reviewed.json) fija el archivo KAO, los tres atlas Saturn, los píxeles PC y cada variante preparada mediante hashes. El mismo comando aplica estas tres revisiones y las dos de Sakura al proyecto original del propietario y exporta a una carpeta nueva.

```powershell
python tools/apply_reviewed_hd_portraits.py --output-project local/work/chapter1-hd-196/project.json --export
```

La auditoría del checkpoint contabilizó 196/304 identidades globales y 86/123 en el capítulo 1, con 392 variantes y cero errores. Quedan 108 pendientes en el catálogo y 37 en el capítulo 1. El paquete privado preparado conserva los 19 fondos byte por byte y tiene un recibo SHA-256 `7db33b3dbf185870f7077a695f27ba420927641e112573dbab963746184dfd02`. Los paquetes entregados se conservan.

## Prueba de ejecución

La build v0.2.0-test.1 reprodujo cada estado durante 180 fotogramas a 2560×1440 con los paquetes de 193 y 196. La comparación obtuvo 180 hashes guest iguales y tres capturas RGB nativas idénticas por identidad. La diferencia GUI del fotograma 8 se limitó al rectángulo de retrato `[404,644) × [996,1284)`. El runtime registró densidad 2 y cero bloques interpretados en las seis ejecuciones. Los estados, las capturas y los informes con hashes por ejecución quedan en el espacio privado del propietario.
