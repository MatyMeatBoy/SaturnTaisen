# Personajes PC para el mod HD de Saturn

El usuario confirmó que se deben adaptar también los sprites de chicas, otros personajes, retratos y expresiones. Continúa la prioridad Saturn; esto no integra ejecución ni traducción de la plataforma PC. La mejora de texto sigue siendo una opción separada.

## Inventario verificado

`tools/audit_hd_characters.py` compara los recursos propios extraídos con ambas ISO Saturn preparadas. Encontró 147 archivos de personajes NC de PC, con 3.596 imágenes no vacías. Los 147 nombres tienen candidatos nativos. El inventario registra hashes de archivo, dimensiones, formatos y ubicaciones por disco; no incluye píxeles ni datos originales. La coincidencia de nombre no demuestra coincidencia de índices, expresiones o geometría.

La inspección nativa mediante `tests/inspect_pc_sprites.cpp` usa el mismo DecodePcSprites del runtime: los 147 archivos y las 3.596 imágenes se decodificaron sin errores, con 42.423.793 píxeles. Todos los registros de imagen NC observados usan 0x15 (RGB555 comprimido). También se inventariaron KAO.SPR (394 imágenes) y KAO_P.SPR (25); su decodificación y su correspondencia narrativa se verifican por separado.

Hay 11.158.719 píxeles verdes puros en la salida NC, y el decodificador actual no asigna transparencia a estas imágenes directas. Esto expone trabajo pendiente de máscaras/composición: no basta con dibujarlas encima. No se declara todo verde como transparente, porque una regla general podría eliminar colores válidos.

## Integración siguiente

1. Identificar las imágenes nativas y las tablas de composición de una escena reproducible. No inferir el formato NC nativo a partir de una cabecera parecida a un tamaño. Un intento exploratorio de LZSS SPRED aplicado directamente al NC Saturn no consume el recurso completo y no se considera un decoder válido.
2. Verificar cuerpos, poses, ojos, bocas y retratos con sus anclajes, máscaras, flips y prioridades. Mantener las expresiones y el ritmo de animación elegidos por el juego.
3. Asociar cada sustitución a una identidad de recurso/imagen, no solo a una dirección VRAM reutilizable. Rechazar fuentes desconocidas y conservar el original si no se obtiene una sustitución completa y usable.
4. Reutilizar la transformación entera del compositor mejorado para que los sprites HD, el vídeo y la caja de texto permanezcan alineados; no introducir escalado fraccional ni cambios de colisión o lógica.
5. Preparar y cargar solo los personajes necesarios, con caché acotada y subida de texturas en el hilo de ventana. Invalidar/recrear recursos al cargar estados o cambiar de dispositivo.
6. Ampliar al resto de personajes y elementos compatibles, comprobando ambas rutas de disco y sin sustituir textos ingleses por rótulos japoneses de PC. Original debe seguir ofreciendo sus sprites originales.

Estado: fondos HD integrados experimentalmente; selector/preparación en launcher implementados; inventario y decodificación de personajes verificados. Los sprites HD de personajes todavía no se están dibujando durante el juego.
