# Primeros retratos de Sakura en HD

La revisión aprobó las identidades Saturn `0013` y `0014` con los atlas PC 18 y 19. El parecido de número sirvió para localizar los candidatos. La aprobación se basó en la expresión, el vestuario rosa, la posición de los rasgos y la comparación de las tres regiones del atlas.

| Identidad Saturn | Atlas PC | RMSE de la base | Primera tira | Segunda tira |
| --- | ---: | ---: | ---: | ---: |
| `0013` | 18 | 0,058240 | 0,047862 | 0,043342 |
| `0014` | 19 | 0,057876 | 0,047865 | 0,042901 |

Las puntuaciones comparan la cuadrícula Saturn de 40×80 con una reducción de área del atlas PC de 80×160 para el análisis. Intercambiar 18 y 19 empeora las tres regiones de cada identidad. Los atlas de vestuario gris 54 y 55 comparten las tiras correspondientes, con diferencia visible en el vestuario de la base. Desplazar cualquiera de los dos candidatos aprobados un píxel en cualquier eje empeoró el ajuste regional. Las variantes conservan el encuadre con `dx=0` y `dy=0`, densidades enteras 1× y 2×, y la máscara Saturn exacta de 3.200 y 12.800 píxeles opacos respectivamente.

## Preparación y reproducción

El registro [de revisiones](../../config/hd-portrait-reviewed.json) fija los hashes del archivo KAO, los atlas Saturn y los píxeles RGBA PC y preparados. La herramienta verifica el registro, copia las imágenes y los índices del proyecto de origen y publica un proyecto nuevo. Si se solicita la exportación, el pack se crea dentro del proyecto nuevo.

```powershell
python tools/apply_reviewed_hd_portraits.py --output-project local/work/sakura-hd-193/project.json --export
```

En un checkout separado se puede indicar `SAKURA_OWNER_ROOT` y usar una ruta absoluta de salida bajo su `local/work`. El comando usa el exportador existente y deja el proyecto original listo para otros flujos de revisión. `match_hd_assets.py --workspace local/work/sakura-hd-193` abre el proyecto con la opción `--serve`. El checkpoint privado de 193 retratos conserva los 19 fondos preparados; el paquete entregado v0.1.2 sigue documentado con 191 retratos.

## Evidencia de ejecución

La build v0.2.0-test.1 reconoció `0013` y `0014` en estados nativos del capítulo 1 a 2560×1440, con densidad 2. Se compararon 420 fotogramas por identidad con los packs de 191 y 193. Los hashes del juego y seis muestras RGB nativas coincidieron. Los cambios de GUI del fotograma 8 quedaron dentro de la caja del retrato, en el rectángulo semiabierto (404, 996) a (644, 1284). Ambos ensayos terminaron con cero bloques interpretados.

La ejecución observó la base de ambos retratos. La revisión de los PNG verificó la presencia, el ajuste y la máscara de ambas tiras. La sustitución durante el parpadeo, el movimiento de la boca y su combinación queda por observar. El checkpoint abarca 193/304 identidades globales y 83/123 del capítulo 1, con 386 variantes válidas y 111 identidades pendientes en el catálogo.

La huella del pack preparado es `24286afce17baeb43d0744b0f4b8171c8d044af02462d660ff71da2272d287b5`. Las capturas, los estados y el recibo local de validación se conservan fuera de Git.
