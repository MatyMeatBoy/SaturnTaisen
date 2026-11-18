# Cuarto lote de retratos HD

Lote T09: 74 identidades nuevas (39 + 35 de Iris) (201 → 275 de 304) con base, ojos y boca. Aceptadas por métrica de paleta independiente por región (base, tira 1, tira 2), candidato PC = ID−1 sin desplazamiento, tiras por debajo de 0,12 y mejores que la intercambiada. Los ambiguos se rechazan.

- Registro revisado: `config/hd-portrait-reviewed.json` (hashes de píxeles PC y variantes 1×/2×).
- Pack exportado en local con 275 retratos y 19 fondos; carga con el runtime 674.182 y 0 bloques interpretados.
- No verificado en juego: el barrido de 106 estados no mostró ningún retrato sustituido (ni de los ya aprobados), por lo que no es concluyente.
- Pendientes (64): Iris 0091–00c5 (atlas nativos con banco de paleta erróneo), 0046/004f/0061, 00f3/00fb, 010d/010f, 011e/011f/0121, 013a–013f, 0152/0153, 0169, 0171/0172, 0185–018a.

## Iris (35 identidades, 0091–00c5)

El rechazo previo se debía a la paleta: los atlas nativos de Iris se decodifican con el banco CRAM 4 de `iris-correct-room-3000.state`. Con ese banco, el 100 % de los 37 candidatos ID−1 es el primero en la comparación RGB y una hoja visual (nativo | PC) coincide en expresión, rubor y boca. Se aceptan 35; `00a1` queda en T45 (tiras intercambiadas). Pack de 275 retratos: carga con 0 bloques interpretados; sin retrato de Iris observado en juego aún.
