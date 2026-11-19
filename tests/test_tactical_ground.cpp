#include "tactical_ground.h"
#include <array>
#include <cassert>

int main(int argc, char** argv) {
    assert(argc == 2);
    using namespace port::tactical_ground;

    // One original 4×4 direct-colour SPRED image with a known key and grid.
    std::array<uint8_t, 128> bytes{};
    std::memcpy(bytes.data(), "SEGA SPRED 02.0M", 16);
    const auto put = [&](int at, unsigned value, int size) {
        for (int i = 0; i < size; ++i) bytes[at + i] = value >> (8 * (size - i - 1));
    };
    put(16, 64, 4);
    put(20, 64, 4);
    put(24, 2, 4);
    put(64, 1, 2);
    put(80, 4, 2);
    put(82, 4, 2);
    put(84, 5, 2);
    put(92, 32, 4);
    const auto setPixel = [&](int x, int y, uint16_t rgb) {
        const auto at = 96 + 2 * (4 * y + x);
        bytes[at] = rgb & 255;
        bytes[at + 1] = rgb >> 8;
    };
    setPixel(0, 0, 0x03FF); // cyan, which is transparent
    setPixel(2, 0, 0x7C00); // red
    setPixel(0, 2, 0x03E0); // green
    setPixel(2, 2, 0x001F); // blue

    const std::filesystem::path root = argv[1];
    const Entry entry{"ground.spr", bytes.size(), port::PreparedHash(bytes), 0, 0, 2, 2, 2};
    assert(Load(root, entry).empty());
    const auto write = [&](size_t size) {
        std::ofstream file(root / entry.path, std::ios::binary);
        assert(file.write(reinterpret_cast<const char*>(bytes.data()), size));
    };
    write(bytes.size());
    const auto ground = Load(root, entry);
    assert((ground == std::vector<uint32_t>{0, 0xFF0000FF, 0xFF00FF00, 0xFFFF0000}));
    assert(Sample(ground, entry, 1, 1) == 0xFFFF0000);
    assert(Sample(ground, entry, -1, 0) == 0 && Sample(ground, entry, 0, -1) == 0);
    assert(Sample(ground, entry, 2, 0) == 0 && Sample(ground, entry, 0, 2) == 0);
    assert(Sample({}, entry, 1, 1) == 0);

    auto narrower = entry;
    narrower.mapEndX = 1;
    assert(Sample(ground, narrower, 1, 1) == 0);
    narrower.worldWidth = 1;
    assert(Load(root, narrower).empty());

    bytes.back() ^= 1;
    write(bytes.size());
    assert(Load(root, entry).empty());
    write(bytes.size() - 1);
    assert(Load(root, entry).empty());
}
