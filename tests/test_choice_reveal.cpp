// SPDX-License-Identifier: GPL-3.0-only
#include "choice_reveal.h"

#include <cassert>
#include <limits>

int main() {
    using port::ExpectedPreloadedChoiceGlyph;
    using port::PreloadedChoiceLine;
    port::PreloadedDialogueRecord record;
    record.simple = true;
    record.lineCount = 2;
    record.raw = "A \r\x85";
    record.lines = {{{0, U"A "}, {3, U"\u2026"}}};

    std::array<uint8_t, 32768> atlas{};
    const auto tile = [&](size_t byte) { return std::span(atlas).subspan((byte - 1) * 128, 128); };
    tile('A').front() = 0x12;
    tile(0x85).front() = 0x34;
    tile(0x85).back() = 0x56;

    assert(PreloadedChoiceLine(record, 62) == &record.lines[0]);
    assert(PreloadedChoiceLine(record, 94) == &record.lines[1]);
    assert(!PreloadedChoiceLine(record, 78));
    assert(ExpectedPreloadedChoiceGlyph(record, 160, 62, atlas, tile('A')) == U'A');
    assert(ExpectedPreloadedChoiceGlyph(record, 168, 62, atlas, tile(' ')) == U' ');
    assert(ExpectedPreloadedChoiceGlyph(record, 164, 94, atlas, tile(0x85)) == U'\u2026');
    assert(!ExpectedPreloadedChoiceGlyph(record, 160, 62, atlas, tile(0x85)));
    assert(!ExpectedPreloadedChoiceGlyph(record, 160, 62, atlas, tile('A').first(127)));
    assert(!ExpectedPreloadedChoiceGlyph(record, 160, 62, std::span(atlas).first(32767), tile('A')));
    for (int x : {152, 161, 172, 176, std::numeric_limits<int>::min(), std::numeric_limits<int>::max()})
        assert(!ExpectedPreloadedChoiceGlyph(record, x, 62, atlas, tile('A')));

    record.lineCount = 3;
    record.raw += "\rA";
    record.lines[2] = {5, U"A"};
    assert(PreloadedChoiceLine(record, 54) == &record.lines[0]);
    assert(PreloadedChoiceLine(record, 78) == &record.lines[1]);
    assert(PreloadedChoiceLine(record, 102) == &record.lines[2]);
    assert(!PreloadedChoiceLine(record, 62));
    assert(!PreloadedChoiceLine(record, 94));
    assert(ExpectedPreloadedChoiceGlyph(record, 164, 102, atlas, tile('A')) == U'A');
    assert(!ExpectedPreloadedChoiceGlyph(record, 168, 102, atlas, tile('A')));
    std::array<uint8_t, 128> wrong{};
    wrong.front() = tile(0x85).front();
    assert(!ExpectedPreloadedChoiceGlyph(record, 164, 78, atlas, wrong));
    record.lines[1].rawOffset = 0;
    assert(!ExpectedPreloadedChoiceGlyph(record, 164, 78, atlas, tile('A')));
    record.lines[1].rawOffset = std::numeric_limits<uint32_t>::max();
    assert(!ExpectedPreloadedChoiceGlyph(record, 164, 78, atlas, tile(0x85)));

    record.raw = std::string(30, 'A') + ' ';
    record.lines[0] = {0, std::u32string(30, U'A') + U' '};
    assert(ExpectedPreloadedChoiceGlyph(record, 44, 54, atlas, tile('A')) == U'A');
    assert(ExpectedPreloadedChoiceGlyph(record, 284, 54, atlas, tile(' ')) == U' ');
    assert(!ExpectedPreloadedChoiceGlyph(record, 292, 54, atlas, tile(' ')));
    record.lines[0].text += U'A';
    assert(!PreloadedChoiceLine(record, 54));
    record.lines[0].text.clear();
    assert(!PreloadedChoiceLine(record, 54));
    record.simple = false;
    assert(!PreloadedChoiceLine(record, 102));
    record.simple = true;
    record.lineCount = 4;
    assert(!PreloadedChoiceLine(record, 102));
}
