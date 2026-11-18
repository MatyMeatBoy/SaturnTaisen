# Destello del título en Mejorado

Continúa T33 dentro del alcance aprobado: evitar el retorno visual a4:3 en el destello y mantener Original, enteros, máximo16:9 y Zoom intactos.

La reproducción actual desde el relevo3918 cambia `title → native → title`. El intervalo observado de superficie uniforme pertenece al sprite directo320×224, CMDCTRL1000, PMOD00A8, color0000, tamaño28E0, origen0,0 y textura143.360bytes repetidosFFBF. La paleta del título conserva el fingerprint91E480C617AD7F6C. No se trata de una regla general para cualquier pantalla plana.

## Implementación y prueba

- [x] Reproducir en el candidato actual, conservando capturas, hashes y cero interpretados en `local/work/t33-current-probe`.
- [x] Fixture RED por helper ausente; GREEN con la superficie exacta y rechazo de fase parcial, otro modo, paleta, tamaño, origen, último sprite, fuente o píxel diferentes.
- [x] Reconocer solo desde metadatos y píxeles del mismo framebuffer. En Mejorado, rellenar el canvas limitado a16:9 con su color nativo exacto; conservar fallback en otros casos.
- [ ] Capturar patch0051, validar SDK compuesto y compilar candidato aislado.
- [ ] Comparar contra el host previo: todos los hashes y píxeles nativos iguales; Original sin cambio; verificar entrada/salida del destello y resoluciones.
- [ ] Revisión e integración con evidencia y pendientes actualizados.

Los pétalos no uniformes siguen siendo una tarea distinta. Su superficie320×224 cambia cada fotograma y comparte el título con otros sprites: no estirar el logo ni promover un campo parcial a un color plano. Los recursos y estados permanecen en local; test.3 no se modifica.
