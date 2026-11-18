# Pendientes actuales — SaturnTaisenFirst



Actualizado: 2026-11-18. Lista de desarrollo; no describe como disponibles cambios que aún no están en un ZIP. Método y entrada para otro bot: [HANDOFF](HANDOFF.md) · [Cola compartida](PENDIENTES.md) · [Cola compartida](PENDIENTES.md).



La prioridad es Saturn. El siguiente paquete privado debe servir para probar en el otro PC el capítulo 1 panorámico y el mod HD, con los huecos declarados. **Todavía no está emitido ese ZIP ni certificado el capítulo 1 completo.** `VERSION` sigue en 0.1.2; los paquetes anteriores se conservan intactos.



## P0 — antes del siguiente ZIP de prueba



- [x] **Menús tácticos:** solapamiento corregido en Mejorado, cinco pestañas y rutas de confirmación/cámara verificadas; revisión independiente sin bloqueadores y patch actualizado. Sigue en desarrollo, no en un ZIP entregado.

- [ ] **Ruta continua del capítulo 1:** alcanzar victoria del primer combate, salida, guardado y recarga sin saltos entre estados. Hay ataques y varios turnos probados; no hay todavía victoria/capítulo completo verificados.

- [ ] **Cobertura AOT reproducible:** conservar y automatizar el descubrimiento de la familia de overlays K001–K019. La build local ampliada resuelve el bloqueo observado de Sumire en PC 060783FC; el ZIP viejo no contiene esa corrección. Comparar nativo con intérprete del mismo SDK sin llamarlo referencia independiente de Saturn.

- [ ] **Panorámico por escena/transición:** cerrar huecos restantes hasta el final del capítulo, incluidos carga, intermedio, mapas, combate, fundidos y vuelta a título. El barrido de estados es cobertura parcial, no un recorrido completo.

- [ ] **Carga:** pulir la fase/unión del mosaico generativo LOADING con el centro nativo. El layout panorámico funciona, pero el empalme sigue provisional.

- [ ] **Texto HD de diálogo:** integrar catálogo precargado y sincronización con la página/revelado real. El catálogo inglés ya está exportado localmente; todavía no es la fuente de texto del runtime. Revisar todas las líneas, desbordes, cambio de página, vibración/mezcla con tinta nativa y centrado interior.

- [ ] **Opciones LIPS HD:** implementar placa de fondo que conserve sprites bajo el panel translúcido, reconocimiento del color seleccionado y transformación de escena correcta en Zoom. Las opciones siguen usando texto nativo; cambiar solo el límite Y produciría errores de composición.

- [ ] **Retratos/animaciones HD:** cubrir los pendientes del capítulo y mantener HD en parpadeo, boca, idle y mezclas VDP2. 81/123 identidades del capítulo tienen sustitución preparada; 42 siguen pendientes. Yoneda dispone de partes, pero se ha identificado fallback durante mezclas blancas; no afirmar que falte únicamente un fotograma de ojos.

- [ ] **Vídeos PC:** extraer, identificar e integrar los equivalentes en el mod HD. No están acreditados como integrados. Preservar subtítulos/letras y sincronía; usar el área de imagen máxima en enteros.

- [ ] **Cuerpos, poses, HUD y menús HD equivalentes:** completar matches verificables. Mantener proporción uniforme y eje cabeza/columna/torso; no deformar para llenar rectángulos ni promover candidatos ambiguos.

- [ ] **Revisión y empaquetado:** registrar árbol de patches, pasar regresiones finales y emitir paquete con identidad nueva. ZIP privado único con disco 1 inglés y HD procesado, sin instalación PC completa. Extraer en carpeta nueva y probar con PATH de Windows, sin toolchain/BIOS externa. Prueba física RX 6900 XT queda para destino.



## Implementado/verificado en desarrollo, pendiente de entrega



- [x] Escala entera y máximo 16:9; Original y Zoom separados. Se mantiene la geometría Zoom aprobada.

