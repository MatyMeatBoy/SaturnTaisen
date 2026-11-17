# Validación jugable del capítulo1

Objetivo inmediato: demostrar una ruta reproducible desde New Game hasta el final del episodio1, guardado del juego y Continue, antes de afirmar capítulo completo. Mantener Saturn como prioridad y no confundir mejoras visuales con progresión validada.

1. Inventariar ruta continua existente de119.781 frames: llega a pasillo y no incluye batalla. Registrar anclas de historia, elecciones y acceso a combate.
2. Desde estado local de combate, avanzar controles y turnos para verificar movimiento/ataque, victoria y salida. Usar copias de backup y movies deterministas; conservar comandos y hashes. Los estados facilitan investigar y no cuentan como ruta continua desde inicio.
3. Si falta bloque AOT, reproducir y atribuir a módulo real; generar de forma estática los candidatos necesarios sin habilitar intérprete en producción. Comparar el tramo con referencia cuando haya dudas de semántica/estado.
4. Componer un recorrido continuo desde el arranque, sin saltos mediante estados. Guardar una partida nativa del final del episodio, reiniciar y cargarla con Continue. Verificar dos repeticiones y ningún fallback interpretado.
5. Documentar por separado pruebas pasadas, rutas alternativas pendientes y estado de campaña/discos. Añadir una regresión por bloqueo corregido, sin tests que solo repitan la implementación.

Fuera de esta prueba: cuerpos HD, PixelGen en mapa y combate panorámico no deben cambiar lógica ni colisiones; investigar HUD relativo después de una base de progreso reproducible. Capítulo1 no se considera verificado hasta lograr4.
