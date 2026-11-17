# Visualización de escena: Zoom opcional

Conservar la composición conjunta actual como opción Original y añadir Zoom a ajustes de Pantalla. Solo escenas narrativas reconocidas en presentación Mejorada. Imagen arriba y diálogo abajo, ambos con escalas enteras independientes. Reservar sombra derecha/inferior de cuatro píxeles nativos y separación visible. El texto/retrato HD usa la proyección del diálogo. Si no cabe o la escena tiene elementos fuera de la región conocida, conservar la composición conjunta.

Verificar primero layout puro en 720p,1080p,1440p,2160p y ultrawide; luego captura real 1440p de ambos modos y ausencia de recortes/solapamiento. Registrar parche reproducible y mantener v0.1.5 intacta.


## Implementación

Ajustes > Pantalla > Visualización de escena: Original / Zoom. Original es el valor por defecto y conserva el grupo conjunto. Zoom usa imagen 288×144 arriba, sombra de cuatro píxeles nativos y diálogo con escala independiente al fondo de la ventana. En 2560×1440: imagen ×7 (2016×1008), sombra28, separación2 y diálogo ×6 (1836×402, y1038). La sombra se dibuja antes del diálogo, que mantiene prioridad visual. Se retira exclusivamente el resto nativo de sombra de imagen identificado en la capa3, x20–307,y153–155; el marco y sombra propios de la caja se conservan.

Se exige escena reconocida, sin arte superior fuera del rectángulo seguro; las demás conservan composición conjunta. Geometría probada a720p,1080p,1440p,2160p y ultrawide. Captura real1440p compara imagen nativa exacta entre ×6/×7 y máscara de texto idéntica a ×6. La corrección de sombra cambia únicamente (482,1038)–(2156,1056) frente a la captura previa.
