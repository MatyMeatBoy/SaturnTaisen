#!/bin/sh
set -eu

here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$here"
mkdir -p user
diagnostic=
if [ "${0##*/}" = diagnostico.sh ]; then
    diagnostic=$(mktemp -d "$here/user/diagnostico.XXXXXX")
    exec >"$diagnostic/run.log" 2>&1
else
    exec >user/run.log 2>&1
fi

language=${SATURNTAISEN_LANGUAGE:-}
case ${1:-} in es|en) language=$1; shift ;; esac
if [ -n "$diagnostic" ]; then
    case ${1:-wide} in
        wide) export SATRECOMP_GA36_WIDE=1 ;;
        original) unset SATRECOMP_GA36_WIDE ;;
        *) exit 2 ;;
    esac
    [ "$#" -eq 0 ] || shift
fi
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
# The four cores of the A33 (RC11, ga36-*-thread patches): the renderer, the sound side and the final picture
# composition on cores of their own; each can be turned off by setting it to 0. Composing 1 frame of N
# (SATRECOMP_FRAME_SKIP=N) stays off unless asked for: the game itself always runs every frame.
export SATRECOMP_VIDEO_THREAD="${SATRECOMP_VIDEO_THREAD:-1}"
export SATRECOMP_SOUND_THREAD="${SATRECOMP_SOUND_THREAD:-1}"
export SATRECOMP_COMPOSE_THREAD="${SATRECOMP_COMPOSE_THREAD:-1}"
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

case $media in game/es) profile=user/es ;; game/en) profile=user/en ;; *) profile=user ;; esac
mkdir -p "$profile"
program=./sakura
if [ -n "$diagnostic" ]; then
    frames=${SATURNTAISEN_DIAG_FRAMES:-7200}
    case $frames in ''|*[!0-9]*|0*) exit 2 ;; esac
    [ "${#frames}" -le 5 ] && [ "$frames" -le 36000 ] || exit 2
    for file in settings.ini backup.bin gamecontrollerdb.txt; do
        if [ -r "$profile/$file" ]; then cp "$profile/$file" "$diagnostic/$file"; fi
    done
    profile=$diagnostic
    program=./diag/sakura
    export SATRECOMP_GA36_DIAG_CSV="$diagnostic/frames.csv"
    export SATRECOMP_FRAME_PROFILE=1 SATRECOMP_WINDOW_LOG=1
    printf 'mode=%s frames=%s video=%s audio=%s\n' "${SATRECOMP_GA36_WIDE:+wide}" "$frames" "$SDL_VIDEO_DRIVER" "$SDL_AUDIO_DRIVER"
    uname -smr
    for path in /sys/class/graphics/fb0/virtual_size /sys/class/graphics/fb0/bits_per_pixel; do
        if [ -r "$path" ]; then printf '%s ' "$path"; cat "$path"; fi
    done
fi
set -- --disc "$disc" "$display" --scale 2 --settings "$profile/settings.ini" --backup "$profile/backup.bin"
if [ -r "$other" ]; then
    set -- "$@" --extra-disc "$other"
fi
if [ -n "$diagnostic" ]; then
    set -- "$@" --frames "$frames" --stats
    "$program" "$@" &
    game_pid=$!
    trap 'kill -TERM "$game_pid" 2>/dev/null || :' HUP INT TERM
    {
        while [ -r "/proc/$game_pid/status" ]; do
            printf '%s ' "$(cut -d ' ' -f 1 /proc/uptime)"
            awk '/^(VmRSS|VmHWM|Threads):/ {printf "%s%s ", $1, $2}' "/proc/$game_pid/status" 2>/dev/null || :
            for path in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_cur_freq /sys/class/thermal/thermal_zone0/temp; do
                if [ -r "$path" ] && read -r value <"$path"; then printf '%s=%s ' "$path" "$value"; fi
            done
            printf '\n'
            sleep 2
        done
    } >"$diagnostic/system.log" &
    monitor_pid=$!
    result=0
    wait "$game_pid" || result=$?
    kill "$monitor_pid" 2>/dev/null || :
    wait "$monitor_pid" 2>/dev/null || :
    printf 'exit_code=%s\n' "$result"
    exit "$result"
fi
exec "$program" "$@"
