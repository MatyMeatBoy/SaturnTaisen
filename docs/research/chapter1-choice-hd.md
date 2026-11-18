# Texto HD de elecciones LIPS

El patch0045 sustituye las opciones inglesas usando el atlas verificado y los comandos del framebuffer mostrado. Reconoce los paneles de dos o tres opciones por su reloj, modo, bancos, filas y centrado. Cada pixel retirado requiere una placa de glifo y propietarios pertenecientes al mismo panel completo; si hay oclusion, datos incompletos o un glifo desconocido, conserva el texto nativo.

La fuente reutiliza la tipografia HD existente, con transformacion uniforme y recorte propio del panel. Zoom usa la transformacion de la imagen superior; la vista conjunta conserva su propio encuadre. No cambia pulsaciones, temporizador ni logica del juego. La sustitucion se activa con texto HD en Mejorado y el atlas ingles conocido; otros idiomas requieren su atlas validado y siguen pendientes.

## Evidencia real

Se ejecutaron diez perfiles a1600x900: Original y Mejorado con Zoom/conjunto, cada uno con texto HD/nativo. Dos escenas privadas del capitulo1 aportaron paneles de dos y tres opciones. Cada perfil ejecuto240fotogramas, con las mismas pulsaciones de seleccion y confirmacion.

- Los240hashes por escena fueron identicos entre sus cinco perfiles; todas las ejecuciones terminaron con cero bloques interpretados.
- Los perfiles HD reconocieron dos o tres filas completas con saved_under=1.
- Capturas8 y31: diferencias limitadas a las zonas de texto del panel; reloj, marco y resaltado no cambian respecto al mismo perfil sin texto HD.
- Captura59: HD y nativo son identicos tras desaparecer las opciones; no quedan letras residuales.
- Captura230: la respuesta inferior usa el texto HD habitual. Se revisaron visualmente los paneles Zoom de ambas escenas: texto dentro del marco y filas separadas.

Pruebas sinteticas: propiedad compartida de dos glifos, rechazo de propietario externo, filas incompletas, centrado/clip y datos ambiguos. Pasaron el fixture de elecciones y los fixtures de placa de glifos y VDP2. El arbol compuesto del SDK coincide con los patches0001..0045.

Los estados, capturas, ejecutable y recibo result.json quedan en local/work/choice-text-qa del propietario. Estas pruebas no acreditan todas las elecciones de la campana ni el vencimiento natural del reloj. El patch esta implementado y probado en estas rutas; no esta incluido en los paquetes previamente entregados.
