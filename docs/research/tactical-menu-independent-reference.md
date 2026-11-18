# Referencia independiente del menú táctico

Beetle Saturn v1.32.1 arrancó el disco 1 inglés, cargó el archivo del capítulo 1 desde la RAM interna y mostró los menús de Move, Atk y Def durante el tutorial del primer combate. En las tres capturas, el submenú emergente cubre parte de la barra horizontal. El solapamiento aparece en el disco traducido bajo emulación independiente.

## Capturas verificadas

Las rutas de la tabla son relativas al directorio privado `local/work/worker-menu-oracle/cold-action-sequence`.

| Acción | Fotograma | PNG de 330 × 224 | Estado de Beetle Saturn | SHA-256 del PNG |
| --- | ---: | --- | --- | --- |
| Move | 14638 | `shot-014638.png` | `state-014638.bin` | `1f5df46eea67792a3d41d0353b44ef89bc01520f86e0464c0b88acb0c02835cc` |
| Atk, Special y Normal | 15238 | `shot-015238.png` | `state-015238.bin` | `91f1ca0f1e294ca5cb805738cf11b886bb109f8fe8324a7a66725f0e295fa561` |
| Def, Heal, Defend y Boost | 15388 | `shot-015388.png` | `end.state` | `ecf20d4b923f9b8c9ae28ef0d35e427ac23b42ae4743487d4308bb5977ae4ec7` |

Las tres capturas del arranque en frío coinciden byte por byte con las de los ensayos con estados intermedios.

## Reproducción local

```powershell
pwsh -File local/work/worker-menu-oracle/replay-menu.ps1
```

El script privado invoca `local/work/mednafen-menu-oracle.py` con los recursos preparados y guarda el resultado en un directorio nuevo. Use `-Output` para cambiar el destino. El `run.json` de la evidencia conserva los 284 eventos, 15.388 fotogramas y 30.776 ciclos de sondeo del mando. `loaded_state_sha256` es nulo en el arranque en frío. Los eventos empiezan en cero y las capturas cuentan las llamadas a `retro_run` desde uno.

| Insumo | SHA-256 |
| --- | --- |
| DLL de Beetle Saturn v1.32.1 | `8e62cd7a513c0c0f95c8a18856a68cd37d09a43df3a68b898325ed8e79e1aaa0` |
| Pista de datos del disco 1 inglés | `5b19031460c87b4773ef2cbd70ef2170bef41c1117ec8cefe27b2af1309205ec` |
| Semilla local de RAM interna, 32.768 bytes | `4aa58364c1eaa4d0cee384894861caa4cde1e426aa2e43da7aa6b4e94379bc5b` |

El control desde el mismo estado de título y durante 160 fotogramas permaneció en el título sin entrada. Una pulsación de Start en el índice 20 durante seis fotogramas abrió Program. El núcleo consultó el botón 3 del mando del puerto 0 dos veces por fotograma y recibió doce lecturas activas de Start. El recorrido espera al título y usa Down para Continue y A para confirmar Continue, File 1 y Yes.

Las muestras documentan el solapamiento en esos tres momentos del tutorial traducido. Las posiciones del menú varían con la cámara, la unidad y la fase de la acción. Esta verificación se limita a la disposición observada del submenú y su barra horizontal.

## Corrección de presentación en desarrollo

La vista Mejorada reconoce el conjunto completo de barra, cinco pestañas, marco emergente, opciones y marcador por hashes y geometría. El marco emergente contiene una prolongación ornamental de 24 píxeles que invade la barra. Se recorta esa prolongación y se desplazan ocho píxeles hacia arriba el marco restante, las opciones y su resaltado. Se conserva la etiqueta nativa de la pestaña y el funcionamiento de selección.

El renderer reconstruye un framebuffer auxiliar del host tras completar la lista VDP1. Rechaza la sustitución si hay comandos ambiguos, cambios de VRAM durante el dibujo, contenido retenido en la placa o diferencias fuera de la zona autorizada. La región solo se acepta si el framebuffer nativo terminado coincide antes con el raster auxiliar sin corregir. No escribe el framebuffer del huésped; Original conserva su presentación anterior.

En la build local se revisaron visualmente Move, Atk, Def, Info y End, Sumire con movimiento deshabilitado y una posición junto al borde del mapa. Las reproducciones compararon 2.965 hashes por fotograma entre Original y Mejorada, con cero bloques interpretados. La regresión `test_chapter1_widescreen_runtime.py` comprueba además que el centro solo cambie en el rectángulo del submenú y que la ruta de ataque/cámara mantenga sus hashes. Estos resultados no acreditan todos los menús de capítulos posteriores. El arreglo sigue en desarrollo y no está en los ZIP anteriores.
