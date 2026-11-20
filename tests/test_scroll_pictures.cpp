// TP2: the scroll-picture table. Compile with the SDK port/ include path (see tests/test_bg2533_pan.cpp).
#include "scroll_pictures.h"

#include <cassert>
#include <cstring>
#include <set>
#include <string>
#include <vector>

int main() {
    using namespace port;
    // Every registered crop is bounded. Keys never collide.
    std::set<std::pair<uint64_t, uint64_t>> keys;
    std::set<std::string> names;
    for (const auto& row : kScrollPictures) {
        assert(ScrollRowValid(row));
        assert(names.insert(row.name).second);
        assert(keys.insert({row.palette, row.cells}).second);
        assert(row.nativeBytes > 0x610 + (row.width / 8) * (row.height / 8) * 4);
        const auto last = ScrollPcCrop(row, ScrollRange(row));
        assert(last.x + last.w <= row.pcWidth && last.y + last.h <= row.pcHeight);
        if (row.fit.rateMilli) {
            for (unsigned offset = 0; offset <= ScrollRange(row); ++offset) {
                const auto crop = ScrollPcCrop(row, offset);
                assert(crop.w && crop.h);
                assert(crop.x + crop.w <= row.pcWidth && crop.y + crop.h <= row.pcHeight);
            }
            continue;
        }
        assert(ScrollPcCrop(row, 0).w == 576 && ScrollPcCrop(row, 0).h == 288);
        if (row.axis == ScrollAxis::Horizontal) {
            assert(row.height == 144 && row.pcWidth == 2 * row.width);
            assert(last.x == 2 * (row.width - 288) && ScrollPcCrop(row, 0).y == (row.pcHeight - 288) / 2);
        } else {
            assert(row.width == 288 && row.pcHeight == 2 * row.height);
            assert(last.y == 2 * (row.height - 144) && ScrollPcCrop(row, 0).x == (row.pcWidth - 576) / 2);
        }
    }

    for (const char* name : {"BG1207", "BG1285", "BG2207", "BG2248", "BG2265", "BG2266",
                             "BG2267", "BG2268", "BG2269", "BG2295", "BG2533"})
        assert(names.contains(name));
    for (const char* name : {"BG1282", "BG2130", "BG2176", "BG2515"})
        assert(names.contains(name));
    // These use the existing still-viewport paths.
    for (const char* name : {"BG1306", "BG2238", "BG2260"})
        assert(!names.contains(name));

    // The calibrated rows use independently measured start and end crops.
    const auto byName = [](const char* name) -> const ScrollPicture& {
        for (const auto& row : kScrollPictures)
            if (!std::strcmp(row.name, name)) return row;
        assert(false);
        return kScrollPictures[0];
    };
    {
        const auto& horizontal = byName("BG2077");
        const auto start = ScrollPcCrop(horizontal, 0);
        const auto last = ScrollPcCrop(horizontal, ScrollRange(horizontal));
        assert(start.x == 0 && start.y == 0 && start.w == 670 && start.h == 314);
        assert(last.x == 351 && last.y == 0);
        auto invalid = horizontal;
        invalid.fit.origin = horizontal.pcWidth;
        assert(!ScrollRowValid(invalid));
    }
    {
        const auto& first = byName("BG2172");
        const auto second = ScrollPcCrop(first, ScrollRange(first));
        assert(second.x == 26 && second.y == 278 && second.w == 536 && second.h == 290);
        const auto& last = byName("BG2518");
        const auto middle = ScrollPcCrop(last, 76);
        assert(middle.x == 27 && middle.y == 149 && middle.w == 488 && middle.h == 264);
    }
    {
        // BG2093 (TP2a-size): whole 592x320 PC picture, 320-wide native, 33 integer offsets, the crop never leaves the PC art.
        const auto& row = byName("BG2093");
        assert(row.width == 320 && row.height == 144 && row.pcWidth == 592 && row.pcHeight == 320 && ScrollRange(row) == 32);
        const auto first = ScrollPcCrop(row, 0), last = ScrollPcCrop(row, 32);
        assert(first.x == 23 && first.y == 0 && first.w == 512 && first.h == 320);
        assert(last.x == 80 && last.x + last.w == row.pcWidth && last.h == 320);
        auto invalid = row;
        invalid.fit.length = 513;
        assert(!ScrollRowValid(invalid));
    }
    // The hand-written pictures keep the crops they had before the table.
    {
        const auto& row = byName("BG1285");
        const auto crop = ScrollPcCrop(row, 75);
        assert(row.axis == ScrollAxis::Horizontal && crop.x == 150 && crop.y == 16 && crop.w == 576 && crop.h == 288);
        assert(row.palette == 0x8B6362BE73FB2551ull && row.cells == 0xBE01460AC7277CC6ull && row.nativeBytes == 77648);
    }
    {
        const auto& row = byName("BG2248");
        const auto crop = ScrollPcCrop(row, 63);
        assert(row.axis == ScrollAxis::Vertical && crop.x == 0 && crop.y == 126 && crop.w == 576 && crop.h == 288);
        assert(row.height == 296 && ScrollRange(row) == 152);
    }
    {
        const auto& row = byName("BG2533");
        assert(row.style == ScrollStyle::EdgeRamp && row.cells == 0 && row.palette == 0x09884FF240CB5BF3ull);
        assert(ScrollPcCrop(row, 224).x == 448 && ScrollPcCrop(row, 224).y == 16);
        assert(byName("BG1207").style == ScrollStyle::ActorForeground);
        assert(byName("BG2295").height == 208);
    }

    // Lookup: palette plus first-cell key; the cell key is only asked when a palette matches.
    int asked = 0;
    const auto cellsOf = [&](const char* name) {
        return [&asked, row = &byName(name)] { ++asked; return row->cells; };
    };
    assert(FindScrollPicture(0x1234, cellsOf("BG1285")) == nullptr && asked == 0);
    assert(FindScrollPicture(byName("BG1285").palette, cellsOf("BG1285")) == &byName("BG1285") && asked == 1);
    assert(FindScrollPicture(byName("BG1285").palette, [] { return uint64_t(1); }) == nullptr);
    asked = 0;
    assert(FindScrollPicture(byName("BG2533").palette, [&] { ++asked; return uint64_t(7); }) == &byName("BG2533") && asked == 0);

    // The matcher takes the row's width: a synthetic 456-wide picture pans and a wrong size is refused.
    for (const unsigned width : {320u, 456u, 512u}) {
        std::vector<uint32_t> picture(width * 144);
        for (unsigned y = 0; y < 144; ++y)
            for (unsigned x = 0; x < width; ++x) picture[y * width + x] = (y << 12) | x;
        std::vector<uint32_t> frame(kPanFrameWidth * kPanFrameHeight);
        std::vector<uint8_t> top(frame.size(), 6);
        for (const unsigned offset : {0u, (width - 288) / 2, width - 288}) {
            for (unsigned y = 0; y < 144; ++y)
                for (unsigned x = 0; x < 288; ++x) {
                    const auto at = (y + kPanPictureOffsetY) * kPanFrameWidth + x + kPanPictureOffsetX;
                    frame[at] = picture[y * width + offset + x];
                    top[at] = 4;
                }
            assert(FindHorizontalPanOffset(picture, frame, top, false, width) == offset);
            assert(!FindHorizontalPanOffset(picture, frame, top, false, width + 8));
        }
    }
    return 0;
}
