# usage: qemu_ab.sh frames binA binB [extra env]   attack and map, both binaries, all in parallel; threads on
R=/mnt/d/01Claude/Sakurawars/tools/ga36/qemu_wsl_run.sh
n=$1; a=$2; b=$3
E="SATRECOMP_VIDEO_THREAD=1 SATRECOMP_SOUND_THREAD=1 SATRECOMP_VIDEO_THREAD_STATS=1 $4"
for s in attack map; do
  for x in $a $b; do bash $R $s-$x $n "$E" $x $s > /tmp/ab-$s-$x.r & done
done
wait
for s in attack map; do for x in $a $b; do echo "== $s $x"; cat /tmp/ab-$s-$x.r; done; done
