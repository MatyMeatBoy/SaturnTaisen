# Índice de investigación

Una línea por documento. Los JSON son la evidencia legible por máquina de su documento; los que no tienen documento propio aparecen al final. `tests/test_research_index.py` comprueba que todo archivo de esta carpeta figure aquí.

## Recompilación y CPU

- [2026-11-17-investigacion.md](2026-11-17-investigacion.md) — investigación inicial, proyectos candidatos y referencias ([projects.json](projects.json), [upstream-evidence.json](upstream-evidence.json)).
- [2026-11-17-casos-recomp.md](2026-11-17-casos-recomp.md) — casos de recompilaciones Saturn y decisiones para Sakura.
- [2026-11-17-cobertura-estatica.md](2026-11-17-cobertura-estatica.md) — ampliación de cobertura estática ([static-program-analysis.json](static-program-analysis.json), [static-program-eager-analysis.json](static-program-eager-analysis.json)).
- [2026-11-17-validacion-nativa.md](2026-11-17-validacion-nativa.md) — arranque nativo y llegada al teatro ([runtime-validation.json](runtime-validation.json)).
- [macl-48bit-regression.md](macl-48bit-regression.md) — MAC.L con acumulación saturada de 48 bits ([macl-48bit-regression.json](macl-48bit-regression.json)).
- [cheviman-saturn-toolchain.md](cheviman-saturn-toolchain.md) — referencias del hilo de cheviman.

## Motor, discos y progreso

- [sakura-engine-notes.md](sakura-engine-notes.md) — conocimiento específico del motor de Sakura.
- [sakura-sdk-and-loading.md](sakura-sdk-and-loading.md) — SDK de Sakura y cargas ([sakura-sdk-inventory.json](sakura-sdk-inventory.json)).
- [chapter1-battle-progress.md](chapter1-battle-progress.md) — validación de combate del capítulo 1 ([chapter1-battle-progress.json](chapter1-battle-progress.json)).
- [save-import.md](save-import.md) — importación de partidas ([public-save-fixtures.json](public-save-fixtures.json)).

## Presentación y HD

- [saturn-background-loading.md](saturn-background-loading.md) — cargas de fondos y mod HD ([saturn-background-loading.json](saturn-background-loading.json), [saturn-background-compression.json](saturn-background-compression.json)).
- [saturn-background-workers.md](saturn-background-workers.md) — preparación multinúcleo de fondos ([saturn-background-workers.json](saturn-background-workers.json)).
- [saturn-hd-characters.md](saturn-hd-characters.md) — personajes PC para el mod HD ([pc-character-inventory.json](pc-character-inventory.json)).
- [pc-spred-resources.md](pc-spred-resources.md) — primera decodificación verificada de recursos PC ([pc-background-inventory.json](pc-background-inventory.json)).
- [hd-font-proportions.md](hd-font-proportions.md) — proporciones de la fuente HD.
- [pixelgen-v1.md](pixelgen-v1.md) — PixelGen v1, extensiones decorativas.
- [v011-floral-background.md](v011-floral-background.md) — fondo floral panorámico de v0.1.1 ([kabe-backgrounds.json](kabe-backgrounds.json)).

## Mandos

- [m30-controller-profiles.md](m30-controller-profiles.md) — mandos M30 y SDL.
- [controller-mapper.md](controller-mapper.md) — mapeador por entradas físicas.

## Evidencia sin documento propio

- [discs-inventory.json](discs-inventory.json) — inventario de discos.
- [prepared-disc1.json](prepared-disc1.json), [prepared-disc2.json](prepared-disc2.json), [prepared-japanese-discs.json](prepared-japanese-discs.json) — preparación de imágenes.
- [translation-code-impact.json](translation-code-impact.json) — código afectado por la traducción.
- [logo-module-analysis.json](logo-module-analysis.json), [ending-module-analysis.json](ending-module-analysis.json) — análisis de módulos LOGO y final.
- [mods-status.json](mods-status.json) — estado de mods evaluados.

## Integración del 2026-11-18

