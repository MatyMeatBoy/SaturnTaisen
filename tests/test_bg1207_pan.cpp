#include "bg1207_verified_pan.h"

#include <cassert>

int main() {
    using namespace port;
    std::vector<uint32_t> picture(kHorizontalPanWidth * kHorizontalPanHeight);
    for (unsigned y = 0; y < kHorizontalPanHeight; ++y) {
        for (unsigned x = 0; x < kHorizontalPanWidth; ++x) {
            picture[y * kHorizontalPanWidth + x] = (y << 9) | x;
        }
    }

    std::vector<uint32_t> frame(kPanFrameWidth * kPanFrameHeight);
    std::vector<uint8_t> top(frame.size(), 6);
    const auto frameIndex = [](unsigned x, unsigned y) {
        return (y + kPanPictureOffsetY) * kPanFrameWidth + x + kPanPictureOffsetX;
    };
    for (const unsigned offset : {0u, 208u, 224u}) {
        for (unsigned y = 0; y < kHorizontalPanHeight; ++y) {
            for (unsigned x = 0; x < kPanInsetWidth; ++x) {
                frame[frameIndex(x, y)] = picture[y * kHorizontalPanWidth + offset + x];
                top[frameIndex(x, y)] = 4;
            }
        }
        assert(FindHorizontalPanOffset(picture, frame, top, false) == offset);
    }

    const auto actor = frameIndex(139, 77);
    top[actor] = 2;
    frame[actor] = 0xFFFFFF;
    assert(FindHorizontalPanOffset(picture, frame, top, true) == 224);
    assert(!FindHorizontalPanOffset(picture, frame, top, false));
    top[actor] = 0;
    assert(!FindHorizontalPanOffset(picture, frame, top, true));
    top[actor] = 2;
    frame[frameIndex(23, 61)] ^= 1;
    assert(!FindHorizontalPanOffset(picture, frame, top, true));
    frame[frameIndex(23, 61)] ^= 1;
    for (unsigned y = 0; y < 4; ++y) {
        for (unsigned x = 0; x < kPanInsetWidth; ++x) {
            top[frameIndex(x, y)] = 2;
        }
    }
    assert(!FindHorizontalPanOffset(picture, frame, top, true));
    assert(!FindHorizontalPanOffset(picture, frame, {}, true));
}
