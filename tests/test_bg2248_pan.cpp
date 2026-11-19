#include "bg2248_verified_pan.h"

#include <cassert>

int main() {
    using namespace port;
    const auto frameIndex = [](unsigned x, unsigned y) {
        return (y + kPanPictureOffsetY) * kPanFrameWidth + x + kPanPictureOffsetX;
    };
    for (const unsigned height : {208u, 296u}) {
        std::vector<uint32_t> picture(kPanInsetWidth * height);
        for (unsigned y = 0; y < height; ++y) {
            for (unsigned x = 0; x < kPanInsetWidth; ++x) {
                picture[y * kPanInsetWidth + x] = (y << 9) | x;
            }
        }

        std::vector<uint32_t> frame(kPanFrameWidth * kPanFrameHeight);
        std::vector<uint8_t> top(frame.size(), 6);
        const auto limit = height - kPanPictureHeight;
        for (const unsigned offset : {0u, limit / 2, limit}) {
            for (unsigned y = 0; y < kPanPictureHeight; ++y) {
                for (unsigned x = 0; x < kPanInsetWidth; ++x) {
                    frame[frameIndex(x, y)] = picture[(y + offset) * kPanInsetWidth + x];
                    top[frameIndex(x, y)] = 4;
                }
            }
            assert(FindVerticalPanOffset(picture, frame, top, height) == offset);
        }

        const auto pixel = frameIndex(21, 22);
        top[pixel] = 0;
        assert(!FindVerticalPanOffset(picture, frame, top, height));
        top[pixel] = 4;
        frame[pixel] ^= 1;
        assert(!FindVerticalPanOffset(picture, frame, top, height));
        assert(!FindVerticalPanOffset(picture, frame, {}, height));
        assert(!FindVerticalPanOffset(picture, frame, top, 143));

        std::fill(picture.begin(), picture.end(), 0);
        std::fill(frame.begin(), frame.end(), 0);
        assert(!FindVerticalPanOffset(picture, frame, top, height));
        assert(DecodePinnedPan({}, kPanInsetWidth, height, 64688, 0).empty());
    }
}
