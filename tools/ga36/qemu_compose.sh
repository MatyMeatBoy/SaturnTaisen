# usage: qemu_compose.sh frames bin   attack and map: compose thread off and on (threads on); hashes must match
R=/mnt/d/01Claude/Sakurawars/tools/ga36/qemu_wsl_run.sh
n=$1; b=$2
E="SATRECOMP_VIDEO_THREAD=1 SATRECOMP_SOUND_THREAD=1 SATRECOMP_VIDEO_THREAD_STATS=1"
for s in attack map; do
  bash $R c0-$s $n "$E" $b $s > /tmp/c0-$s.r &
  bash $R c1-$s $n "$E SATRECOMP_COMPOSE_THREAD=1" $b $s > /tmp/c1-$s.r &
done
wait
for s in attack map; do for c in c0 c1; do echo "== $c $s"; cat /tmp/$c-$s.r; grep "compose thread" ~/stp/err-$c-$s.txt; done; done
