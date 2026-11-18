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

    const auto partial=port::MatchPreloadedNarrativeRow(record,160,{{72,U'A'},{88,U'B'}});
    assert(partial && partial->x==72 && partial->text==U"A B");
    assert(partial->text.data()==record.lines[0].text.data()+1);
    assert(port::MatchPreloadedNarrativeRow(record,160,{{72,U'A'}})->text==U"A");
    assert(port::MatchPreloadedNarrativeRow(record,160,{{64,U' '},{72,U'A'}})->text==U" A");
    assert(!port::MatchPreloadedNarrativeRow(record,160,{{88,U'B'}})); // missing A
    assert(!port::MatchPreloadedNarrativeRow(record,160,{{72,U'A'},{96,U'C'}})); // missing B
    assert(!port::MatchPreloadedNarrativeRow(record,160,{{72,U'A'},{88,U'D'}})); // wrong record or glyph
    assert(!port::MatchPreloadedNarrativeRow(record,160,{{73,U'A'}}));
    assert(!port::MatchPreloadedNarrativeRow(record,160,{{312,U'A'}}));
    assert(!port::MatchPreloadedNarrativeRow(record,159,{{72,U'A'}}));
    assert(!port::MatchPreloadedNarrativeRow(record,197,{{64,U'E'}}));
    assert(!port::MatchPreloadedNarrativeRow(record,160,{}));
    const auto fourth=port::MatchPreloadedNarrativeRow(record,196,{{64,U'E'},{72,U'n'}});
    assert(fourth && fourth->text==U"En");
    assert(!port::PreloadedNarrativeColumn(56,31)); // Ink clip is not the command origin.
    auto padded=record;
    padded.lineCount=1;
    padded.lines[0].text=std::u32string(30,U'A')+U' ';
    std::map<int,char32_t> paddedCells;
    for(int col=0;col<30;++col)paddedCells[64+col*8]=U'A';
    paddedCells[304]=U' ';
    const auto fullWidth=port::MatchPreloadedNarrativeRow(padded,160,paddedCells);
    assert(fullWidth && fullWidth->text.size()==31 && fullWidth->text.back()==U' ');
    record.simple=false;
    assert(!port::MatchPreloadedNarrativeRow(record,196,{{64,U'E'}}));
    record.simple=true;
    assert(!port::MatchPreloadedNarrativeRow(record,196,{{64,U'E'},{80,U'd'}})); // missing n on row four

    std::vector<uint8_t> atlas(32768);
    const size_t ellipse=(0x85-1)*128;
    atlas[ellipse]=0x12;
    atlas[ellipse+127]=0x34;
    const auto tile=std::span(atlas).subspan(ellipse,128);
    assert(port::ExpectedPreloadedNarrativeGlyph(record,64,172,atlas,tile)==U'\u2026');
    assert(port::ExpectedPreloadedNarrativeGlyph(record,65,172,atlas,tile)==0);
    assert(port::ExpectedPreloadedNarrativeGlyph(record,72,172,atlas,tile)==0);
    assert(port::ExpectedPreloadedNarrativeGlyph(record,64,184,atlas,tile)==0);
    assert(port::ExpectedPreloadedNarrativeGlyph(record,64,172,atlas,tile.first(127))==0);
    assert(port::ExpectedPreloadedNarrativeGlyph(record,64,172,std::span(atlas).first(32767),tile)==0);
    auto wrong=std::vector<uint8_t>(tile.begin(),tile.end());
    wrong.back()^=1;
    assert(port::ExpectedPreloadedNarrativeGlyph(record,64,172,atlas,wrong)==0);
    record.lines[1].rawOffset=static_cast<uint32_t>(record.raw.size());
    assert(port::ExpectedPreloadedNarrativeGlyph(record,64,172,atlas,tile)==0);
}
