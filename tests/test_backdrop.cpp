#include "backdrop.h"
#include <cassert>
#include <vector>
#include <thread>
#include <atomic>
int main(int argc,char** argv) {
    const std::array<int16_t,3> fade{-255,30,-10};
    assert(port::OffsetBackdropPixel(0xFF1020F0,fade)==0xFF063E00);
    assert(port::OffsetBackdropPixel(0xFFFEFEFE,{20,20,20})==0xFFFFFFFF);
    std::vector<uint32_t> reference(320*224),visible;
    for(size_t i=0;i<reference.size();i++)reference[i]=0xFF000000u|uint32_t(i%251)*0x010101u;
    visible=reference;
    assert(port::MatchesAnchoredBackdrop(visible,reference,{}));
    for(size_t i=0;i<visible.size()/10;i++)visible[i]^=0x0000FF00u;
    assert(port::MatchesAnchoredBackdrop(visible,reference,{}));
    visible.assign(reference.size(),0xFF000000u);
    assert(!port::MatchesAnchoredBackdrop(visible,reference,{}));
    assert(!port::MatchesAnchoredBackdrop({},reference,{}));
    visible=reference;for(auto& pixel:visible)pixel=port::OffsetBackdropPixel(pixel,{-8,-16,-24});
    assert(port::MatchesAnchoredBackdrop(visible,reference,{-8,-16,-24}));
    std::vector<uint8_t> palette(512);
    for(int i=0;i<256;i++){palette[i*2]=0x80;palette[i*2+1]=0x1F;}
    auto* source=SDL_CreateSurface(1920,1080,SDL_PIXELFORMAT_ABGR8888);assert(source);
    SDL_FillSurfaceRect(source,nullptr,0xFFFF0000); // blue master; only authorized palette entry is red
    auto* logical=port::NormalizeBackdrop(source,palette);assert(logical);
    assert(logical->w==416 && logical->h==234);
    auto* anchored=port::NormalizeBackdrop(source,palette,800,450);assert(anchored);
    assert(anchored->w==800 && anchored->h==450);
    std::vector<uint32_t> native(320*224,0xFF0000F8);
    SDL_FillSurfaceRect(anchored,nullptr,0xFFFF0000);
    assert(port::AnchorBackdropSurface(anchored,native,palette));
    const auto at=[&](int x,int y){return reinterpret_cast<uint32_t*>(static_cast<uint8_t*>(anchored->pixels)+y*anchored->pitch)[x];};
    assert(at(240,113)==native[0] && at(239,113)==native[0]);
    assert(at(230,113)==0xFFFF0000); // preserve generated art away from the seam
    SDL_DestroySurface(anchored);
    for(int y=0;y<234;y++)for(int x=0;x<416;x++)
        assert(reinterpret_cast<uint32_t*>(static_cast<uint8_t*>(logical->pixels)+y*logical->pitch)[x]==0xFF0000F8);
    assert(!port::NormalizeBackdrop(source,std::span<const uint8_t>(palette.data(),12)));
    assert(argc==2);
    const auto file=std::filesystem::path(argv[1])/"master.png";
    assert(SDL_SavePNG(source,file.string().c_str()));
    SDL_Surface* prepared=nullptr;
    std::thread worker([&]{prepared=port::PrepareBackdrop(file,palette,std::filesystem::path(argv[1])/"prepared",true);});
    worker.join();assert(prepared && prepared->w==416 && prepared->h==234);
    assert(static_cast<uint32_t*>(prepared->pixels)[0]==0xFF0000F8);
    SDL_DestroySurface(prepared);
    // Foreground demand and speculative preparation may target the same cache.
    std::atomic<unsigned> ready=0;std::vector<std::thread> concurrent;
    for(unsigned i=0;i<8;i++)concurrent.emplace_back([&] {
        auto* image=port::PrepareBackdrop(file,palette,std::filesystem::path(argv[1])/"shared",true);
        if(image && static_cast<uint32_t*>(image->pixels)[0]==0xFF0000F8)++ready;
        SDL_DestroySurface(image);
    });
    for(auto& thread:concurrent)thread.join();assert(ready==8);
    unsigned cacheCount=0;
    for(const auto& item:std::filesystem::directory_iterator(std::filesystem::path(argv[1])/"shared")) {
        assert(item.path().extension()==".stfb");++cacheCount;
    }
    assert(cacheCount==1);
    assert(!port::PrepareBackdrop(file,palette,{},true));
    assert(!port::PrepareBackdrop(file,std::span<const uint8_t>(palette.data(),12),{},false));
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
