#include "map_crossfade.h"
#include <cassert>
#include <vector>

int main() {
    const port::IntegerViewport native{20,4,640,448,2};
    std::vector<uint32_t> mapRows(16*224);
    for (int y=0;y<224;y++)for (int x=0;x<16;x++)
        mapRows[y*16+x]=y*0x010100+x;

    const port::MapCrossfade recipe{16,{-1,0,0}};
    const uint32_t floral=0x808080;
    // Left -1 wraps to phase 7. Right +0 starts the other edge's phase 0.
    assert(port::SampleMapCrossfade(recipe,mapRows,native,19,3,floral)==0xFF404042);
    assert(port::SampleMapCrossfade(recipe,mapRows,native,660,452,floral)==0xFFAFAF43);
    assert(!port::SampleMapCrossfade(recipe,mapRows,native,20,4,floral));
    assert(!port::SampleMapCrossfade(recipe,mapRows,native,659,451,floral));
    assert(!port::SampleMapCrossfade({},mapRows,native,19,3,floral));
    assert(!port::SampleMapCrossfade({33,{}},mapRows,native,19,3,floral));
    assert(!port::SampleMapCrossfade({16,{256,0,0}},mapRows,native,19,3,floral));
    assert(!port::SampleMapCrossfade(recipe,std::span{mapRows}.first(1),native,19,3,floral));
    assert(!port::SampleMapCrossfade(recipe,mapRows,{},19,3,floral));
    // Top/bottom bands repeat the nearest native gradient row.
    assert(port::SampleMapCrossfade(recipe,mapRows,native,20,3,floral)==0xFF40403F);
    assert(port::SampleMapCrossfade(recipe,mapRows,native,20,452,floral)==0xFFAFAF3F);
    assert(port::SampleMapCrossfade({32,{}},mapRows,native,660,4,floral)==0xFF000008);

    // Whole-row evidence is required even if a cursor obscures the native edge.
    std::vector<port::MapFadeEdge> edges(32*224);
    for(int y=0;y<224;y++)for(int x=0;x<32;x++)
        edges[y*32+x]={mapRows[y*16+(x/16)*8+x%8],recipe};
    std::vector<uint32_t> reconstructed;
    auto verified=port::VerifyMapCrossfadeEdges(edges,reconstructed);
    assert(verified && verified->mapWeight==16 && verified->postMixOffset==recipe.postMixOffset);
    for(size_t at=0;at<mapRows.size();at++)assert(reconstructed[at]==(mapRows[at]|0xFF000000));
    edges[7].mix.mapWeight=0;
    assert(!port::VerifyMapCrossfadeEdges(edges,reconstructed) && reconstructed.empty());
    edges[7].mix=recipe;
    edges[8].mix.mapWeight=15;
    assert(!port::VerifyMapCrossfadeEdges(edges,reconstructed));
    edges[8].mix=recipe;
    edges[7].mapRgb=0xA00000;
    assert(!port::VerifyMapCrossfadeEdges(edges,reconstructed));
}
