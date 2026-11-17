# PixelGen v1 — extensiones decorativas

Nombre confirmado por el usuario. Flujo: generar con contexto del escenario, conservar el original fuera de la zona aprobada, normalizar a la rejilla nativa y paleta compatible, revisar la unión al tamaño real e integrar en coordenadas del mapa. El desplazamiento y escala siguen al mapa/cámara; unidades, efectos y HUD se componen encima. No añade casillas jugables ni cambia colisiones.

Primer recurso aprobado: jardín de la primera batalla, extensión derecha. Se omite la franja de agua espuria y el vacío; se continúan césped, muro y cerezos. La primera generación redibujó el centro y se descartó como sustitución completa. Se generó contexto derecho separado y se incorporó únicamente x814–895 de la captura diagnóstica de896×448. Los píxeles x0–813 permanecen originales. Fuente, variantes y manifest de hashes están en local/art/tactics/stage01; preview-16x9-v2.png es la composición aprobada. Contiene datos derivados del propietario y queda fuera de Git.

Límite de diseño:16:9 máximo, ultrawide descartado. Las coordenadas de esta captura no son todavía anclajes del mapa. Falta identificar el recurso nativo y scroll/cámara de la escena antes de integrar la extensión móvil. No presentar una superposición fija como extensión terminada.

Investigación: el SDK dibuja VDP2 adicional en ruta GPU, pero oculta los lados si no detecta suelo3D. Una prueba temporal retiró esa condición y reveló mapa real más allá del rectángulo nativo, junto con límites y contenido espurio que requieren tratamiento por escenario. La condición original se restauró; esa prueba no está habilitada en producción. Referencia primaria: [renderer del SDK](https://github.com/tmcleroy/satrecomp/blob/67a5fd456609f702817c08164e77e1420dc91138/video/renderer.cpp).
