# timeout: 900
# Installs RC31 (patches 0354-0363 on the RC lab base) as the port's game, keeping what was there to go back:
#   sakura -> sakura.rc3-antes, lib/libSDL3.so.0 -> lib/libSDL3.so.0.neon1-antes, launch.sh -> launch.sh.antes-rc31
# The new SDL is the one with the NEON present paths (ga36-sdl3-neon-present.patch); launch.sh gets the three threads.
g=/home/player/ports/saturntaisen; u=$g/usb
# room: the RC32 test binary goes (its SDL is the new one, kept for the port)
[ -r $u/bin/rc32/lib/libSDL3.so.0 ] && cp $u/bin/rc32/lib/libSDL3.so.0 $u/libSDL3-neon2.so.0
rm -f $u/bin/rc32/sakura; rm -rf $u/bin/rc32
df -k /home/player | tail -1
cat $u/rc31.xz.00 $u/rc31.xz.01 $u/rc31.xz.02 $u/rc31.xz.03 $u/rc31.xz.04 $u/rc31.xz.05 $u/rc31.xz.06 > $u/rc31.xz
if [ "$(sha256sum $u/rc31.xz | cut -d' ' -f1)" != f910f6f51c67e4c284d24e72a95f6c55ae3ee38d9b3a405910073548e78681e4 ]; then
  echo "xz distinto; las partes se quedan"; ls -la $u/rc31.xz.*; rm -f $u/rc31.xz; exit 2
fi
for n in 00 01 02 03 04 05 06; do rm -f "$u/rc31.xz.$n"; done
unxz -c $u/rc31.xz > $u/sakura-rc31.new &
x=$!
while kill -0 $x 2>/dev/null; do sleep 30; echo "descomprimiendo: $(ls -la $u/sakura-rc31.new | awk '{print $5}') bytes"; done
wait $x; rm -f $u/rc31.xz
if [ "$(sha256sum $u/sakura-rc31.new | cut -d' ' -f1)" != 6a12e53a488e2ff939decba3a9ea2dcf27a12c9e3f488366ab2f812c22146a44 ]; then
  echo "RC31 distinto, no se instala"; rm -f $u/sakura-rc31.new; exit 3
fi
echo "RC31 OK"
# the swap (renames on the same card: no extra room)
[ -e $g/sakura.rc3-antes ] || mv $g/sakura $g/sakura.rc3-antes
mv -f $u/sakura-rc31.new $g/sakura && chmod +x $g/sakura
if [ -r $u/libSDL3-neon2.so.0 ]; then
  [ -e $g/lib/libSDL3.so.0.neon1-antes ] || mv $g/lib/libSDL3.so.0 $g/lib/libSDL3.so.0.neon1-antes
  mv -f $u/libSDL3-neon2.so.0 $g/lib/libSDL3.so.0
fi
if ! grep -q SATRECOMP_COMPOSE_THREAD $g/launch.sh; then
  cp $g/launch.sh $g/launch.sh.antes-rc31
  sed -i 's#^export SATRECOMP_LAZY_BLOCKS=1$#export SATRECOMP_LAZY_BLOCKS=1\n\# RC31: the renderer, the sound side and the final composition on cores of their own (0 turns each off)\nexport SATRECOMP_VIDEO_THREAD="${SATRECOMP_VIDEO_THREAD:-1}"\nexport SATRECOMP_SOUND_THREAD="${SATRECOMP_SOUND_THREAD:-1}"\nexport SATRECOMP_COMPOSE_THREAD="${SATRECOMP_COMPOSE_THREAD:-1}"#' $g/launch.sh
fi
grep -n "THREAD\|LAZY" $g/launch.sh
ls -la $g $g/lib | grep -v "^total"
sha256sum $g/sakura $g/lib/libSDL3.so.0 | cut -c1-16
# a start: 300 frames of the first attack, as played, from the installed binary (its own lib/ through $ORIGIN)
export SATRECOMP_VIDEO_THREAD=1 SATRECOMP_SOUND_THREAD=1 SATRECOMP_COMPOSE_THREAD=1 NOHASH=1
sh $u/medir.sh inst31 $g/sakura attack 300 headless | grep "salida\|cuadros 20"
sh $u/medir.sh inst31 $g/sakura attack 300 fbdev | grep "salida"
grep "frame profile: emulation\|frame profile: presentation\|SDL_Init" $u/med/inst31-attack-fbdev/err.txt | head -3
df -k /home/player | tail -1
