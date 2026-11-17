#include "backdrop.h"
#include <cassert>
#include <vector>
int main(int argc,char** argv) {
    const std::array<int16_t,3> fade{-255,30,-10};
    assert(port::OffsetBackdropPixel(0xFF1020F0,fade)==0xFF063E00);
    assert(port::OffsetBackdropPixel(0xFFFEFEFE,{20,20,20})==0xFFFFFFFF);
    std::vector<uint8_t> palette(512);
    for(int i=0;i<256;i++){palette[i*2]=0x80;palette[i*2+1]=0x1F;}
    auto* source=SDL_CreateSurface(1920,1080,SDL_PIXELFORMAT_ABGR8888);assert(source);
    SDL_FillSurfaceRect(source,nullptr,0xFFFF0000); // blue master; only authorized palette entry is red
    auto* logical=port::NormalizeBackdrop(source,palette);assert(logical);
    assert(logical->w==416 && logical->h==234);
    for(int y=0;y<234;y++)for(int x=0;x<416;x++)
        assert(reinterpret_cast<uint32_t*>(static_cast<uint8_t*>(logical->pixels)+y*logical->pitch)[x]==0xFF0000F8);
    assert(!port::NormalizeBackdrop(source,std::span<const uint8_t>(palette.data(),12)));
    assert(argc==2);
    const auto file=std::filesystem::path(argv[1])/"master.png";
    assert(SDL_SavePNG(source,file.string().c_str()));
    auto* output=SDL_CreateSurface(416,234,SDL_PIXELFORMAT_ABGR8888);assert(output);
    auto* renderer=SDL_CreateSoftwareRenderer(output);assert(renderer);
    std::vector<uint32_t> base;
    auto* texture=port::LoadBackdrop(renderer,file,palette,std::filesystem::path(argv[1])/"cache",&base);
    assert(texture && base.size()==416*234);
    assert(SDL_RenderTexture(renderer,texture,nullptr,nullptr));
    auto* shown=SDL_RenderReadPixels(renderer,nullptr);assert(shown);
    auto* rgba=SDL_ConvertSurface(shown,SDL_PIXELFORMAT_ABGR8888);assert(rgba);
    assert(static_cast<uint32_t*>(rgba->pixels)[0]==0xFF0000F8);
    SDL_DestroySurface(rgba);SDL_DestroySurface(shown);
    for(auto& pixel:base)pixel=port::OffsetBackdropPixel(pixel,fade);
    assert(SDL_UpdateTexture(texture,nullptr,base.data(),416*4));
    assert(SDL_RenderTexture(renderer,texture,nullptr,nullptr));
    shown=SDL_RenderReadPixels(renderer,nullptr);assert(shown);
    rgba=SDL_ConvertSurface(shown,SDL_PIXELFORMAT_ABGR8888);assert(rgba);
    assert(static_cast<uint32_t*>(rgba->pixels)[0]==0xFF001E00);
    SDL_DestroySurface(rgba);SDL_DestroySurface(shown);SDL_DestroyTexture(texture);
    SDL_DestroyRenderer(renderer);SDL_DestroySurface(output);
    SDL_DestroySurface(logical);SDL_DestroySurface(source);
}
