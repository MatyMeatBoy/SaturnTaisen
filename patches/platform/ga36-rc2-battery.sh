#!/bin/sh
set -u
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$here"
mkdir -p user
bundle=$(mktemp -d "$here/user/rc2-bateria.XXXXXX") || exit 1
exec >"$bundle/resumen.log" 2>&1
export SATURNTAISEN_DIAG_ROOT="$bundle" SATURNTAISEN_DIAG_FRAMES=750 SATURNTAISEN_DIAG_PROFILE=0
printf 'RC2 laboratorio: 750 cuadros, sin pulsar botones; orden RC1 RC2 RC2 RC1\n'
failed=0
for pair in 1:rc1 2:rc2 3:rc2 4:rc1; do
 index=${pair%:*}; variant=${pair#*:}
 printf 'inicio caso=%s variante=%s\n' "$index" "$variant"
 SATURNTAISEN_DIAG_PROGRAM=$variant /bin/sh "$here/ga36-rc2-case.sh" es
 result=$?
 printf 'fin caso=%s exit_code=%s\n' "$index" "$result"
 [ "$result" -eq 0 ] || failed=1
done
printf 'bateria_exit_code=%s\n' "$failed"
exit "$failed"
