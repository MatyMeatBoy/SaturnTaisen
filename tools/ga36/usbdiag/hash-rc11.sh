# timeout: 900
# RC11 all on, without --hash-log (as played): compose thread off and on, attack and map; then the real screen
# with the compose thread and with it plus composing 1 frame of 2. Then a hash check (attack, 300 frames) on/off.
g=/home/player/ports/saturntaisen; u=$g/usb; m=$u/medir.sh; b=$u/bin/rc11/sakura
[ -x $b ] || { echo "sin RC11"; exit 3; }
export SATRECOMP_VIDEO_THREAD=1 SATRECOMP_SOUND_THREAD=1 SATRECOMP_VIDEO_THREAD_STATS=1
NOHASH=1 sh $m c0 $b attack 600 headless
NOHASH=1 SATRECOMP_COMPOSE_THREAD=1 sh $m c1 $b attack 600 headless
NOHASH=1 sh $m c0 $b map 600 headless
NOHASH=1 SATRECOMP_COMPOSE_THREAD=1 sh $m c1 $b map 600 headless
NOHASH=1 SATRECOMP_COMPOSE_THREAD=1 sh $m c1 $b attack 600 fbdev
grep "frame profile\|fbdev\|SDL" $u/med/c1-attack-fbdev/err.txt | head -12
NOHASH=1 SATRECOMP_COMPOSE_THREAD=1 SATRECOMP_FRAME_SKIP=2 sh $m c1s2 $b attack 600 fbdev
grep "frame profile" $u/med/c1s2-attack-fbdev/err.txt | head -3
sh $m h0 $b attack 300 headless
SATRECOMP_COMPOSE_THREAD=1 sh $m h1 $b attack 300 headless
cmp $u/med/h0-attack-headless/hash.txt $u/med/h1-attack-headless/hash.txt && echo "hash igual con y sin hilo de composicion"
df -k /home/player | tail -1
