#include "narrative_text.h"
#include "integer_viewport.h"
#include "glyph_text.h"
#include <fstream>
#include <iterator>
#include <vector>
#include <cassert>
#include <array>
#include <cmath>
int main(int argc,char** argv) {
    if(argc==2) {
        std::ifstream file(argv[1],std::ios::binary);
        std::vector<uint8_t> atlas((std::istreambuf_iterator<char>(file)),{});
        assert(port::KnownEnglishAtlas(atlas));
        unsigned wide=0;
        for(unsigned code=32;code<=255;code++)if(const auto unicode=port::GlyphCodepoint(code)) {
            int right=-1;
            for(int y=0;y<16;y++)for(int x=0;x<16;x++) {
                const auto packed=atlas[(code-1)*128+y*8+x/2];
                if((x&1?packed&15:packed>>4)!=0)right=std::max(right,x);
            }
            assert(right<=8);
            const bool registered=std::find(port::kKnownNinePixelGlyphs.begin(),port::kKnownNinePixelGlyphs.end(),unicode)!=port::kKnownNinePixelGlyphs.end();
            assert(registered==(right==8));wide+=registered;
        }
        assert(wide==44);
    }
    std::array<uint8_t,128> tile{};
    for(int y=0;y<12;y++)for(int x=0;x<4;x++)tile[y*8+x]=0x11;
    // A 16-pixel texture may have only 8 ink pixels. The last letter still fits.
    assert(port::NarrativeInkFits(296,196,tile));
    assert(!port::NarrativeInkFits(297,196,tile));
    assert(!port::NarrativeInkFits(296,201,tile));
    assert(!port::NarrativeInkFits(55,160,tile));
    assert(!port::NarrativeInkFits(56,159,tile));
    assert(!port::NarrativeInkFits(56,160,std::span<const uint8_t>(tile.data(),4)));
    auto edge=tile;edge[4*8+4]=0x10;
    assert(!port::NarrativeInkFits(296,172,edge));
    assert(port::NarrativeRecognizedInkFits(296,172,edge,U'w'));
    assert(port::NarrativeRecognizedInkFits(296,184,edge,U'\u2026'));
    assert(!port::NarrativeRecognizedInkFits(296,172,edge,U'm'));
    assert(port::NarrativeRecognizedInkFits(296,172,edge,U'M'));
    assert(port::NarrativeRecognizedInkFits(296,172,edge,U'\u0152'));
    assert(!port::NarrativeRecognizedInkFits(296,172,edge,U'\u6f22'));
    assert(!port::NarrativeRecognizedInkFits(297,172,edge,U'w'));
    edge[4*8+4]=0x11; // a second outboard column has no witnessed exception
    assert(!port::NarrativeRecognizedInkFits(296,172,edge,U'w'));
    // Descenders on the fourth row belong inside the box, not to a native fallback.
    std::array<uint8_t,128> descender{};
    for(int y=2;y<15;y++)for(int x=0;x<4;x++)descender[y*8+x]=0x11;
    assert(port::NarrativeInkFits(56,196,descender));
    // Use a single affine scale for the entire font. A narrow i must not be
    // stretched to a native bitmap's different width or height.
    const auto natural=port::NaturalTextPlacement(7.5f,1,3,9,0,2,11,3);
    assert(natural.scale>0);
    const float wide=7*natural.scale,narrow=natural.scale;
    assert(std::abs(wide/narrow-7)<0.0001f);
    assert(std::abs((12*natural.scale+natural.offsetY)-(3*natural.scale+natural.offsetY)-9*natural.scale)<0.0001f);
    assert(std::abs(1*natural.scale+natural.offsetX)<0.0001f);
    assert(std::abs(3*natural.scale+natural.offsetY-6)<0.0001f);
    assert(9*natural.scale<=11*3);
    // Letters keep a visible gap inside the 8-pixel cell instead of filling it.
    assert(7.5f*natural.scale<8*3*0.95f);
    // Reserve three native pixels above the inner bottom frame, even for
    // descenders on the fourth line. Offset is fixed before any text reveals.
    for(int scale:{1,3,6,8}) {
        const float bottom=14.5f*scale;
        const float row=port::NarrativeRowTop(196,scale);
        assert(row+bottom<=208*scale+0.001f);   // one native pixel lower since 2026-11-19 (owner): still above the inner bottom frame
        assert(port::NarrativeRowTop(172,scale)-port::NarrativeRowTop(160,scale)==11*scale);
    }
    for(const auto [w,h]:std::array<std::pair<int,int>,5>{{{640,480},{1280,720},{1920,1080},{3840,2160},{3440,1440}}}) {
        const auto fit=port::FitInteger(w,h,320,224);
        const auto clip=port::NarrativeClip(fit.x,fit.y,fit.scale,0,0);
        assert(clip[0]>=0 && clip[1]>=0 && clip[2]<=w && clip[3]<=h);
        assert(clip[2]-clip[0]==248*fit.scale && clip[3]-clip[1]==48*fit.scale);
        const auto cropped=port::NarrativeClip(fit.x,fit.y,fit.scale,8,12);
        assert(cropped[0]==clip[0]-8*fit.scale && cropped[1]==clip[1]-12*fit.scale);
    }
}
