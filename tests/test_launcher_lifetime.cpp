// Deterministic Windows lifetime regression, using only this synthetic child.
#include "game_process.h"
#include <SDL3/SDL.h>
#include <windows.h>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <new>
#include <thread>
#include <cstdio>

int main(int argc,char** argv) {
    SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX);
    if (argc==3 && std::string(argv[1])=="child") {
        std::this_thread::sleep_for(std::chrono::milliseconds(150));
        std::ofstream(argv[2]) << "finished";
        return 7;
    }
    if (argc!=2) return 2;
    SDL_Init(SDL_INIT_EVENTS);
    const auto marker=std::filesystem::path(argv[1])/"child-finished.txt";
    void* page=VirtualAlloc(nullptr,4096,MEM_COMMIT|MEM_RESERVE,PAGE_READWRITE);
    if (!page || sizeof(GameProcess)>4096) return 3;
    auto* process=new(page) GameProcess;
    std::string error;
    if (!process->start(std::filesystem::absolute(argv[0]),{"child",marker.string()},argv[1],error)) {
        std::fprintf(stderr,"%s\n",error.c_str());return 4;
    }
    process->~GameProcess();
    DWORD old=0;
    if (!VirtualProtect(page,4096,PAGE_NOACCESS,&old)) return 6;
    // The child's waiter must no longer access the destroyed GameProcess.
    for (int i=0;i<100 && !std::filesystem::exists(marker);i++) SDL_Delay(20);
    SDL_Delay(2000);
    const bool finished=std::filesystem::exists(marker);
    VirtualFree(page,0,MEM_RELEASE);
    SDL_Quit();
    if (!finished) return 5;
    std::puts("Launcher may close while its child finishes without accessing freed state");
    return 0;
}
