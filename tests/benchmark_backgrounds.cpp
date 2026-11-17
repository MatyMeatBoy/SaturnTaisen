// Component benchmark of the exact backdrop loaders used by the Saturn frontend.
#include "backdrop.h"
#include "pc_backdrop.h"
#include <chrono>
#include <iostream>
#include <iterator>
int main(int argc,char** argv) {
    if(argc!=4)return 2;
    const std::filesystem::path root=argv[1],cache=argv[2],pcRoot=argv[3];
    auto* surface=SDL_CreateSurface(1,1,SDL_PIXELFORMAT_ABGR8888);
    auto* renderer=surface?SDL_CreateSoftwareRenderer(surface):nullptr;
    if(!renderer)return 3;
    for(int kind=0;kind<2;kind++)for(int family=0;family<10;family++)for(int variant=0;variant<2;variant++) {
        if(family==9 && variant==1)continue; // native 90/91 are identical
        const std::string id="KABE"+std::to_string(family)+std::to_string(variant);
        const auto start=std::chrono::steady_clock::now();SDL_Texture* texture=nullptr;
        if(kind) {
            const auto* info=port::PcBackdropFor(id);if(!info)return 4;
            texture=port::LoadPcBackdrop(renderer,root/"assets/generated/pc-backgrounds"/(std::string(info->id)+"-v1.png"),pcRoot,id,cache,nullptr,true);
        } else {
            std::ifstream file(root/"local/work/background-bench/palettes"/(id+".bin"),std::ios::binary);
            const std::vector<uint8_t> palette((std::istreambuf_iterator<char>(file)),{});
            texture=port::LoadBackdrop(renderer,root/"assets/generated/backgrounds"/(id+".png"),palette,cache);
        }
        const auto us=std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-start).count();
        if(!texture){std::cerr<<"failed "<<kind<<" "<<id<<"\n";return 5;}
        std::cout<<(kind?"pc_hd":"saturn")<<","<<id<<","<<us<<"\n";
        SDL_DestroyTexture(texture);
    }
    SDL_DestroyRenderer(renderer);SDL_DestroySurface(surface);return 0;
}
