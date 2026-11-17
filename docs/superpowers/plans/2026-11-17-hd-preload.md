# Precarga HD opcional

Opción en tarjeta MOD HD del launcher y ajustes Pantalla. Por defecto desactivada. Al activarse, antes del primer frame listo se cargan los fondos disponibles y variantes de retratos HD habilitadas. Barra visible y contador en el título; launcher conserva su espera hasta confirmar primer frame. CPU/renderer propios del hilo de ventana; no cambia los tiempos del CD invitado.

Fondos conservan su caché validada y su subida SDL en el hilo principal. Retratos verifican tamaño/hash/dimensiones antes de decodificar; la precarga guarda ambas densidades en memoria, máximo394 pares (~25MiB de píxeles). Sin precarga solo se conserva un atlas activo. Recurso fallido conserva fallback original. Los fondos PC se omiten si están desactivados. Memoria liberada al cerrar/recrear ventana.

Evidencia: escena idéntica entre carga normal y anticipada. Prueba aislada con el pack completo disponible:38/38 fondos,382 variantes de191 retratos,0 errores. Pruebas reales de720p,900p,1080p,1440p,2160p y ancho3440 previas a eliminar soporte ultrawide; cambios limitados al retrato. PNG corrupto o manifiesto ausente conserva la captura original exacta. No equivale al pack completo de cuerpos NC ni a validar toda la campaña.
