#include "launch_ready.h"
#include <cassert>
#include <fstream>
int main(int argc,char** argv) {
    const auto root=std::filesystem::path(argv[1]);
    auto file=root/"ready.flag";
    assert(!recomp::LaunchReady(file));
    { std::ofstream out(file);out<<"partial"; }
    assert(!recomp::LaunchReady(file));
    std::filesystem::remove(file);
    assert(recomp::PublishLaunchReady(file));
    assert(recomp::LaunchReady(file));
    assert(!std::filesystem::exists(file.string()+".tmp"));
    assert(!recomp::PublishLaunchReady(root/"missing"/"ready.flag"));
    assert(!recomp::LaunchReady(root/"missing"/"ready.flag"));
    assert(recomp::PublishLaunchReady({})); // direct CLI has no observer
}
