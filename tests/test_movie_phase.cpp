#include "movie_phase.h"
#include <array>
#include <cassert>
#include <vector>
struct Command {std::array<uint16_t,16> words{};};
struct Sprite {Command command;std::vector<uint8_t> pixels;int x=0,y=0;};
int main(){
 std::vector<uint8_t> low(1<<20),high(1<<20),script(15404,0x42);
 std::copy(script.begin(),script.end(),low.begin()+0x4000);
 auto cursor=[&](uint32_t value){for(int i=0;i<4;i++)high[0x685B4+i]=uint8_t(value>>(24-i*8));};
 for(uint32_t pc:{0x204006u,0x204462u,0x204ED8u,0x204EDEu,0x204EE4u,0x204EE6u}){cursor(pc);assert(port::CaptureFirstMoviePhase(low,high,script));}
 for(uint32_t pc:{0x204000u,0x20582Cu,0x205990u,0x205FA8u}){cursor(pc);assert(!port::CaptureFirstMoviePhase(low,high,script));}
 cursor(0x204006);low[0x4001]^=1;assert(!port::CaptureFirstMoviePhase(low,high,script));low[0x4001]^=1;
 assert(!port::CaptureFirstMoviePhase(low,high,std::span<const uint8_t>{}));
 assert(!port::CaptureFirstMoviePhase(std::span<const uint8_t>{},high,script));
 std::vector<uint8_t> source(320*224,5);
 assert(!port::FirstMovieBlankFrame(false,source,true));
 assert(port::FirstMovieBlankFrame(true,source,true));
 for(uint8_t layer:{uint8_t(1),uint8_t(2),uint8_t(4),uint8_t(6)}){source[320*8+16]=layer;assert(!port::FirstMovieBlankFrame(true,source,true));}
 source[320*8+16]=5;source[320*152+8]=0;assert(port::FirstMovieBlankFrame(true,source,true));
 source[320*151+8]=0;assert(!port::FirstMovieBlankFrame(true,source,true));source[320*151+8]=5;
 assert(!port::FirstMovieBlankFrame(true,source,false));
 assert(!port::KnownFirstMovieScript(script));
 std::vector<Sprite> sprites{{{{0,0,0xA0,0xC500,0,0x2640}},std::vector<uint8_t>(304*64),8,152}};
 assert(!port::OnlyFirstMovieOrnaments(std::span<const Sprite>{sprites})); // corrupt footer payload
 sprites[0].command.words[0]=4;assert(!port::OnlyFirstMovieOrnaments(std::span<const Sprite>{sprites}));
 assert(port::OnlyFirstMovieOrnaments(std::span<const Sprite>{}));
}
