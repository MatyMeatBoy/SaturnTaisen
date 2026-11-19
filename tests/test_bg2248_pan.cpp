#include "bg2248_verified_pan.h"

#include <cassert>

int main() {
    using namespace port;
    std::vector<uint32_t> picture(kBG2248Width * kBG2248Height);
    for (unsigned y = 0; y < kBG2248Height; ++y) {
        for (unsigned x = 0; x < kBG2248Width; ++x) {
            picture[y * kBG2248Width + x] = (y << 9) | x;
        }
    }

    std::vector<uint32_t> frame(kPanFrameWidth * kPanFrameHeight);
    std::vector<uint8_t> top(frame.size(), 6);
    const auto frameIndex = [](unsigned x, unsigned y) {
        return (y + kPanPictureOffsetY) * kPanFrameWidth + x + kPanPictureOffsetX;
    };
    for (const unsigned offset : {0u, 63u, 152u}) {
        for (unsigned y = 0; y < kBG2248InsetHeight; ++y) {
            for (unsigned x = 0; x < kBG2248Width; ++x) {
                frame[frameIndex(x, y)] = picture[(y + offset) * kBG2248Width + x];
                top[frameIndex(x, y)] = 4;
            }
        }
        assert(FindBG2248Offset(picture, frame, top) == offset);
    }

    top[frameIndex(21, 22)] = 0;
    assert(!FindBG2248Offset(picture, frame, top));
    top[frameIndex(21, 22)] = 4;
    frame[frameIndex(21, 22)] ^= 1;
    assert(!FindBG2248Offset(picture, frame, top));
    assert(!FindBG2248Offset(picture, frame, {}));

    std::fill(picture.begin(), picture.end(), 0);
    std::fill(frame.begin(), frame.end(), 0);
    assert(!FindBG2248Offset(picture, frame, top));
    assert(DecodePinnedPan({}, kBG2248Width, kBG2248Height, kBG2248Bytes, 0).empty());
}
