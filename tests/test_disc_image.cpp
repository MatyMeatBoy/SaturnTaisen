// Tests use invented disc data, never a game dump.
#include "disc_image.h"
#include <array>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <vector>

static void le(std::ofstream& out, unsigned value, int size) {
    for (int i=0;i<size;++i) out.put(static_cast<char>(value >> (8*i)));
}
int main(int argc, char** argv) {
    if(argc != 2) return 2;
    const std::filesystem::path base(argv[1]);
    std::filesystem::create_directories(base);
    { std::ofstream out(base / "data.iso", std::ios::binary); std::vector<char> bytes(2048*2, 'D');out.write(bytes.data(),bytes.size()); }
    { std::ofstream out(base / "audio.wav", std::ios::binary);
      out.write("RIFF",4);le(out,36+2352,4);out.write("WAVEfmt ",8);le(out,16,4);le(out,1,2);le(out,2,2);le(out,44100,4);le(out,176400,4);le(out,4,2);le(out,16,2);out.write("data",4);le(out,2352,4);
      for(int i=0;i<2352;++i) out.put(static_cast<char>(i%251)); }
    { std::ofstream cue(base / "game.cue");cue << "FILE \"data.iso\" BINARY\n TRACK 01 MODE1/2048\n INDEX 01 00:00:00\n POSTGAP 00:02:00\nFILE \"audio.wav\" WAVE\n TRACK 02 AUDIO\n PREGAP 00:02:00\n INDEX 01 00:00:00\n"; }
    port::DiscImage disc;
    if(!disc.Open((base/"game.cue").string()) || disc.Tracks().size()!=2) {std::cerr<<"CUE open failed\n";return 1;}
    const auto& track=disc.Tracks()[1];
    if(track.startFAD!=452 || track.endFAD!=452 || disc.LeadOutFAD()!=453) {std::cerr<<"gap timing wrong: "<<track.startFAD<<".."<<track.endFAD<<" leadout "<<disc.LeadOutFAD()<<"\n";return 1;}
    std::array<uint8_t,2352> bytes{};
    if(!disc.ReadRaw(track,0,bytes.data())) return 1;
    for(int i=0;i<2352;++i) if(bytes[i]!=i%251) {std::cerr<<"WAV header leaked into PCM\n";return 1;}
    if(disc.ReadRaw(track,1,bytes.data())) {std::cerr<<"read past audio track\n";return 1;}
    std::array<uint8_t,2048> data{};
    if(!disc.ReadUserData(150,data.data()) || data[0]!='D' || disc.ReadUserData(152,data.data())) return 1;
    std::cout<<"WAV payload, explicit gaps, track bounds and user data passed\n";
}
