cmake_minimum_required(VERSION 3.28)
project(sakura_machine_tests LANGUAGES CXX)
find_package(ZLIB REQUIRED)
set(CMAKE_CXX_STANDARD 20)
get_filename_component(DEP "${CMAKE_CURRENT_SOURCE_DIR}/../../local/deps/satrecomp" ABSOLUTE)
set(CORE
    machine/sh2.cpp machine/machine.cpp machine/vdp.cpp machine/cd.cpp machine/state.cpp
    sound/chip.cpp sound/m68k.cpp sound/state.cpp
    video/renderer.cpp video/regs.cpp video/layers.cpp video/vdp1.cpp video/raster.cpp
    runtime/recomp.cpp runtime/hle_bios.cpp runtime/backup.cpp runtime/game.cpp
    runtime/shared_lifts.cpp runtime/music.cpp runtime/no_game.cpp
    recomp-common/settings.cpp)
list(TRANSFORM CORE PREPEND "${DEP}/")
add_executable(machine-tests machine_tests.cpp test_blocks.cpp ${CORE})
target_link_libraries(machine-tests PRIVATE ZLIB::ZLIB)
target_compile_definitions(machine-tests PRIVATE SATRECOMP_OWN_MACHINE)
target_include_directories(machine-tests PRIVATE "${DEP}/runtime" "${DEP}/machine")
