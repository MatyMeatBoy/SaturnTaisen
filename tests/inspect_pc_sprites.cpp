// Read-only owner-resource audit of the production SPRED decoder. No pixel export.
#include "pc_spr.h"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <algorithm>
int main(int argc,char** argv) {
    if(argc!=2)return 2;
    std::vector<std::filesystem::path> paths;
    for(const auto& entry:std::filesystem::directory_iterator(argv[1]))
        if(entry.is_regular_file() && entry.path().extension()==".SPR")paths.push_back(entry.path());
    std::sort(paths.begin(),paths.end());unsigned failed=0;
    for(const auto& path:paths) {
        std::ifstream input(path,std::ios::binary|std::ios::ate);const auto length=input.tellg();
        if(!input || length<=0 || length>64*1024*1024)return 3;
        std::vector<uint8_t> bytes(static_cast<size_t>(length));input.seekg(0);
        if(!input.read(reinterpret_cast<char*>(bytes.data()),bytes.size()))return 3;
        std::vector<port::PcSprite> images;std::string error;
        if(!port::DecodePcSprites(bytes,images,error)) {std::cerr<<path.filename()<<": "<<error<<'\n';++failed;continue;}
        uint64_t pixels=0,green=0,transparent=0;
        for(const auto& image:images)for(const auto p:image.pixels) {
            pixels++;if((p&0xFFFFFF)==0x00FF00)green++;if(!(p>>24))transparent++;
        }
        std::cout<<path.filename().string()<<','<<images.size()<<','<<pixels<<','<<green<<','<<transparent<<'\n';
    }
    return failed?1:0;
}
