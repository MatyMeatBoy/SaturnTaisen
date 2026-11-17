// Synthetic Saturn headers, no game sectors. Test the actual launcher description.
#define LAUNCHER_GAME_NAME "SaturnTaisenFirst"
#define LAUNCHER_DISC_NAME "Sakura Wars"
#define LAUNCHER_DISC_PRODUCT "GS-9037"
#define LAUNCHER_DISC_VERSION "V1.005"
#define LAUNCHER_EXTRA_DISC_PRODUCT ""
#define LAUNCHER_EXTRA_DISC_NAME ""
#define LAUNCHER_SOUNDTRACK_DISCS ""
#define LAUNCHER_CUSTOM_SOUNDTRACK 0
#define SATRECOMP_COMBOS ""
#include "../local/deps/satrecomp/launcher/src/description.cpp"
#include <cassert>
#include <array>

void DrawSakuraSaves(launcher::PageContext&) {}
void ShutdownSakuraSaves() {}

int main(int argc,char** argv) {
    assert(argc==2);
    const auto root=std::filesystem::absolute(argv[1]);
    const auto folder=root/"local"/"prepared"/"disc1";
    std::filesystem::create_directories(folder);
    const auto iso=folder/"Track 01.iso";
    const auto cue=folder/"game.cue";
    auto write=[&](const char* version,const char* number) {
        std::array<char,2048> header{};
        std::fill(header.begin(),header.end(),' ');
        std::memcpy(header.data(),"SEGA SEGASATURN ",16);
        std::memcpy(header.data()+0x20,"GS-9037",7);
        std::memcpy(header.data()+0x2a,version,6);
        std::memcpy(header.data()+0x38,number,6);
        std::ofstream file(iso,std::ios::binary);file.write(header.data(),header.size());
    };
    std::ofstream(cue) << "FILE \"Track 01.iso\" BINARY\n  TRACK 01 MODE1/2048\n    INDEX 01 00:00:00\n";
    write("V1.005","CD-1/2");
    const auto& about=launcher::describe();
    assert(about.check(cue.string()).usable());
    const auto program=root/"local"/"build"/"sakura"/""; // SDL_GetBasePath ends with a separator
    const auto nearby=about.find_nearby(program);
    assert(!nearby.empty() && std::filesystem::equivalent(nearby,cue));
    write("V1.006","CD-1/2");
    assert(!about.check(cue.string()).usable());
    write("V1.005","CD-2/2");
    assert(about.check(cue.string()).message.find("Disco 2/2")!=std::string::npos);
    launcher::Launch launch;launch.file=cue.string();launch.folder=root/"profile";
    launch.on=[](const char*) {return false;};
    const auto arguments=about.arguments(launch);
    auto video=std::find(arguments.begin(),arguments.end(),"--video");
    assert(video!=arguments.end() && *(video+1)=="software");
    std::puts("Launcher finds prepared discs with SDL paths and rejects unknown revisions");
}
