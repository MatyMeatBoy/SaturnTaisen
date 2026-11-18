# PixelGen v1 — extensiones decorativas

Nombre confirmado por el usuario. Flujo: generar con contexto del escenario, conservar el original fuera de la zona aprobada, normalizar a la rejilla nativa y paleta compatible, revisar la unión al tamaño real e integrar en coordenadas del mapa. El desplazamiento y escala siguen al mapa/cámara; unidades, efectos y HUD se componen encima. No añade casillas jugables ni cambia colisiones.

Primer recurso aprobado: jardín de la primera batalla, extensión derecha. Se omite la franja de agua espuria y el vacío; se continúan césped, muro y cerezos. La primera generación redibujó el centro y se descartó como sustitución completa. Se generó contexto derecho separado y se incorporó únicamente x814–895 de la captura diagnóstica de940×448. Los píxeles x0–813 permanecen originales. Fuente, variantes y manifest de hashes están en local/art/tactics/stage01; preview-16x9-v2.png es la composición aprobada. Contiene datos derivados del propietario y queda fuera de Git.

Límite de diseño:16:9 máximo, ultrawide descartado. La composición de referencia completa y sus entradas permanecen locales.

## Anclaje nativo de la primera batalla

Calibración posterior contra el mapa VDP2 completo: la captura de referencia tiene940×448 píxeles de salida, correspondientes a438×224 píxeles nativos. Su origen de mapa es277,24, con8825 coincidencias de patrones locales frente a menos de923 para las escalas alternativas ensayadas. Por tanto, no sirve tratar ambos ejes como una ampliación uniforme×2.

La franja aprobada814–895 se exporta sola como39×224 píxeles nativos y se ancla en656,24. El mapa nativo termina en la columna655; la extensión comienza fuera de ella. `tools/export_tactical_extension.py` valida hash, dimensiones y rectángulo aprobado antes de producir la franja y su manifiesto, excluyendo todo el contexto original. El export inicial41×224 con origen655,48 era provisional y ha quedado sustituido antes de entregar un ZIP.

El consumidor usa scroll por línea y el mismo entero de la escena. El renderer conserva el centro original y rasteriza aparte los sprites que cruzan el antiguo límite, con framebuffer y clip exclusivos del host. Las unidades y efectos desconocidos conservan prioridad sobre la extensión. Ocho fotogramas identificados de las partículas decorativas de agua del borde derecho se filtran únicamente en esa región y en la presentación; la lógica invitada y su framebuffer permanecen intactos. Todavía se verifica la cámara durante el combate y el recorrido completo del capítulo.

Investigación: el SDK dibuja VDP2 adicional en ruta GPU, pero oculta los lados si no detecta suelo3D. Una prueba temporal retiró esa condición y reveló mapa real más allá del rectángulo nativo, junto con límites y contenido espurio que requieren tratamiento por escenario. La condición original se restauró; esa prueba no está habilitada en producción. Referencia primaria: [renderer del SDK](https://github.com/tmcleroy/satrecomp/blob/67a5fd456609f702817c08164e77e1420dc91138/video/renderer.cpp).
