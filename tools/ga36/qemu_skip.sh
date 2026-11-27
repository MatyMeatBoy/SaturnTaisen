# usage: qemu_skip.sh frames bin   attack: no skip, skip 2 (picture in the hash) and both without the picture
R=/mnt/d/01Claude/Sakurawars/tools/ga36/qemu_wsl_run.sh
n=$1; b=$2
E="SATRECOMP_VIDEO_THREAD=1 SATRECOMP_SOUND_THREAD=1 SATRECOMP_VIDEO_THREAD_STATS=1"
bash $R s1 $n "$E" $b attack > /tmp/s1.r &
bash $R s2 $n "$E SATRECOMP_FRAME_SKIP=2" $b attack > /tmp/s2.r &
bash $R n1 $n "$E SATRECOMP_HASH_NO_PICTURE=1" $b attack > /tmp/n1.r &
bash $R n2 $n "$E SATRECOMP_HASH_NO_PICTURE=1 SATRECOMP_FRAME_SKIP=2" $b attack > /tmp/n2.r &
wait
for f in s1 s2 n1 n2; do echo "== $f"; cat /tmp/$f.r; done
cd ~/stp
echo "cuadros con imagen igual (s1 vs s2):"; join hash-s1.txt hash-s2.txt | awk '$2==$3{same++} $2!=$3{diff++; if ($1%2==1) odd++; else even++} END {print "iguales", same, "distintos", diff, "(impares", odd+0, "pares", even+0, ")"}'
