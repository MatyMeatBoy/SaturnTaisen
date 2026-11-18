# Crossfade del mapa al comedor

La ruta `map-room.state` y `tests/chapter1-map-dining-hall.movie` se reprodujo durante 900 fotogramas en Original y Mejorado con el mismo ejecutable del parche 44. Mejorado usó Zoom a 2560×1440, los recursos locales de la entrega y el paquete HD preparado v0.1.2. Las dos ejecuciones produjeron el mismo registro de hashes del juego y las nueve capturas RGB nativas fueron idénticas. Ambas registraron cero bloques interpretados.

| Comprobación de la salida presentada | Fotogramas de captura | Resultado |
| --- | --- | --- |
| Franja exterior del mapa contra el mapa previo y el fondo floral posterior | 403, 405, 410, 425, 450, 464 | 854 muestras por captura coincidieron exactamente con pesos de mapa de 32, 32, 29, 22, 9 y 2 sobre 32. |
| Imagen del comedor con el encuadre Zoom de la escena estable | 490, 500, 520 | 5.184 muestras por captura coincidieron con pesos de imagen de 5, 10 y 20 sobre 32. Imagen de 2016×1008, escala 7. |
| Sombra derecha del comedor con RGB nativo `505050` | 490, 500, 520 | 890 muestras por captura coincidieron con los mismos pesos de la imagen. El desplazamiento fue de 28 píxeles. |
| Cursor contra el borde superior izquierdo | 175 en una reproducción separada | El gradiente siguió ocupando el ancho. Esta reproducción permaneció en el mapa después de pulsar A con el cursor fuera de una sala. |

El exterior del mapa usa sus píxeles nativos de borde y el fondo floral muestreado en la misma posición final que el centro. La comparación del exterior usa columnas a ambos lados de la vista nativa. En algunas filas, el RGB del borde interior cambia unos niveles respecto al fotograma 400 incluso con peso de mapa completo. Ese fotograma sirve de referencia para el exterior. La prueba de igualdad del RGB nativo usa las dos ejecuciones del mismo fotograma.

En el compositor del Saturn, las muestras nativas 410, 425 y 450 verificaron la mezcla de NBG3 sobre NBG0 en los 71.255 píxeles fuera del cursor por muestra. La captura de ventana y el estado guardado pueden corresponder a pasos adyacentes del fundido. Por eso la tabla usa los pesos medidos directamente en cada captura de ventana.

Evidencia privada en `local/work/map-floral-fade-final/`. Los manifiestos conservan los comandos, perfiles, entradas y hashes. El ejecutable tiene SHA-256 `de45af3dcb7713921c88bda56e71f611b1de4c738f3472ae28e52385c38a9800` y el registro de hashes del juego tiene SHA-256 `49e4093e867bd76fe1137f69da9a0a48b0fd8c50837d44254347d9a89173a593`. La validación cubre esta entrada al comedor y la oclusión del gradiente por el cursor en el mapa. Falta una entrada a sala con el cursor junto al borde en el primer fotograma del fundido.
