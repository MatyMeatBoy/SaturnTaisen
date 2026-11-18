# Reproducción de la ampliación AOT de combate

`tools/discover_battle_overlays.py` sustituye el ensayo privado que amplió la familia K001–K019 después del bloqueo de Sumire en 060783FC. No modifica discos, la base de descubrimiento activa ni ejecutables. Lee una base semilla y emite un candidato y su manifiesto en un directorio privado nuevo.

Se reutiliza el analizador estático del proyecto y el SDK fijado. Los módulos deben pertenecer exactamente a la familia conocida, tener tamaño/alineación acotados y punteros absolutos que apoyen la base observada 06078000. El analizador no puede emitir bytes ni direcciones ajenos al módulo. Se deduplican módulos iguales, pero se conservan variantes distintas en una misma dirección de CPU y todos los perfiles de procedencia. Esto genera candidatos; no acredita que cada entrada sea código ejecutado.

## Resultado reproducido

Desde la semilla privada anterior al arreglo, 580.328 entradas, se recuperaron 18 módulos únicos y 33.696 candidatos nuevos: **614.024 entradas**, exactamente el mismo conjunto que usa la build test.1. Ninguna entrada faltó ni sobró. El [manifiesto](battle-overlay-reproduction.json) conserva hashes, perfiles y recuentos; los bytes de código quedan en `local/work`, fuera de Git.

No se regeneró ni sustituyó el ejecutable compartido para esta comprobación. La corrección de Sumire y su paridad AOT/intérprete ya se documentaron en [progresión del capítulo 1](chapter1-battle-progress.md). Esta reproducción elimina una dependencia de scripts privados al reconstruir aquel arreglo; no demuestra campaña completa ni resuelve módulos nuevos de otros capítulos.

## Uso

Ejemplo desde la raíz de un checkout con las dos imágenes propias preparadas:

```powershell
python tools/discover_battle_overlays.py `
  --disc "disc1=local/prepared/disc1/Track 01.iso" `
  --disc "disc2=local/prepared/disc2/Track 01.iso" `
  --seed-blocks local/work/sakura/blocks-before-k-family.txt `
  --output local/work/battle-overlay-reproduction
```

Para un worktree sin SDK propio, `--sdk-root` puede indicar la dependencia existente y los argumentos de imagen/semilla pueden ser rutas absolutas. El SDK debe tener el commit fijado. El ensayo registrado incluyó también los dos perfiles japoneses disponibles para contrastar variantes. El manifiesto distingue las imágenes efectivamente incluidas en cada ejecución.

La salida no se promociona automáticamente. Comparar el conjunto, revisar el manifiesto y coordinar la regeneración/compilación antes de sustituir `blocks.txt`. Nunca hacerlo mientras otro colaborador utiliza esa base o compila. La CLI rechaza destinos existentes y destinos fuera de `local/work`.

Pruebas: `python -m unittest discover -s tests -p test_battle_overlay_discovery.py -v`. Cubren selección de familia, tamaños, punteros, variantes, rechazo de candidatos inválidos y validación de la semilla sin modificarla.
