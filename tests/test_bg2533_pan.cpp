#include "bg2533_verified_pan.h"

#include <cassert>

using namespace port;

int main() {
    std::vector<uint32_t> art(kPanPictureWidth * kPanPictureHeight);
    for (unsigned y = 0; y < kPanPictureHeight; ++y) {
        for (unsigned x = 0; x < kPanPictureWidth; ++x) {
            art[y * kPanPictureWidth + x] = (x << 8) | y;
        }
    }
    std::vector<uint32_t> frame(kPanFrameWidth * kPanFrameHeight);
    std::vector<uint8_t> layers(frame.size(), 6);
    const auto index = [](unsigned x, unsigned y) {
        return (y + kPanPictureOffsetY) * kPanFrameWidth + x + kPanPictureOffsetX;
    };
    const auto show = [&](unsigned start, unsigned width) {
        for (unsigned y = 0; y < kPanPictureHeight; ++y) {
            for (unsigned x = 0; x < kPanInsetWidth; ++x) {
                const auto at = index(x, y);
                frame[at] = x < width ? art[y * kPanPictureWidth + start + x] : 0;
                layers[at] = x < width ? 4 : 2;
            }
        }
    };

    show(75, 288);
    auto full = FindVerifiedPanPosition(art, frame, layers);
    assert(full && full->offset == 75 && full->visibleWidth == 288);
    show(224, 272);
    auto edge = FindVerifiedPanPosition(art, frame, layers);
    assert(edge && edge->offset == 224 && edge->visibleWidth == 272);

    layers[index(10, 10)] = 2;
    assert(!FindVerifiedPanPosition(art, frame, layers));
    layers[index(10, 10)] = 4;
    frame[index(10, 10)] ^= 1;
    assert(!FindVerifiedPanPosition(art, frame, layers));
    assert(!FindVerifiedPanPosition(art, frame, {}));
    assert(DecodePinnedBG2533({}).empty());
}
