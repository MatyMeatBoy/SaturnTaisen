// The window starts borderless by default; --fullscreen forces it; --windowed, headless and test windows opt out.
#include "window_policy.h"
#include <cassert>
int main() {
    assert(port::StartsBorderless(false, false, false));  // the default
    assert(port::StartsBorderless(true, false, false));   // --fullscreen / launcher.ini video fullscreen
    assert(port::StartsBorderless(true, true, true));     // an explicit --fullscreen wins
    assert(!port::StartsBorderless(false, true, false));  // --windowed
    assert(!port::StartsBorderless(false, false, true));  // hidden test window or headless
    return 0;
}