- [x] Extensión derecha Stage01 en coordenadas del mapa: franja generada de 39×224 en (656,24), anclada al scroll. Sprites fuera del límite se rasterizan aparte; unidades y efectos desconocidos se conservan.

- [x] Fondos de mapa día/noche extendidos siguiendo sus filas nativas.

- [x] Intermedio con paleta de logotipo: identidad secundaria validada contra la imagen IC01 presentada, evitando aceptar otras pantallas por una paleta compartida.

- [x] Anclaje sin desfase en ventanas impares, incluido 705×513.

- [x] Cuatro reproducciones de transición: 3.750 hashes por fotograma coincidentes entre Original/Mejorado, cero bloques interpretados. Son rutas desde estados locales.

- [x] Ataques Sakura y Sumire probados contra el intérprete del mismo SDK; base local ampliada a 614.024 candidatos/bloques estáticos. Esto no mide cobertura ejecutada de toda la campaña.

- [x] Catálogo local de inglés: 29.725 registros por disco, 59.450 con contexto de ambos discos; offsets, IDs, bytes y hashes preservados. Datos de juego fuera de Git.

- [x] Auditoría de retratos: 191/304 identidades globales aceptadas, 113 pendientes; 382 variantes preparadas revisadas. Cobertura no equivale a todas las animaciones durante gameplay.

- [x] Empaquetadores: nombres únicos, rechazo de colisiones y comprobación real de dimensiones de la franja táctica; nunca incluir el contexto original del mapa en el release normal.



## P1 — completar Saturn y producto unificado



- [ ] Validar campaña completa, overlays de todos los capítulos y rutas alternativas, evitando cuelgues y pérdidas de progreso.

- [ ] Ambos discos obligatorios en el producto final; transición real y natural, con guardado/recarga antes y después.

- [ ] Importar y contrastar partidas de formatos de emuladores; conservar fuentes y documentar formatos realmente probados.

- [ ] Comprobar entradas LIPS y avance/salto de diálogo con animaciones, latencia y pulsaciones sostenidas frente al original.

- [ ] M30: validar perfil XInput documentado con el usuario y reconocimiento por GUID; comprobar Bluetooth/2.4G físicamente. DInput sigue sin informe. Mantener reasignación y compatibilidad general SDL3.

- [ ] RetroAchievements juego 16546: catálogo exacto, condiciones 1:1, badges locales, pestaña, popup temático, modo local offline y login/sync softcore. No anunciar soporte disponible: sigue pendiente. No adivinar condiciones ni sustituirlas por logros propios.

- [ ] Launcher y ajustes ingame: terminar navegación con mando, selector Original/Mejorado con ejemplos, pruebas de cierre tras juego listo y configuración persistente.

- [ ] Completar inventario de fondos por capítulo, empalmes mapa/novela y variantes de paleta; extender cada identidad correcta, sin un fondo global incorrecto entre escenas.

- [ ] Medir cargas reales y pausas de primer uso, caché fría/preparada, RAM/VRAM y GPU. Quitar el raster auxiliar panorámico del modo Original cuando sea seguro. No atribuir a SSD/multinúcleo mejoras sin medición.

- [ ] README, badges e informes ligados a la versión efectivamente publicada; nunca porcentajes de campaña inventados.



## P2 — después de Saturn



- [ ] Ruta jugable de PC y adaptación de la traducción inglesa Saturn.

- [ ] Extensiones de fondos PC cuando se cargue ese mod, manteniendo proporciones.

- [ ] Otros idiomas sobre el catálogo estructurado, tras completar y verificar inglés/Saturn.



## Evidencia y documentos



[Handoff](HANDOFF.md) · [Progresión](research/chapter1-battle-progress.md) · [Transiciones](research/chapter1-wide-transitions.md) · [Referencia independiente de menús](research/tactical-menu-independent-reference.md) · [PixelGen v1](research/pixelgen-v1.md) · [Catálogo](research/dialogue-catalog.md) · [Retratos](research/portrait-animation-coverage.md).



Actualizar esta lista al cerrar cada bloque. Marcar una tarea solo con la prueba correspondiente y anotar si el cambio sigue local o ya está empaquetado.
