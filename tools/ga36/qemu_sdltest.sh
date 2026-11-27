# qemu_sdltest.sh: the SDL picture path test with the old and the new SDL build (identical hashes expected)
S=/mnt/d/01Claude/Dynabrothers1+2/local/goodluckos/sysroot
T=/mnt/d/01Claude/Sakurawars/local/build/ga36-a33/sdltest
for v in old new old new; do
  printf '%s: ' $v
  LD_LIBRARY_PATH=$T/$v SDL_VIDEO_DRIVER=dummy qemu-arm -cpu cortex-a7 -L $S $T/sdlpresent_test
done
