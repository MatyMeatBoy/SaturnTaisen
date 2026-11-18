// SPDX-License-Identifier: GPL-3.0-only
#include "dialogue_reveal.h"

#include <cassert>
#include <vector>

int main() {
    port::PreloadedDialogueRecord record;
    record.simple=true;
    record.lineCount=4;
    record.raw=" A BCD\r\x85\rLeft\rEnd";
    record.lines={{{0,U" A BCD"},{7,U"\u2026"},{9,U"Left"},{14,U"End"}}};

    const auto partial=port::MatchPreloadedNarrativeRow(record,160,{{64,U'A'},{80,U'B'}});
    assert(partial && partial->x==64 && partial->text==U"A B");
    assert(partial->text.data()==record.lines[0].text.data()+1);
    assert(port::MatchPreloadedNarrativeRow(record,160,{{64,U'A'}})->text==U"A");
    assert(port::MatchPreloadedNarrativeRow(record,160,{{56,U' '},{64,U'A'}})->text==U" A");
    assert(!port::MatchPreloadedNarrativeRow(record,160,{{80,U'B'}})); // missing A
    assert(!port::MatchPreloadedNarrativeRow(record,160,{{64,U'A'},{88,U'C'}})); // missing B
    assert(!port::MatchPreloadedNarrativeRow(record,160,{{64,U'A'},{80,U'D'}})); // wrong record or glyph
    assert(!port::MatchPreloadedNarrativeRow(record,160,{{65,U'A'}}));
    assert(!port::MatchPreloadedNarrativeRow(record,160,{{304,U'A'}}));
    assert(!port::MatchPreloadedNarrativeRow(record,159,{{64,U'A'}}));
    assert(!port::MatchPreloadedNarrativeRow(record,197,{{56,U'E'}}));
    assert(!port::MatchPreloadedNarrativeRow(record,160,{}));
    const auto fourth=port::MatchPreloadedNarrativeRow(record,196,{{56,U'E'},{64,U'n'}});
    assert(fourth && fourth->text==U"En");
    record.simple=false;
    assert(!port::MatchPreloadedNarrativeRow(record,196,{{56,U'E'}}));
    record.simple=true;
    assert(!port::MatchPreloadedNarrativeRow(record,196,{{56,U'E'},{72,U'd'}})); // missing n on row four

    std::vector<uint8_t> atlas(32768);
    const size_t ellipse=(0x85-1)*128;
    atlas[ellipse]=0x12;
    atlas[ellipse+127]=0x34;
    const auto tile=std::span(atlas).subspan(ellipse,128);
    assert(port::ExpectedPreloadedNarrativeGlyph(record,56,172,atlas,tile)==U'\u2026');
    assert(port::ExpectedPreloadedNarrativeGlyph(record,57,172,atlas,tile)==0);
    assert(port::ExpectedPreloadedNarrativeGlyph(record,64,172,atlas,tile)==0);
    assert(port::ExpectedPreloadedNarrativeGlyph(record,56,184,atlas,tile)==0);
    assert(port::ExpectedPreloadedNarrativeGlyph(record,56,172,atlas,tile.first(127))==0);
    assert(port::ExpectedPreloadedNarrativeGlyph(record,56,172,std::span(atlas).first(32767),tile)==0);
    auto wrong=std::vector<uint8_t>(tile.begin(),tile.end());
    wrong.back()^=1;
    assert(port::ExpectedPreloadedNarrativeGlyph(record,56,172,atlas,wrong)==0);
    record.lines[1].rawOffset=static_cast<uint32_t>(record.raw.size());
    assert(port::ExpectedPreloadedNarrativeGlyph(record,56,172,atlas,tile)==0);
}
