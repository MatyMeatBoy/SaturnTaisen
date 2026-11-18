# T21 — cobertura AOT reproducible de overlays

Alcance aprobado en la cola: automatizar la ampliación K001–K019 que corrigió Sumire, sin modificar discos ni la base compartida usada por Claude.

1. Añadir pruebas sintéticas para identificación exacta de familia, límites/alineación/base, variantes duplicadas, conservación de candidatos previos y rechazo de datos incompletos.
2. Implementar `tools/discover_battle_overlays.py`: leer ISOs preparados, validar overlays, deduplicar por SHA, reutilizar `static_program.discover`, fusionar candidatos conservando variantes y emitir base/manifiesto en un directorio privado nuevo. El SDK se puede indicar explícitamente para trabajar en worktree aislado.
3. Reproducir desde la base privada anterior al arreglo con los cuatro perfiles disponibles. Comparar el conjunto resultante con los 614.024 candidatos actuales, sin promocionarlo ni regenerar el ejecutable compartido. Registrar inputs, hashes y límites; candidatos no equivalen a cobertura ejecutada.
4. Revisar, abrir PR T21 e integrar con la cola actualizada. Los workers documentan puntos verificables de capítulos posteriores y revisan por separado T10.
