#include "pc_backdrop.h"
#include <cassert>
int main() {
    auto* source=SDL_CreateSurface(640,480,SDL_PIXELFORMAT_ABGR8888);assert(source);
    SDL_FillSurfaceRect(source,nullptr,0xFFFF0000);
    const std::vector<uint32_t> palette{0xFF0000FF};
    auto* logical=port::NormalizePcBackdrop(source,palette);assert(logical);
    assert(logical->w==864 && logical->h==486);
    assert(static_cast<uint32_t*>(logical->pixels)[0]==0xFF0000FF);
    assert(!port::NormalizePcBackdrop(source,{}));
    assert(port::PcBackdropFor("KABE00")->id=="KABE0100");
    assert(port::PcBackdropFor("KABE91")->id=="KABE1000");
    assert(!port::PcBackdropFor("KABE99"));
    assert(!port::PcBackdropFor("../../KABE00"));
    SDL_DestroySurface(logical);SDL_DestroySurface(source);
}
