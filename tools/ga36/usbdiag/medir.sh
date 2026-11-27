# timeout: 600
# SaturnTaisen GA36: medir un binario sin instalar nada. El binario corre desde usb/bin/<etiqueta> (enlace duro,
# sin release.marker al lado) para que acepte los estados de prueba.
# Uso: sh medir.sh ETIQUETA BINARIO ESCENARIO CUADROS [headless|fbdev] [opciones extra]
g=/home/player/ports/saturntaisen; u=$g/usb; cd "$g" || exit 3
tag=$1; exe=$2; scen=$3; n=$4; mode=${5:-headless}; shift 5 2>/dev/null; extra="$*"
o=$u/med/$tag-$scen-$mode; rm -rf "$o"; mkdir -p "$o" "$u/bin/$tag"
b=$u/bin/$tag/sakura
[ "$b" -ef "$exe" ] || { rm -f "$b"; ln "$exe" "$b" 2>/dev/null || { echo "sin enlace duro: $exe se corre en su sitio"; rmdir "$u/bin/$tag" 2>/dev/null; b=$exe; }; }
export LD_LIBRARY_PATH=$g/lib SATRECOMP_LAZY_BLOCKS=1 SATRECOMP_FRAME_PROFILE=1
# (the binary finds its SDL through $ORIGIN/lib before the system one: a test binary gets a copy of the port's)
d=$(dirname "$b"); [ "$d" = "$g" ] || [ -r "$d/lib/libSDL3.so.0" ] || { mkdir -p "$d/lib"; cp $g/lib/libSDL3.so.0 "$d/lib/"; }
read -r SATRECOMP_WARM_BLOCK_PAGES <warm-pages.txt; export SATRECOMP_WARM_BLOCK_PAGES
export SATRECOMP_OPTI36S_CSV=$o/frames.csv SDL_AUDIO_DRIVER=dummy
if [ "$mode" = fbdev ]; then
  # this SDL has no dummy audio driver; the real launcher uses alsa
  export SATURNTAISEN_FBDEV=/dev/fb0 SDL_VIDEO_DRIVER=dummy SDL_RENDER_DRIVER=software SATRECOMP_WINDOW_LOG=1 SDL_AUDIO_DRIVER=alsa
  disp="--windowed --scale 2"
else disp=--headless; fi
# (NOHASH=1: as played, without the per-frame state hash, which costs some 5 ms a frame on the board)
if [ -n "$NOHASH" ]; then hashopt=; else hashopt="--hash-log $o/hash.txt"; fi
pg0=$(awk '/^pgmajfault/{print $2}' /proc/vmstat); t0=$(cut -d' ' -f1 /proc/uptime)
env ${GAME_PRELOAD:+LD_PRELOAD=$GAME_PRELOAD} "$b" $disp --unthrottled --stats --frames "$n" --disc game/es/disc1/game.cue --backup "$o/backup.bin" \
  --state-load 0:$u/$scen.state --movie $u/$scen.movie $hashopt $extra >"$o/out.txt" 2>"$o/err.txt" &
p=$!
while [ -r /proc/$p/stat ]; do
  echo "$(cut -d' ' -f1 /proc/uptime) $(cut -d' ' -f10-17,20 /proc/$p/stat 2>/dev/null) $(awk '/^VmRSS/{print $2}' /proc/$p/status 2>/dev/null) $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq)"
  for t in /proc/$p/task/*; do printf 'T %s %s\n' "$(cat $t/comm 2>/dev/null)" "$(cut -d' ' -f10,12,14,15 $t/stat 2>/dev/null)"; done
  sleep 1
done >"$o/sys.txt"
wait $p; r=$?; t1=$(cut -d' ' -f1 /proc/uptime); pg1=$(awk '/^pgmajfault/{print $2}' /proc/vmstat)
echo "== $tag $scen $mode salida $r tiempo $t0 -> $t1 majflt_sistema $((pg1-pg0))"
sha256sum "$o/hash.txt" 2>/dev/null | cut -c1-16
grep -v '^opti36s-parts' "$o/err.txt" | grep -i "state\|frame profile\|error" | head -20
awk '/^opti36s-parts/ && $2>=20 {t+=$3;c+=$4;v+=$5;s+=$6;k++} END {if(k) printf "cuadros 20+: %d, medio %.1f ms (sh2 %.1f video %.1f sonido %.1f) = %.1f fps\n",k,t/k,c/k,v/k,s/k,1000*k/t}' "$o/err.txt"
grep -E "video thread|counted wait|idle loops|sound thread|sound bus" "$o/err.txt"
tail -n 9 "$o/sys.txt" | grep -v '^T' | tail -n 2
