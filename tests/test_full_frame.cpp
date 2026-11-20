// TP2b: the full-frame table and its native-frame guard. Compile with the SDK port/ include path (see tests/test_eve_square.cpp).
#include "full_frame.h"

#include <cassert>
#include <set>
#include <string>
#include <vector>

int main() {
    using namespace port;
    static_assert(kFullFrameCount == 6);
    std::set<std::uint64_t> palettes;
    std::set<std::string> names;
    for (const auto& row : kFullFrameRows) {
        assert(FullFrameRowValid(row));
        assert(names.insert(row.name).second);
        assert(palettes.insert(row.palette).second);  // a shared palette could not identify a picture
        assert(row.crop.x + row.crop.width <= int(row.pcWidth) && row.crop.y + row.crop.height <= int(row.pcHeight));
        // The crop keeps the Saturn frame shape within 20 %: it is the same picture, not a different composition.
        const double drift = (double(row.crop.width) / row.crop.height) / (320.0 / 224.0);
        assert(drift > 0.8 && drift < 1.2);
    }
    // The whole frame is the destination, at any integer scale.
    const auto target = EveInsetDestination(kFullFrameRect, 320, 48, 6);
    assert((target == EveRect{320, 48, 1920, 1344}));

    std::vector<std::uint8_t> layer(320 * 224, 2);
    assert(IsFullFrame(layer, 320, 224));
    layer[320 * 100 + 7] = 4;  // one pixel from another plane (a sprite, text or a fade edge) keeps the native frame
    assert(!IsFullFrame(layer, 320, 224));
    layer.assign(320 * 224, 6);  // no winning layer
    assert(!IsFullFrame(layer, 320, 224));
    layer.assign(320 * 224, 2);
    assert(!IsFullFrame(layer, 288, 144));
    assert(!IsFullFrame(std::span<const std::uint8_t>(layer).first(320 * 223), 320, 224));
    // A crop outside the PC picture is rejected.
    FullFrameRow bad = kFullFrameRows[0];
    bad.crop = {600, 0, 100, 100};
    assert(!FullFrameRowValid(bad));
}
