# usage: qemu_wsl_run.sh tag frames "ENV=1 ENV2=2" [binary=sakura] [scenario=attack]
# (no profiler; prints wall/user time, the state hash and the frame profile; runs in ~/stp of WSL)
cd ~/stp; tag=$1; n=$2; extra=$3; bin=${4:-sakura}; scen=${5:-attack}
S=/mnt/d/01Claude/Dynabrothers1+2/local/goodluckos/sysroot
read -r W < warm-pages.txt
export LD_LIBRARY_PATH=/root/stp SATRECOMP_LAZY_BLOCKS=1 SATRECOMP_WARM_BLOCK_PAGES=$W SATRECOMP_FRAME_PROFILE=1 SDL_AUDIO_DRIVER=dummy
case $bin in /*) ;; *) bin=./$bin ;; esac   # (a path: run it where it is, without a copy in WSL's own disk)
/usr/bin/time -f "tiempo %e s user %U s rss %M KB" env $extra qemu-arm -cpu cortex-a7 -L $S $bin --headless --unthrottled --stats --frames $n --disc disc/game.cue --backup /tmp/b-$tag.bin \
  --state-load 0:$scen.state --movie $scen.movie --hash-log /root/stp/hash-$tag.txt > out-$tag.txt 2> err-$tag.txt
echo "rc=$?"; sha256sum hash-$tag.txt | cut -c1-16; tail -n1 err-$tag.txt; grep "lean composition\|video thread" err-$tag.txt
awk '/^opti36s-parts/ && $2>=20 {t+=$3;c+=$4;v+=$5;s+=$6;k++} END {printf "media cuadros 20+: total %.1f sh2 %.1f video %.1f sonido %.1f\n",t/k,c/k,v/k,s/k}' err-$tag.txt
