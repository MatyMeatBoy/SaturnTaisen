# timeout: 900
# RC11: join the parts, check the archive before removing anything, unpack to usb/bin/rc11/sakura (a line of
# progress every 30 s: USBdiag cuts a job silent for 5 min); remove what RC7/RC9 left
u=/home/player/ports/saturntaisen/usb
rm -f $u/bin/rc7/sakura $u/rc9.xz; rm -rf $u/bin/rc7
cat $u/rc11.xz.00 $u/rc11.xz.01 $u/rc11.xz.02 $u/rc11.xz.03 $u/rc11.xz.04 $u/rc11.xz.05 $u/rc11.xz.06 > $u/rc11.xz
if [ "$(sha256sum $u/rc11.xz | cut -d' ' -f1)" != 3acd6b1f01f53e91457cbb05db2d26d22cabb0943ab02a9669812839a94863f8 ]; then
  echo "xz distinto; las partes se quedan"; ls -la $u/rc11.xz.*; rm -f $u/rc11.xz; exit 2
fi
for n in 00 01 02 03 04 05 06; do rm -f "$u/rc11.xz.$n"; done
mkdir -p $u/bin/rc11
unxz -c $u/rc11.xz > $u/bin/rc11/sakura &
x=$!
while kill -0 $x 2>/dev/null; do sleep 30; echo "descomprimiendo: $(ls -la $u/bin/rc11/sakura | awk '{print $5}') bytes"; done
wait $x; chmod +x $u/bin/rc11/sakura
rm -f $u/rc11.xz
if [ "$(sha256sum $u/bin/rc11/sakura | cut -d' ' -f1)" = 13c113e5fefb826fa30308dd4337ef507cc9204f66bd3feba5bd0e0c18b5f974 ]; then
  echo "RC11 OK"; rm -rf $u/bin/rc9
else echo "RC11 distinto"; rm -f $u/bin/rc11/sakura; fi
ls -la $u $u/bin $u/bin/* 2>&1 | grep -v "^total"
df -k /home/player | tail -1
