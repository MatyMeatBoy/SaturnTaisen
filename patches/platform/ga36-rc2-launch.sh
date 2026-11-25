#!/bin/sh
set -eu

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$here"
mkdir -p user
exec >user/rc2-run.log 2>&1

language=${SATURNTAISEN_LANGUAGE:-}
case ${1:-} in es|en) language=$1; shift ;; esac
[ "$#" -le 1 ] || exit 2
case ${1:-1} in
    1) first=1; second=2 ;;
    2) first=2; second=1 ;;
    *) exit 2 ;;
esac
case $language in
    en|es) media="game/$language" ;;
    '')
        media=game
        for candidate in game/es game/en game; do
            if [ -r "$candidate/disc$first/game.cue" ]; then
                media=$candidate
                break
            fi
        done ;;
    *) exit 2 ;;
esac
disc="$media/disc$first/game.cue"
other="$media/disc$second/game.cue"
if [ ! -r "$disc" ]; then
    printf 'Disco preparado requerido / Prepared disc required: %s\n' "$disc"
    exit 5
fi

if [ -z "${SDL_GAMECONTROLLERCONFIG:-}" ] && [ -r /etc/profile.d/sdl_controller.sh ]; then
    . /etc/profile.d/sdl_controller.sh
fi
if [ -z "${SATURNTAISEN_FBDEV+x}" ] && [ -z "${SDL_VIDEO_DRIVER:-${SDL_VIDEODRIVER:-}}" ] &&
   [ -r /dev/fb0 ] && [ -w /dev/fb0 ]; then
    SATURNTAISEN_FBDEV=/dev/fb0
fi
export SDL_VIDEO_DRIVER="${SDL_VIDEO_DRIVER:-${SDL_VIDEODRIVER:-kmsdrm}}"
export SDL_AUDIO_DRIVER="${SDL_AUDIO_DRIVER:-${SDL_AUDIODRIVER:-alsa}}"
export SDL_KMSDRM_DEVICE_INDEX="${SDL_KMSDRM_DEVICE_INDEX:-1}"
export LD_LIBRARY_PATH="$here/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export SATRECOMP_LAZY_BLOCKS=1
if [ -z "${SATRECOMP_WARM_BLOCK_PAGES:-}" ] && [ -r warm-pages.txt ]; then
    read -r SATRECOMP_WARM_BLOCK_PAGES <warm-pages.txt
    export SATRECOMP_WARM_BLOCK_PAGES
fi

display=--fullscreen
if [ -n "${SATURNTAISEN_FBDEV:-}" ]; then
    export SATURNTAISEN_FBDEV
    export SDL_VIDEO_DRIVER=dummy SDL_RENDER_DRIVER=software SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1
    display=--windowed
fi

case $media in game/es) original=user/es; profile=user/rc2/es ;; game/en) original=user/en; profile=user/rc2/en ;; *) original=user; profile=user/rc2 ;; esac
mkdir -p "$profile"
for file in settings.ini backup.bin gamecontrollerdb.txt; do
    if [ ! -e "$profile/$file" ] && [ -r "$original/$file" ]; then cp "$original/$file" "$profile/$file"; fi
done
set -- --disc "$disc" "$display" --scale 2 --settings "$profile/settings.ini" --backup "$profile/backup.bin"
if [ -r "$other" ]; then
    set -- "$@" --extra-disc "$other"
fi
exec ./rc2/sakura "$@"
