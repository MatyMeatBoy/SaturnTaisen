# Visualización de escena: Zoom opcional

Conservar la composición conjunta actual como opción Original y añadir Zoom a ajustes de Pantalla. Solo escenas narrativas reconocidas en presentación Mejorada. Imagen arriba y diálogo abajo, ambos con escalas enteras independientes. Reservar sombra derecha/inferior de cuatro píxeles nativos y separación visible. El texto/retrato HD usa la proyección del diálogo. Si no cabe o la escena tiene elementos fuera de la región conocida, conservar la composición conjunta.

Verificar primero layout puro en 720p,1080p,1440p,2160p y ultrawide; luego captura real 1440p de ambos modos y ausencia de recortes/solapamiento. Registrar parche reproducible y mantener v0.1.5 intacta.


## Implementación

Ajustes > Pantalla > Visualización de escena: Original / Zoom. Original es el valor por defecto y conserva el grupo conjunto. Zoom usa imagen 288×144 arriba, sombra de cuatro píxeles nativos y diálogo con escala independiente al fondo de la ventana. En 2560×1440: imagen ×7 (2016×1008), sombra28, separación2 y diálogo ×6 (1836×402, y1038). La sombra se dibuja antes del diálogo, que mantiene prioridad visual. Se retira exclusivamente el resto nativo de sombra de imagen identificado en la capa3, x20–307,y153–155; el marco y sombra propios de la caja se conservan.

Se exige escena reconocida, sin arte superior fuera del rectángulo seguro; las demás conservan composición conjunta. Geometría probada a720p,1080p,1440p,2160p y ultrawide. Captura real1440p compara imagen nativa exacta entre ×6/×7 y máscara de texto idéntica a ×6. La corrección de sombra cambia únicamente (482,1038)–(2156,1056) frente a la captura previa.


## Ajuste de márgenes aprobado por dirección visual

Zoom compacta ahora los dos bloques visibles y centra el conjunto verticalmente. La separación es una unidad de la escala del diálogo (mínimo2 píxeles); la sombra de imagen puede pasar detrás de la caja. Al calcular la escala se reserva margen exterior, manteniendo escalas enteras y sin recortar. En2560×1440 mantiene imagen×7 y diálogo×6: margen superior12, imageny12–1020, separación6, diálogoy1026–1428, margen inferior12. Original no cambia. Geometría verificada en720p/1080p/1440p/2160p/ultrawide y ancho2044; captura real y prueba de igualdad de píxeles de imagen y tinta del texto correctas.


## Desplazamiento inferior

El conjunto Zoom baja hasta tres unidades de escala del diálogo, limitado por el borde inferior. En1440p baja18 píxeles: margen superior30, imageny30–1038, separación6 y diálogoy1044–1446. Solo se permite ocultar una fila nativa inferior cuando la procedencia del framebuffer confirma que contiene sombra/fondo; si hay contenido o marco, el descenso se limita al borde de la pantalla. Se conservan escalas×7/×6 y Original. Geometría y comparación real de imagen/texto verificadas; captura local lowered.png.


## Separación final de diálogo

Se baja solo el diálogo media unidad de su escala (3 píxeles en1440p), sin mover la imagen. La separación pasa de6 a9; la caja empieza eny1047. El runtime identifica hasta dos filas finales que sean exclusivamente sombra/fondo y limita el desplazamiento para proteger marco y contenido. Imageny30, escalas×7/×6 y modo Original conservados. Fixture geométrico y comparación real de imagen/tinta correctos; captura dialogue-lowered.png.


Composición Zoom final confirmada: imagen y sombra suben1 píxel de salida; diálogo y sombra bajan1, dentro del límite de sombra recortable. En1440p: imageny29, diálogo1048, separación11; escalas×7/×6. Geometría y captura real de imagen/texto aprobadas.
