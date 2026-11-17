// Component benchmark of the exact backdrop loaders used by the Saturn frontend.
#include "backdrop.h"
#include "pc_backdrop.h"
#include "background_workers.h"
#include <chrono>
#include <iostream>
#include <iterator>
int main(int argc,char** argv) {
    if(argc!=4 && argc!=5)return 2;
    const std::filesystem::path root=argv[1],cache=argv[2],pcRoot=argv[3];
    if(argc==5) {
        const unsigned count=std::stoul(argv[4]);if(count<1 || count>8)return 2;
        std::vector<port::BackgroundWorkers::Job> jobs;std::array<std::string,38> rows;
        std::atomic<unsigned> failures=0;size_t index=0;
        for(int kind=0;kind<2;kind++)for(int family=0;family<10;family++)for(int variant=0;variant<2;variant++) {
            if(family==9 && variant==1)continue;
            const std::string id="KABE"+std::to_string(family)+std::to_string(variant);
            const size_t row=index++;
            jobs.push_back([&,kind,id,row] {
                const auto start=std::chrono::steady_clock::now();SDL_Surface* prepared=nullptr;
                if(kind) {
                    const auto* info=port::PcBackdropFor(id);if(!info)return false;
                    prepared=port::PreparePcBackdrop(root/"assets/generated/pc-backgrounds"/(std::string(info->id)+"-v1.png"),pcRoot,id,cache,true);
                } else {
                    std::ifstream file(root/"local/work/background-bench/palettes"/(id+".bin"),std::ios::binary);
                    const std::vector<uint8_t> palette((std::istreambuf_iterator<char>(file)),{});
                    prepared=port::PrepareBackdrop(root/"assets/generated/backgrounds"/(id+".png"),palette,cache,true);
                }
                const auto us=std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-start).count();
                rows[row]=std::string(kind?"pc_hd":"saturn")+","+id+","+std::to_string(us)+"\n";
                const bool ok=prepared!=nullptr;SDL_DestroySurface(prepared);if(!ok)++failures;return ok;
            });
        }
        port::BackgroundWorkers workers;workers.Start(std::move(jobs),count);workers.Wait();
        for(const auto& row:rows)std::cout<<row;
        return failures==0 && workers.Completed()==38 && workers.Failed()==0?0:5;
    }
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
