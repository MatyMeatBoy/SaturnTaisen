# Fondo floral widescreen — v0.1.1

## Estado y autorización

El usuario aprobó **preliminarmente** la segunda propuesta generada el 17/11/2026 y después indicó que **prefiere la primera variante por tener más flores**. La primera pasa a ser la referencia artística elegida: mantener su mayor densidad floral al corregir el acabado de píxel. No es todavía el asset final ni está integrado en el runtime. Mantener v0.1.0 intacta.

Archivos locales, conservados fuera de Git como los recursos derivados del juego:

- Original extraído: `local/work/v011/layers/movie-layer5.png` (320×224).
- Primera propuesta, ahora preferida por el usuario: `local/art/v011/floral-day/proposal-01.png`.
- Segunda propuesta, aprobada preliminarmente antes de esa preferencia: `local/art/v011/floral-day/proposal-02-preliminary-approved.png`.

Generación mediante herramienta integrada image_gen, sin API externa configurada por el proyecto. Instrucción: extender el bitmap original a 16:9, preservando composición central, flores rosas de cinco pétalos, gradiente diagonal verde/crema/rosa y trama de píxel; sin texto, marcos, personajes ni interfaz. La segunda pasada pidió explícitamente conservar las posiciones originales y evitar bordes vectoriales y textura de papel.

La salida sigue reinterpretando partes del centro y su textura: la aprobación es de dirección artística, no una comprobación de preservación exacta de píxeles. No anunciar esta propuesta como pixel-perfect. La meta de producción es un lienzo lógico 416×234 (16:9 exacto), original 320×224 centrado en (48,5), con continuidad comprobada en sus cuatro uniones. No convertir a esa resolución mediante interpolación suave.

## Evidencia de separación

La captura de planos del renderer muestra el fondo diurno en NBG3, vídeo en RBG0 y marco/emblema en VDP1. La escena de Iris usa otra paleta floral, nocturna, y combina personaje, texto y marco en VDP1. Separación de planos no implica separación automática de todos los elementos de interfaz.

El fondo diurno no debe sustituir la variante nocturna ni aparecer en escenas cuya composición no se haya identificado. Las herramientas de la traducción contienen imágenes de subtítulos: no recortar vídeo suponiendo que siempre carece de texto.

## Escalado acordado

El fondo usa píxeles cuadrados, nearest-neighbor y factor entero positivo. Para cubrir una salida W×H con un fondo B×C: `k = max(1, ceil(W/B), ceil(H/C))`; centrar Bk×Ck y recortar únicamente el excedente decorativo. Así se cubren 16:9, 4:3, ultrapanorámico y ventanas arbitrarias sin escala fraccionaria ni deformación. El recorte no se aplica al vídeo, texto o personajes.

El contenido jugable usa un factor entero independiente, el mayor que permita mostrar su conjunto completo. El fondo puede requerir un entero superior para cubrir la ventana; no reducir el contenido por obligarlo a compartir factor con el fondo. Preservar la opción Original y todas las escenas aún no reconocidas.

Pendiente: acabado del asset a resolución lógica, verificación de uniones y paleta, integración del compositor y pruebas de salida real. Esta nota no registra esas tareas como terminadas.
