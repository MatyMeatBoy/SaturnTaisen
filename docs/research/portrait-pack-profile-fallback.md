# Selección del paquete de retratos HD

El runtime evalúa primero el catálogo de `user/mods/hd-portraits`. Si ese candidato falla, evalúa `hd-resources/portraits` como catálogo incluido. Publica la ruta y los datos únicamente tras validar el candidato. Con un KAO original verificado, conserva la prioridad del mod personal. Con recursos preparados, el recibo debe coincidir con el origen, el número de identidades y la huella del manifiesto seleccionado. Si ambos candidatos fallan, se conserva el retrato nativo.

Antes del cambio, el runtime probaba el catálogo incluido cuando el manifiesto personal no se podía leer. Un manifiesto personal que se podía leer y luego fallaba al compararse con el recibo dejaba el juego sin retratos HD. La prueba sintética reproduce dos causas, un número antiguo de identidades y el mismo número con otro manifiesto. También cubre el perfil vacío, el manifiesto mal formado, el perfil que coincide con el recibo y el caso donde ambos catálogos son inválidos.

Con `SATRECOMP_HD_STATS=1`, el log indica si se rechazó el perfil o el catálogo incluido y da el motivo. La validación de cada PNG al precargarlo o mostrarlo conserva su comportamiento.

## Verificación

- La prueba sintética falló con el encabezado anterior. Con el cambio, ambos rechazos tardíos seleccionan las cuatro variantes del catálogo incluido.
- Se compiló un fixture directo con Clang, SDL y el lector del SDK. En una prueba con el KAO original del propietario, el mod personal de una identidad conservó prioridad sobre un catálogo de dos identidades.
- Con el catálogo de 191 como entrada del perfil y el paquete preparado de 201 como entrada incluida, el fixture de solo lectura registró `prepared count mismatch`, `records=201 source=prepared` y `portrait preload: variants=402 failed=0`. Esta prueba ejercitó los PNG reales. La selección de ruta se verificó después en la build integrada descrita abajo.
- El ZIP de v0.2.0-test.2 se publicó antes de este cambio y conserva su contenido.

## Build integrada y paridad

Patch0047 sobre el árbol registrado0001..0046. Candidato674.023 bloques SHA256 `cdedbb966ea5222d55898c50c7b89303fd53eb23c2ed19f3a391308f54f07897`. Se comparó con el runtime de test.2 en cuatro perfiles: catálogo191, catálogo201 con huella distinta, perfil vacío y copia válida del catálogo201.

Ocho ejecuciones de90fotogramas a2560×1440. Los dos perfiles obsoletos pasaron de0 a402variantes precargadas sin fallos. Los90hashes por caso y tres capturas RGB nativas por caso coincidieron; todos terminaron con cero bloques interpretados. En ambos casos corregidos, la única diferencia GUI frente a test.2 fue el retrato, dentro de `[404,644) × [1090,1378)`. Los perfiles vacío y válido conservaron el GUI idéntico. Los cuatro perfiles nuevos mostraron exactamente el mismo GUI que el perfil vacío con201.

Evidencia privada: local/work/portrait-fallback-runtime/result.json y sus logs/capturas. La validación del árbol compuesto y dos fixtures de retratos pasaron. El CMake compartido recuperó su salida habitual tras compilar el candidato aislado. El fallo diferido de un PNG después de aceptar el catálogo sigue fuera de esta corrección; no se promete fallback por archivo de imagen. El cambio está probado en desarrollo, no incluido en test.2.
