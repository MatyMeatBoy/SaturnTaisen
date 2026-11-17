#include "disc_image.h"
#include <array>
#include <cassert>
#include <fstream>
#include <filesystem>
#include <thread>
int main(int argc,char**argv) {
    const auto root=std::filesystem::path(argv[1]);
    for(int disc=0;disc<2;disc++) {
        std::ofstream out(root/(disc?"second.iso":"first.iso"),std::ios::binary);
        for(int sector=0;sector<80;sector++)for(int n=0;n<2048;n++)out.put(static_cast<char>((sector+n+disc*17)%251));
    }
    port::DiscImage image;assert(image.Open((root/"first.iso").string()));
    auto read=[&](int sector,int salt) {
        std::array<uint8_t,2048> bytes{};assert(image.ReadUserData(150+sector,bytes.data()));
        for(int n=0;n<2048;n++)assert(bytes[n]==(sector+n+salt)%251);
    };
    for(int sector=0;sector<80;sector++)read(sector,0);
    assert(image.Stats().hostReads<=3); // 80 sectors served by three bounded 64 KiB reads
    auto worker=[&](int first){for(int sector=first;sector<80;sector+=2)read(sector,0);};
    std::thread a(worker,0),b(worker,1);a.join();b.join();
    assert(image.Open((root/"second.iso").string()));
    read(0,17);read(31,17);read(32,17);read(79,17);
    auto invalid=image.Tracks()[0];invalid.file=999;
    std::array<uint8_t,2352> raw{};
    assert(!image.ReadRaw(invalid,0,raw.data()));
    assert(!image.ReadRaw(image.Tracks()[0],0xffffffff,raw.data()));
}
