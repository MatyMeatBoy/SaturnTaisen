#include "eve_inset.h"
#include <cassert>
#include <vector>

int main() {
    using namespace port;
    constexpr EveRect square{104, 40, 112, 112};
    constexpr std::uint64_t palette = 0x319E682E63DC3A4Eull;
    std::vector<std::uint8_t> layer(320 * 224);
    for (int y = square.y; y < square.y + square.height; ++y)
        for (int x = square.x; x < square.x + square.width; ++x)
            layer[y * 320 + x] = 5;
    assert(IsEveInset({layer, palette, 320, 224, true}, palette, square));
    assert(!IsEveInset({layer, palette, 320, 224, true}, palette, kEve202NativeRect));
    const auto target = EveInsetDestination(square, 320, 48, 6);
    assert((target == EveRect{944, 288, 672, 672}));
    layer[0] = 5;
    assert(!IsEveInset({layer, palette, 320, 224, true}, palette, square));
}
