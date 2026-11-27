# timeout: 900
# RC11 as played (no --hash-log), all on: compose thread off/on, attack and map; real screen with the compose
# thread, with and without composing 1 frame of 2; then fbbench (writes back the pixels the screen shows)
g=/home/player/ports/saturntaisen; u=$g/usb; m=$u/medir.sh; b=$u/bin/rc11/sakura
[ -x $b ] || { echo "sin RC11"; exit 3; }
export SATRECOMP_VIDEO_THREAD=1 SATRECOMP_SOUND_THREAD=1 SATRECOMP_VIDEO_THREAD_STATS=1 NOHASH=1
sh $m c0 $b attack 600 headless
SATRECOMP_COMPOSE_THREAD=1 sh $m c1 $b attack 600 headless
sh $m c0 $b map 600 headless
SATRECOMP_COMPOSE_THREAD=1 sh $m c1 $b map 600 headless
SATRECOMP_COMPOSE_THREAD=1 sh $m c1 $b attack 600 fbdev
grep "frame profile\|SDL_Init" $u/med/c1-attack-fbdev/err.txt | head -12
SATRECOMP_COMPOSE_THREAD=1 SATRECOMP_FRAME_SKIP=2 sh $m c1s2 $b attack 600 fbdev
grep "frame profile" $u/med/c1s2-attack-fbdev/err.txt | head -12
chmod +x $u/fbbench && $u/fbbench
rm -f $u/fbbench
