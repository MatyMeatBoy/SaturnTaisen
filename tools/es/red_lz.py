"""Compresor/descompresor LZ de los graficos de Sakura Taisen (Saturn).

Formato obtenido de la rutina SH-2 del programa /SAKURA en 0x0600A164
(r4=origen, r5=destino; devuelve bytes escritos). Hay una variante
incremental con estado en 0x0600A200 que acepta el mismo flujo.

Flujo: bits de control leidos de bytes de bandera, LSB primero; el byte de
bandera se lee del flujo en el momento en que se necesita su primer bit
(entre los datos de los tokens). Tokens:

  1               literal: copia 1 byte
  0 0 a b  X      corto:   distancia 256-X (1..256), longitud (a<<1|b)+2 (2..5)
  0 1      L H    largo:   w=L|H<<8; distancia = 8192-(w>>3) (1..8192)
                           si w&7: longitud = (w&7)+2 (3..9)
                           si no:  sigue un byte N, longitud N+1 (1..256)
  0 1      00 00  fin del flujo

Las copias se hacen byte a byte (pueden solaparse).
"""
from __future__ import annotations

import argparse
import sys

__all__ = ['decompress', 'decompress_ex', 'compress']


class FormatError(ValueError):
    pass


def decompress_ex(data: bytes, start: int = 0, limit: int = 1 << 24):
    """Descomprime desde data[start]; devuelve (salida, bytes_consumidos)."""
    if type(start) is not int or type(limit) is not int or not 0 <= start <= len(data) or limit < 0:
        raise FormatError('origen o límite inválido')
    out = bytearray()
    pos = start
    n = len(data)
    flags = 0
    left = 0

    def byte():
        nonlocal pos
        if pos >= n:
            raise FormatError('flujo truncado')
        v = data[pos]
        pos += 1
        return v

    def bit():
        nonlocal flags, left
        if left == 0:
            flags = byte()
            left = 8
        b = flags & 1
        flags >>= 1
        left -= 1
        return b

    while True:
        if bit():
            if len(out) >= limit:
                raise FormatError('salida demasiado larga')
            out.append(byte())
            continue
        if bit():
            lo = byte()
            hi = byte()
            w = lo | hi << 8
            if w == 0:
                break
            dist = 8192 - (w >> 3)
            if w & 7:
                count = (w & 7) + 2
            else:
                count = byte() + 1
        else:
            count = (bit() << 1 | bit()) + 2
            dist = 256 - byte()
        src = len(out) - dist
        if src < 0:
            raise FormatError('referencia antes del inicio (pos %#x)' % pos)
        if count > limit - len(out):
            raise FormatError('salida demasiado larga')
        for i in range(count):
            out.append(out[src + i])
    return bytes(out), pos - start


def decompress(data: bytes) -> bytes:
    return decompress_ex(data)[0]


class _Writer:
    def __init__(self):
        self.out = bytearray()
        self.flagpos = -1
        self.nbits = 8

    def bit(self, b):
        if self.nbits == 8:
            self.flagpos = len(self.out)
            self.out.append(0)
            self.nbits = 0
        if b:
            self.out[self.flagpos] |= 1 << self.nbits
        self.nbits += 1

    def byte(self, v):
        self.out.append(v & 0xFF)


def _token_cost(dist, length):
    """Coste en bits del mejor token para (dist, length) o None."""
    best = None
    if 2 <= length <= 5 and dist <= 256:
        best = 12
    if dist <= 8192:
        if 3 <= length <= 9:
            c = 18
        elif length <= 256:
            c = 26
        else:
            c = None
        if c is not None and (best is None or c < best):
            best = c
    return best


def compress(data: bytes) -> bytes:
    """Compresion LZ con analisis optimo (programacion dinamica)."""
    data = bytes(data)
    n = len(data)
    # Indice de posiciones por prefijo de 2 bytes para buscar coincidencias.
    heads = {}
    chains = [-1] * n
    MAXCHAIN = 256
    # matches[i] = lista de (longitud, distancia) candidatas
    cost = [0] * (n + 1)
    choice = [None] * (n + 1)
    # Precalcular coincidencias de izquierda a derecha.
    cand = [None] * n
    for i in range(n):
        res = []
        if i + 1 < n:
            key = data[i] | data[i + 1] << 8
            j = heads.get(key, -1)
            steps = 0
            bestlen = 1
            short_best = 1
            while j >= 0 and i - j <= 8191 and steps < MAXCHAIN:
                d = i - j
                m = 0
                lim = min(256, n - i)
                while m < lim and data[j + m] == data[i + m]:
                    m += 1
                if d <= 256 and m > short_best and m >= 2:
                    short_best = m
                    res.append((min(m, 256), d))
                elif m > bestlen:
                    res.append((m, d))
                if m > bestlen:
                    bestlen = m
                if m == lim and d > 256:
                    break
                j = chains[j]
                steps += 1
            chains[i] = heads.get(key, -1)
            heads[key] = i
        # Coincidencias de distancia 1..2 (rachas) aunque no esten en la cadena
        cand[i] = res
    INF = 1 << 60
    cost = [INF] * (n + 1)
    cost[n] = 0
    for i in range(n - 1, -1, -1):
        best = cost[i + 1] + 9
        bc = None
        for m, d in cand[i]:
            # Probar longitudes utiles: todas hasta m (acotado)
            for L in _lengths(m, d):
                c = _token_cost(d, L)
                if c is None:
                    continue
                v = cost[i + L] + c
                if v < best:
                    best = v
                    bc = (L, d)
        cost[i] = best
        choice[i] = bc
    w = _Writer()
    i = 0
    while i < n:
        ch = choice[i]
        if ch is None:
            w.bit(1)
            w.byte(data[i])
            i += 1
            continue
        L, d = ch
        if 2 <= L <= 5 and d <= 256 and _token_cost(d, L) == 12:
            w.bit(0); w.bit(0)
            v = L - 2
            w.bit(v >> 1 & 1); w.bit(v & 1)
            w.byte(256 - d)
        else:
            w.bit(0); w.bit(1)
            hiw = (8192 - d) << 3
            if 3 <= L <= 9:
                v = hiw | (L - 2)
                w.byte(v); w.byte(v >> 8)
            else:
                w.byte(hiw); w.byte(hiw >> 8)
                w.byte(L - 1)
        i += L
    w.bit(0); w.bit(1)
    w.byte(0); w.byte(0)
    return bytes(w.out)


def _lengths(m, d):
    if m <= 9:
        return range(2, m + 1)
    # mas largas: todas las de 2..9 y luego la maxima (y alguna intermedia)
    return list(range(2, 10)) + [m]


def _main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('modo', choices=['d', 'c'])
    ap.add_argument('entrada')
    ap.add_argument('salida')
    ap.add_argument('--offset', type=lambda s: int(s, 0), default=0)
    a = ap.parse_args()
    raw = open(a.entrada, 'rb').read()
    if a.modo == 'd':
        out, used = decompress_ex(raw, a.offset)
        print('consumidos %d bytes, salida %d bytes' % (used, len(out)))
    else:
        out = compress(raw)
        print('entrada %d bytes, comprimido %d bytes' % (len(raw), len(out)))
    open(a.salida, 'wb').write(out)


if __name__ == '__main__':
    _main()
