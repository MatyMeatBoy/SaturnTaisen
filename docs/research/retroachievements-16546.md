# RetroAchievements 16546 en Saturn

Consulta del 18 de noviembre de 2026. La [ficha oficial de Sakura Taisen](https://retroachievements.org/game/16546) muestra 68 logros base, 499 puntos y seis tablas de clasificación. Esta investigación verifica la identificación del disco y el contrato de integración. Quedan pendientes la descarga autenticada del catálogo de condiciones, la prueba de sus disparos y la integración con una cuenta.

## Identificación de los discos

El lector Saturn de rcheevos abre la pista 1 y obtiene los primeros 512 bytes de datos del sector inicial, con la firma de Saturn. El hash identifica la cabecera y solo cubre esos 512 bytes. [Método de identificación](https://docs.retroachievements.org/developer-docs/game-identification.html#sega) · [Código de rcheevos v12.5.0](https://github.com/RetroAchievements/rcheevos/blob/v12.5.0/src/rhash/hash_disc.c#L1191-L1218).

Se compiló un programa privado con el rcheevos oficial v12.5.0 y se llamó a `rc_hash_generate` con `RC_CONSOLE_SATURN` (39) sobre los CUE preparados. Los resultados también coincidieron con el MD5 de los primeros 512 bytes de la pista ISO MODE1/2048. Ambas filas corresponden a los hashes publicados para el juego 16546. [Hashes oficiales](https://retroachievements.org/game/16546/hashes).

| Entrada local | Hash calculado por rcheevos | Etiqueta oficial |
| --- | --- | --- |
| Disco 1, inglés v2.1 | `c4db9d08d56d1fbf78322852775d4818` | Japan · Disc 1 (6M) |
| Disco 2, inglés v2.1 | `c306c094d0177459b31f411cd4cd44a9` | Japan · Disc 2 (6M) |
| Disco 1, compilación española local | `c4db9d08d56d1fbf78322852775d4818` | Japan · Disc 1 (6M) |

El hash por sí solo no permite distinguir esas traducciones de las ediciones japonesas de la tabla. Para habilitar evaluación y envío futuros hace falta identificar el medio local completo y validar por variante las lecturas y condiciones. La prueba de disco 2 calcula su identidad. El cambio natural de disco requiere probar la continuidad de sesión y pasar el hash del medio entrante mediante la API de cambio de medio de rcheevos. [Integración de `rc_client`](https://github.com/RetroAchievements/rcheevos/wiki/rc_client-integration) · [Pruebas de compatibilidad de traducciones](https://docs.retroachievements.org/guidelines/content/player-compatibility-testing.html).

## Mapa de memoria

El mapa de rcheevos expresa los rangos como offsets de RetroAchievements y dos regiones de 1 MiB. El SDK local expone `satrecomp::Ram` con los dos bancos y los bytes de invitado en orden big-endian. [Mapa Saturn en rcheevos v12.5.0](https://github.com/RetroAchievements/rcheevos/blob/v12.5.0/src/rcheevos/consoleinfo.c#L863-L869).

| Rango de RetroAchievements | Banco Saturn | Dirección SH-2 inicial |
| --- | --- | --- |
| `0x000000–0x0FFFFF` | Work RAM Low | `0x00200000` |
| `0x100000–0x1FFFFF` | Work RAM High | `0x06000000` |

El adaptador propuesto leería bytes directamente y acotaría cada tramo al final de su banco antes de continuar en el siguiente. Las direcciones desde `0x200000` quedan fuera del mapa. El orden solicitado por la condición lo interpreta rcheevos. La comprobación debe cubrir lecturas en el borde, multibyte, orden de bytes, reinicios, cambio de disco y estados cargados. Evaluar una vez por fotograma confirmado y omitir las iteraciones de run-ahead, el renderizado y las reproducciones de diagnóstico. Usar lecturas en el hilo dueño de la máquina y vaciar eventos de red en ese hilo. Coordinar el reinicio o la restauración del estado de condiciones al cargar estados, con serialización acotada mediante la API del cliente. [Callback de memoria y API de ejecución](https://github.com/RetroAchievements/rcheevos/blob/v12.5.0/include/rc_client.h).

## Catálogo, insignias y conexión

| Bloque | Flujo documentado |
| --- | --- |
| Catálogo 1:1 | Usar el conjunto aprobado por el servicio y sus IDs, textos, puntos y condiciones. `rc_client_create_achievement_list` representa el conjunto cargado. La API web Game Extended entrega metadatos con una web API key y cumple otra función. El HTML público aporta referencia de inventario. |
| Insignias | Usar la URL que devuelve `rc_client_achievement_get_image_url` para el estado bloqueado o desbloqueado. Cachear por ID y estado en el perfil, con límites de caché y un sustituto visual si falta la imagen. |
| Inicio de sesión | Pedir contraseña solo al iniciar sesión, luego conservar el token por cuenta si el usuario activa Recordar. Usar `rc_client_begin_login_with_password` o `rc_client_begin_login_with_token`. El anfitrión suministra transporte HTTPS asíncrono, límites y UI. |
| Casual y desconexión | Inicializar con Hardcore deshabilitado. El cliente reintenta fallos transitorios de premios en la sesión activa y publica eventos de desconexión y reconexión. El host sigue atendiendo `rc_client_idle` mientras el juego está en pausa. |
| Arranque offline y persistencia | Mantener por separado una copia local verificada del conjunto, el historial offline y la cola de una cuenta autenticada. Inicializar una sesión nueva sin internet requiere resolver el origen y las reglas de caché de las condiciones. La cola en memoria de rcheevos por sí sola se pierde al salir. |

[API de `rc_client`](https://github.com/RetroAchievements/rcheevos/wiki/rc_client-integration) · [Reintentos en el cliente](https://github.com/RetroAchievements/rcheevos/blob/v12.5.0/src/rc_client.c#L4615-L4705) · [Game Extended](https://api-docs.retroachievements.org/v1/get-game-extended.html) · [Guía de insignias](https://docs.retroachievements.org/guidelines/content/badge-and-icon-guidelines.html).

El patrón de ReKHCoM separa logros locales sin cuenta, sesión online Casual y reintentos tras perder red. Su fuente mantiene una cola por usuario con fecha y valida un subconjunto habilitado de condiciones para medios compatibles. Su documento de validación separa deliberadamente proyección de RAM, prueba local y habilitación oficial. Saturn debe validar su mapa y sus condiciones propios. [Cliente de ReKHCoM](https://github.com/MatyMeatBoy/ReKHCoM/blob/6c1951273fc2ccf79369cead1ba207e7297b931d/port/achievements/ra_client.c) · [Persistencia offline](https://github.com/MatyMeatBoy/ReKHCoM/blob/6c1951273fc2ccf79369cead1ba207e7297b931d/port/achievements/offline_achievements.c) · [Validación de ReKHCoM](https://github.com/MatyMeatBoy/ReKHCoM/blob/6c1951273fc2ccf79369cead1ba207e7297b931d/port/progress/RETROACHIEVEMENTS_71_VALIDACION.md).

## Pendientes comprobables

- Revisar la vía de integración y la compatibilidad por medio antes de sincronizar con una cuenta. La guía Standalone excluye los ports no oficiales de los sets de esa categoría. Aquí se estudia el conjunto Saturn existente mediante su mapa de memoria canónico. La guía de `rc_client` menciona la identificación del cliente con un User-Agent para Hardcore. El desarrollo local y las pruebas de Casual con transporte simulado pueden avanzar en paralelo a esta revisión. La compatibilidad oficial y la sincronización con una cuenta siguen sin verificar. [Standalone Support](https://docs.retroachievements.org/general/standalone-support.html) · [Integración de `rc_client`](https://github.com/RetroAchievements/rcheevos/wiki/rc_client-integration).
- Obtener el catálogo por un canal soportado, registrar revisión e IDs distintos, y comprobar su paridad. Mantener las respuestas, las insignias y el progreso en caché local. Antes de considerar un arranque desde cero sin red con 68 condiciones, confirmar la vía de distribución o instalación del conjunto.
- Probar lecturas y disparos primero con transporte desconectado y memoria capturada en rutas naturales contra una referencia Saturn. Incluir falsos positivos en guardados, reset, transición entre discos y carga de estados. Probar login, expiración, reintentos, almacenamiento por cuenta y reapertura de la cola en un servidor simulado antes de una prueba autorizada de sync.
- Conservar desbloqueos obtenidos sin cuenta como progreso local. Los reintentos de una sesión autorizada deben conservar el usuario, juego, hash, ID y fecha de origen y retirarse solo tras confirmación de servicio. Las rutas que conceden o sincronizan logros requieren validación del cliente y la sesión.

La investigación no inició sesión, no envió desbloqueos ni actualizó el servicio. Las fuentes, el ejecutable del sondeo, su log de hashes y las lecturas de referencia se conservan en la carpeta privada de investigación.
