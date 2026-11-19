#include "bg1207_verified_pan.h"

#include <cassert>

int main() {
    using namespace port;
    std::vector<uint32_t> picture(kBG1207Width * kBG1207Height);
    for (unsigned y = 0; y < kBG1207Height; ++y) {
        for (unsigned x = 0; x < kBG1207Width; ++x) {
            picture[y * kBG1207Width + x] = (y << 9) | x;
        }
    }

    std::vector<uint32_t> frame(kPanFrameWidth * kPanFrameHeight);
    std::vector<uint8_t> top(frame.size(), 6);
    const auto frameIndex = [](unsigned x, unsigned y) {
        return (y + kPanPictureOffsetY) * kPanFrameWidth + x + kPanPictureOffsetX;
    };
    for (const unsigned offset : {0u, 208u, 224u}) {
        for (unsigned y = 0; y < kBG1207Height; ++y) {
            for (unsigned x = 0; x < kPanInsetWidth; ++x) {
                frame[frameIndex(x, y)] = picture[y * kBG1207Width + offset + x];
                top[frameIndex(x, y)] = 4;
            }
        }
        assert(FindBG1207Offset(picture, frame, top, false) == offset);
    }

    const auto actor = frameIndex(139, 77);
    top[actor] = 2;
    frame[actor] = 0xFFFFFF;
    assert(FindBG1207Offset(picture, frame, top, true) == 224);
    assert(!FindBG1207Offset(picture, frame, top, false));
    top[actor] = 0;
    assert(!FindBG1207Offset(picture, frame, top, true));
    top[actor] = 2;
    frame[frameIndex(23, 61)] ^= 1;
    assert(!FindBG1207Offset(picture, frame, top, true));
    frame[frameIndex(23, 61)] ^= 1;
    for (unsigned y = 0; y < 4; ++y) {
        for (unsigned x = 0; x < kPanInsetWidth; ++x) {
            top[frameIndex(x, y)] = 2;
        }
    }
    assert(!FindBG1207Offset(picture, frame, top, true));
    assert(!FindBG1207Offset(picture, frame, {}, true));
}
