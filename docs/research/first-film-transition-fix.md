# Primer video: fondo limpio antes y despues

El patch0046 elimina en Mejorado el pie vacio y la sombra de imagen de las fases verificadas de New Game. El video activo conserva el recorte288x144 y su escala entera maxima del patch0038. Original no cambia.

## Identidad y fase

El programa0100.BIN tiene15404bytes y FNV64 `5DA24532C9356735`. Se lee una vez mediante el nombre simple usado por DiscFiles; se rechazan otros archivos. Cada testigo de fase compara el modulo completo contra Low WRAM en00204000 y lee el cursor BE32 de High WRAM060685B4. La lista exacta observada es00204006,00204462,00204ED8,00204EDE,00204EE4 y00204EE6. La secuencia y las muestras se describen en [la investigación del cursor](first-film-script-phase.md); estos valores no son una identificacion general del SDK ni de todos sus opcodes.

El testigo se captura en el callback de framebuffer, bajo su mismo mutex y antes de restaurar RAM tras run-ahead. Se copia junto a los pixeles presentados. Es metadato del host y no entra en el estado guest ni modifica el guion.

Ocultar requiere ademas un frame320x224 sin capas de imagen1/2/4, fondo floral visible, y solo capas0/3 dentro de las zonas conocidas. Las ordenes dibujables VDP1 deben estar ausentes o ser exclusivamente el pie/badge conocidos por modo, geometria y hash de textura. Se acepta el banco de badge C400 o4400 durante su fundido y dos copias identicas del pie al salir. Cualquier figura, glifo, textura u orden dibujable desconocida conserva el render normal. La tarjeta del episodio utiliza capa4 y se rechaza expresamente aunque persista el cursor00204EE6.

## Verificacion continua

Reproduccion desde title-final.state, sin cargar estados intermedios divergentes, hasta6201fotogramas. El candidato final SHA256 es `453e1a6ae4679f654d27534c718edd7e5b817f97f8048a14178422dcbd1a1af1` (614024bloques).

- Todos los6201hashes coinciden con Original y con la ruta archivada; seis capturas RGB nativas coinciden y hay cero bloques interpretados.
- Fondo solo: pasos707..879 y5938..6067, sin retorno intermedio al grupo de novela. Se revisaron las capturas806/807/820/830/831 y5938/5939/5960/5988/5989.
- Video ampliado:880..5937. La imagen usa el area288x144 y no incluye la caja de texto vacia.
- Paso6068: la tarjeta del episodio conserva su contenido nativo. Esa transicion y el efecto completo de petalos del titulo siguen pendientes por separado.
- Los fixtures verifican cursores admitidos/rechazados, modulo alterado, buffers truncados, presencia de imagen/actor fuera del pie y comandos desconocidos. Se observo el fallo antes de implementar la correccion.

Las trazas opcionales SATRECOMP_MOVIE_PHASE_TRACE numeran los cambios de cursor y layout para acotar defectos de un solo fotograma. Estados, imagenes y recibos se conservan en local/work/first-film-phase-approved y las auditorias anteriores del propietario. El patch esta probado en esta ruta y aun no esta incluido en un nuevo ZIP. No acredita toda la introduccion ni la campana.