- [chapter-sweep.md](chapter-sweep.md) — nueve rutas posteriores, residencias verificadas y ampliación EVT06 del episodio4 ([resultado](episode4-aot-fix.json)).
- [portrait-white-blends.md](portrait-white-blends.md) — metadatos exactos de mezcla blanca y preservación del fundido en retratos HD.
- [later-chapter-validation.md](later-chapter-validation.md) — partidas verificadas, bloqueo de EVT02 y seguimiento de la carga de episodios posteriores ([arreglo AOT](episode2-aot-fix.json)).
- [battle-overlay-reproduction.md](battle-overlay-reproduction.md) — reconstrucción verificable de la ampliación de combate ([manifiesto](battle-overlay-reproduction.json)).
- [spanish-translation-workflow.md](spanish-translation-workflow.md) — guiones ingleses con IDs, controles y alias entre discos para el parche español de Claude.
- [scene-tagging.md](scene-tagging.md) — seis etiquetas sencillas, inventario de ambos discos y vínculos con los guiones, distinguiendo candidatos de observaciones.
- [battle-overlay-family.json](battle-overlay-family.json) — evidencia o informe del bloque de presentación y cobertura del capítulo 1.
- [chapter1-continuous-battle.json](chapter1-continuous-battle.json) — evidencia o informe del bloque de presentación y cobertura del capítulo 1.
- [chapter1-wide-transitions.md](chapter1-wide-transitions.md) — evidencia o informe del bloque de presentación y cobertura del capítulo 1.
- [dialogue-catalog.md](dialogue-catalog.md) — evidencia o informe del bloque de presentación y cobertura del capítulo 1.
- [portrait-animation-coverage.md](portrait-animation-coverage.md) — evidencia o informe del bloque de presentación y cobertura del capítulo 1.
- [tactical-menu-independent-reference.md](tactical-menu-independent-reference.md) — evidencia o informe del bloque de presentación y cobertura del capítulo 1.

- [dialogue-panel-compositing.md](dialogue-panel-compositing.md): Mezcla Saturn exacta y continuidad del fondo dentro del panel.

- [hd-text-row-rejections.md](hd-text-row-rejections.md): Reproducciones de Sumire y María: glifos válidos fuera del límite.

- [intro-petals-transition.md](intro-petals-transition.md): Pétalos horneados, fallback durante destellos y primer vídeo.

- [battle-story-inset-shadow.md](battle-story-inset-shadow.md): Prueba por capas de ausencia de sombra en la viñeta táctica.

- [dialogue-voice-advance.md](dialogue-voice-advance.md): Pulsaciones A/B/C, voz real y comparación AOT/intérprete.

- [wide-map-crossfades.md](wide-map-crossfades.md): Fundido mapa/floral con continuidad a16:9, entrada directa aZoom y paridad nativa.

## Traducción

- [traduccion-espanol.md](traduccion-espanol.md) — parche al español: método japonés → inglés → español, formatos de diálogo, combate y menús, ISO con ranuras fijas.

- [first-sakura-hd-portraits.md](first-sakura-hd-portraits.md): Matches revisados de Sakura0013/0014, reproducción y límites de la prueba en juego.
- [Segundo lote de retratos HD del capítulo 1](chapter1-sumire-hd-portraits.md)
- [Tercer lote de retratos HD del capítulo 1](chapter1-third-hd-portraits.md)
- [Selección del paquete de retratos HD](portrait-pack-profile-fallback.md)

- [chapter1-choice-hd.md](chapter1-choice-hd.md): Texto HD LIPS de dos/tres opciones, propiedad de glifos y diez perfiles reales.

- [first-film-transition-fix.md](first-film-transition-fix.md): Fase verificada del primer video, fondo limpio y prueba continua de6201fotogramas.

- [first-film-script-phase.md](first-film-script-phase.md): Investigación del cursor de0100.BIN y límites de las fases sin imagen.

- [RetroAchievements 16546 en Saturn](retroachievements-16546.md)
- [dialogue-preload-runtime.md](dialogue-preload-runtime.md): Catálogo inmutable, lectura acotada y narrativa precargada con celdas de revelado nativas; cobertura global pendiente.
- [chapter1-victory-followup.md](chapter1-victory-followup.md): Derrota de Satan, rutinas relocalizadas, bloqueo postcombate y validación de guardado/Resume.
- [Identificación de grupos LIPS por el cursor](lips-script-cursor.md) — dos paneles verificados con el script, la tabla y los tiles nativos.
- [Progresión táctica del capítulo 2](chapter2-tactical-progression.md) — Continue, órdenes, fase enemiga y ataque aliado con comparación AOT/intérprete.
- [Registro de overlays EVT](evt-overlay-registry.md)
