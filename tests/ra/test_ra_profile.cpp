#include "ra_profile.h"

#include <cassert>
#include <fstream>
#include <iterator>

using namespace port::ra;

int main(int argc,char** argv) {
    assert(argc==2);
    const std::filesystem::path profile(argv[1]);
    assert(!LoadCredentials(profile));
    const Credentials test{"MockAccount","local-synthetic-token-never-from-web"};
    assert(!SaveCredentials(profile,{"","unsafe"}));
    assert(!SaveCredentials(profile,{"injected\nline","unsafe"}));
    assert(SaveCredentials(profile,test));
    assert(LoadCredentials(profile)==test);
    const auto file=profile/"retroachievements"/"account.dat";
    {
        std::ifstream stream(file,std::ios::binary);
        const std::string raw(std::istreambuf_iterator<char>(stream),{});
        assert(!raw.empty() && raw.find(test.token)==std::string::npos);
    }
    assert(SaveCredentials(profile,{"OtherMockAccount","replacement"}));
    assert(LoadCredentials(profile)->username=="OtherMockAccount");
    assert(ForgetCredentials(profile));
    assert(!std::filesystem::exists(file) && !LoadCredentials(profile));
    assert(ForgetCredentials(profile));

    Progress data{"MockAccount", "ready", {{876543,5,true,"Fixture","Text with\r\nlines","00234"}}};
    assert(SaveProgress(profile,data));
    const auto view=LoadProgress(profile);
    assert(view && view->username==data.username && view->state==data.state && view->achievements.size()==1);
    assert(view->achievements[0].unlocked && view->achievements[0].description=="Text with  lines");
}
