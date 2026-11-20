#include "tactical_ground.h"

#include <cassert>
#include <cstring>
#include <set>

// The generated ground table (patch 0188): every entry must be found by its own signature, keys must be unique and
// distinct from the hand-written grounds, and the geometry must be the one the sampler and the placement assembler expect.
int main() {
    using namespace port::tactical_ground;
    const Entry* hand[] = {&kStage01, &kStage02, &kStage04, &kStage05, &kStage06, &kStage21};
    std::set<uint64_t> seen;
    for (const auto* entry : hand) assert(seen.insert(entry->mapSignature).second);
    assert(std::size(kGenerated) == 17);
    for (const auto& entry : kGenerated) {
        assert(seen.insert(entry.mapSignature).second);
        assert(Find(entry.mapSignature) == &entry);
        assert(std::strncmp(entry.path, "SAKURA2/MAP/MAP", 15) == 0);
        assert(entry.groundPage == 0x40000);
        assert(entry.bytes > 0 && entry.assetHash && entry.centreLayout);
        assert(entry.worldWidth > 0 && entry.worldWidth <= 1024 && entry.worldHeight > 0 && entry.worldHeight <= 1024);
        assert(entry.mapEndX == entry.worldWidth);
        if (entry.placementTileSize) {
            assert(entry.placementTileSize % 2 == 0);
            assert(entry.worldWidth % (entry.placementTileSize / 2) == 0);
            assert(entry.worldHeight % (entry.placementTileSize / 2) == 0);
        }
    }
    assert(Find(0) == nullptr && Find(0x1234) == nullptr);
    // The existing grounds keep their entries.
    assert(Find(kStage02.mapSignature) == &kStage02 && Find(kStage21.mapSignature) == &kStage21);
}
