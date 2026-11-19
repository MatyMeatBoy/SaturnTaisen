#include "eve_inset.h"

static_assert(port::EveCropFits({16, 8, 544, 272}, 576, 288));
static_assert(port::EveCropFits(port::kEve202PcCrop, 576, 320));
static_assert(port::EveCropFits({32, 24, 544, 264}, 576, 288));
static_assert(!port::EveCropFits({16, 8, 544, 281}, 576, 288));
static_assert(!port::EveCropFits({-1, 0, 544, 272}, 576, 288));
static_assert(!port::EveCropFits({0, 0, 0, 272}, 576, 288));
static_assert(!port::EveCropFits({2147483647, 0, 2147483647, 10}, 576, 288));

int main() {}
