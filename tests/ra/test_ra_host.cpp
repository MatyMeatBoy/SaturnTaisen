#include "ra_host.h"

#include <cassert>
#include <chrono>
#include <thread>
#include <vector>

using namespace port::ra;
using namespace std::string_literals;

int main(int argc,char** argv) {
    assert(argc==2);
    const std::filesystem::path profile(argv[1]);
    std::vector<uint8_t> systemArea(512);
    const std::string magic="SEGA SEGASATURN ";
    std::copy(magic.begin(),magic.end(),systemArea.begin());
    auto unused=Session::Open(profile,systemArea,[](const Request&) -> Response {
        assert(false);
        return {};
    });
    assert(!unused);

    const Exchange server=[](const Request& request) -> Response {
            assert(ClassifyEndpoint(request.url,!request.data.empty()) != Endpoint::Invalid);
            if (request.url.starts_with("https://media."))
                return {request.id,404,{}};
            if (request.data.starts_with("r=login2"))
                return {request.id,200,R"({"Success":true,"User":"MockUser","Token":"MockToken","Score":0,"SoftcoreScore":0,"Messages":0})"};
            if (request.data.starts_with("r=achievementsets"))
                return {request.id,200,R"({"Success":true,"GameId":16546,"Title":"Test","ConsoleId":39,"ImageIconUrl":"https://media.retroachievements.org/Images/1.png","RichPresenceGameId":16546,"RichPresencePatch":"","Sets":[{"AchievementSetId":777,"GameId":16546,"Title":null,"Type":"core","ImageIconUrl":"https://media.retroachievements.org/Images/1.png","Achievements":[{"ID":876543,"Title":"Fixture","Description":"Synthetic","Flags":3,"Points":5,"MemAddr":"0xH000011=3","Author":"Fixture","BadgeName":"00234","Created":1367266583,"Modified":1376929305}],"Leaderboards":[]}]})"};
            if (request.data.starts_with("r=startsession"))
                return {request.id,200,R"({"Success":true,"Unlocks":[],"HardcoreUnlocks":[]})"};
            if (request.data.starts_with("r=awardachievement"))
                return {request.id,200,R"({"Success":true,"Score":0,"SoftcoreScore":5,"AchievementID":876543,"AchievementsRemaining":0})"};
            assert(false);
            return {};
        };
    assert(SaveCredentials(profile,{"MockUser","MockToken"}));
    Session player(profile,{"MockUser","MockToken"},"c4db9d08d56d1fbf78322852775d4818",server);
    std::vector<uint8_t> low(kBankSize),high(kBankSize);
    uint64_t frame=0;
    const auto wait=[&](auto predicate) {
        for(int n=0;n<500;++n) {
            ++frame;
            player.Frame(low,high);
            if(predicate())return true;
            std::this_thread::sleep_for(std::chrono::milliseconds(2));
        }
        return false;
    };
    assert(wait([&] {auto view=LoadProgress(profile); return view && view->state=="ready";}));
    ++frame;
            player.Frame(low,high);
    low[0x11]=3;
    assert(wait([&] {return player.Popup(frame)!=nullptr;}));
    assert(player.Popup(frame)->title=="Fixture");
    player.PopupShown(frame);
    assert(wait([&] {return ReadActivity(profile).find("synced 876543")!=std::string::npos;}));
    assert(ReadActivity(profile).find("MockToken")==std::string::npos);
    assert(player.Popup(frame+300)==nullptr);

    const auto offlineProfile=profile/"offline";
    const Credentials account{"MockUser","MockToken"};
    constexpr auto hash="c4db9d08d56d1fbf78322852775d4818";
    assert(SaveCredentials(offlineProfile,account));
    const auto until = [&](Session& game, auto predicate) {
        for(int n=0;n<500;++n) {
            ++frame;
            game.Frame(low,high);
            if(predicate())return true;
            std::this_thread::sleep_for(std::chrono::milliseconds(2));
        }
        return false;
    };
    const auto state = [&] {
        const auto progress=LoadProgress(offlineProfile);
        return progress ? progress->state : std::string{};
    };
    low[0x11]=0;
    {
        Session prime(offlineProfile,account,hash,server);
        assert(until(prime,[&] {return state()=="ready";}));
    }
    assert(LoadOfflineSession(offlineProfile,account.username,hash));
    assert(!LoadOfflineSession(offlineProfile,"DifferentUser",hash));
    unsigned attempted=0;
    {
        Session offline(offlineProfile,account,hash,[&](const Request& request) {
            ++attempted;
            assert(request.data.starts_with("r=login2"));
            return Response{request.id,RC_API_SERVER_RESPONSE_RETRYABLE_CLIENT_ERROR,{}};
        });
        assert(until(offline,[&] {return state()=="offline";}));
        ++frame;
        offline.Frame(low,high);
        low[0x11]=3;
        assert(until(offline,[&] {return offline.Popup(frame)!=nullptr;}));
        assert(AwardJournal(offlineProfile).Pending(account.username).size()==1);
        assert(ReadActivity(offlineProfile).find("synced 876543")==std::string::npos);
    }
    assert(attempted==1);
    {
        Session restored(offlineProfile,account,hash,server);
        assert(until(restored,[&] {return ReadActivity(offlineProfile).find("synced 876543")!=std::string::npos;}));
        assert(AwardJournal(offlineProfile).Pending(account.username).empty());
    }
}
