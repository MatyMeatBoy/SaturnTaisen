# Selección del paquete de retratos HD

El runtime evalúa primero el catálogo de `user/mods/hd-portraits`. Si ese candidato falla, evalúa `hd-resources/portraits` como catálogo incluido. Publica la ruta y los datos únicamente tras validar el candidato. Con un KAO original verificado, conserva la prioridad del mod personal. Con recursos preparados, el recibo debe coincidir con el origen, el número de identidades y la huella del manifiesto seleccionado. Si ambos candidatos fallan, se conserva el retrato nativo.

Antes del cambio, el runtime probaba el catálogo incluido cuando el manifiesto personal no se podía leer. Un manifiesto personal que se podía leer y luego fallaba al compararse con el recibo dejaba el juego sin retratos HD. La prueba sintética reproduce dos causas, un número antiguo de identidades y el mismo número con otro manifiesto. También cubre el perfil vacío, el manifiesto mal formado, el perfil que coincide con el recibo y el caso donde ambos catálogos son inválidos.

Con `SATRECOMP_HD_STATS=1`, el log indica si se rechazó el perfil o el catálogo incluido y da el motivo. La validación de cada PNG al precargarlo o mostrarlo conserva su comportamiento.

## Verificación

- La prueba sintética falló con el encabezado anterior. Con el cambio, ambos rechazos tardíos seleccionan las cuatro variantes del catálogo incluido.
- Se compiló un fixture directo con Clang, SDL y el lector del SDK. En una prueba con el KAO original del propietario, el mod personal de una identidad conservó prioridad sobre un catálogo de dos identidades.
- Con el catálogo de 191 como entrada del perfil y el paquete preparado de 201 como entrada incluida, el fixture de solo lectura registró `prepared count mismatch`, `records=201 source=prepared` y `portrait preload: variants=402 failed=0`. Esta prueba ejercitó los PNG reales. Queda pendiente verificar la detección de la ruta desde una build integrada.
- El ZIP de v0.2.0-test.2 se publicó antes de este cambio y conserva su contenido.
