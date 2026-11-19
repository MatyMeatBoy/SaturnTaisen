#include "ra_client.h"
#include <array>
#include <cassert>

#include <string_view>
#include <vector>

using namespace port::ra;
using namespace std::string_view_literals;

constexpr auto kDisc1 = "c4db9d08d56d1fbf78322852775d4818"sv;
constexpr auto kDisc2 = "c306c094d0177459b31f411cd4cd44a9"sv;
constexpr auto kLogin = R"({"Success":true,"User":"MockUser","Token":"MockToken","Score":0,"SoftcoreScore":0,"Messages":0})"sv;
constexpr auto kCatalog = R"({"Success":true,"GameId":16546,"Title":"Synthetic test","ConsoleId":39,"ImageIconUrl":"https://media.retroachievements.org/Images/1.png","RichPresenceGameId":16546,"RichPresencePatch":"","Sets":[{"AchievementSetId":777,"GameId":16546,"Title":null,"Type":"core","ImageIconUrl":"https://media.retroachievements.org/Images/1.png","Achievements":[{"ID":876543,"Title":"Read both work RAM banks","Description":"Synthetic condition","Flags":3,"Points":5,"MemAddr":"0xH000011=3_0xH100004=7","Author":"Fixture","BadgeName":"00234","Created":1367266583,"Modified":1376929305}],"Leaderboards":[]}]})"sv;
constexpr auto kStart = R"({"Success":true,"Unlocks":[],"HardcoreUnlocks":[]})"sv;
constexpr auto kAward = R"({"Success":true,"Score":0,"SoftcoreScore":5,"AchievementID":876543,"AchievementsRemaining":0})"sv;

Request TakeOne(Client& client,std::string_view action) {
    auto requests=client.TakeRequests();
    assert(requests.size()==1);
    assert(requests[0].data.starts_with(action));
    return std::move(requests[0]);
}

int main(int argc,char** argv) {
    assert(argc==2);
    const auto profile=std::filesystem::path(argv[1]);
    std::vector<uint8_t> low(kBankSize),high(kBankSize);
    low.back()=0xab;
    high.front()=0xcd;
    high.back()=0xef;
    std::array<uint8_t,4> buf{0xaa,0xaa,0xaa,0xaa};
    const auto read=[&](uint32_t address){return ReadSaturnMemory(low,high,address,buf);};
    assert(read(kBankSize-1)==4 && buf[0]==0xab && buf[1]==0xcd);
    assert(read(2*kBankSize-1)==1 && buf[0]==0xef && buf[1]==0xcd);
    assert(read(2*kBankSize)==0 && read(0xffffffffu)==0);
    assert(ReadSaturnMemory({},high,0,buf)==0);
    assert(ReadSaturnMemory(low,high,0,{})==0);
    std::vector<uint8_t> header(2048);
    constexpr auto magic="SEGA SEGASATURN "sv;
    std::copy(magic.begin(),magic.end(),header.begin());
    const auto id=SaturnDiscHash(header);
    assert(id=="4c6bc0e574e65d6e943d5ce9997d2ec4");
    header[900]=99;
    assert(id==SaturnDiscHash(header));
    assert(SaturnDiscHash(std::span<const uint8_t>(header).first(511)).empty());
    header[0]=0;
    assert(SaturnDiscHash(header).empty());

    Client client;
    assert(client.GetState()==State::SignedOut);
    assert(!client.SetMedia("00000000000000000000000000000000"));
    assert(client.TakeRequests().empty());
    assert(client.SetMedia(kDisc1));
    assert(client.TakeRequests().empty());
    assert(client.Login("MockUser","MockToken"));
    assert(!client.Login("Other","OtroToken"));
    auto login=TakeOne(client,"r=login2");
    assert(login.data.find("&p=")==std::string::npos);
    assert(client.Respond(login.id,200,kLogin));
    assert(!client.Respond(login.id,200,kLogin));
    auto set=TakeOne(client,"r=achievementsets");
    assert(set.data.find(kDisc1)!=std::string::npos);
    assert(client.Respond(set.id,200,kCatalog));
    auto start=TakeOne(client,"r=startsession");
    assert(start.data.find("&h=0&")!=std::string::npos);
    assert(client.Respond(start.id,200,kStart));

    client.Evaluate(low,high);
    assert(client.GetState()==State::Ready);
    auto list=client.Achievements();
    assert(list.size()==1 && list[0].id==876543 && list[0].points==5 && !list[0].unlocked);
    assert(client.TakeUnlocks().empty() && client.TakeRequests().empty());
    client.Evaluate(low,high);
    low[0x11]=3;
    high[4]=7;
    client.Evaluate(low,high);
    auto opened=client.TakeUnlocks();
    assert(opened.size()==1 && opened[0].id==876543 && opened[0].badgeUrl.starts_with("https://"));
    assert(low[0x11]==3 && high[4]==7);
    auto award=TakeOne(client,"r=awardachievement");
    assert(award.data.find("&h=0&")!=std::string::npos);
    assert(client.Respond(award.id,-2,{}));
    award=TakeOne(client,"r=awardachievement");
    assert(client.Respond(award.id,200,kAward));
    client.Evaluate(low,high);
    assert(client.TakeUnlocks().empty() && client.TakeRequests().empty());
    assert(client.Achievements()[0].unlocked);
    assert(client.SetMedia(kDisc2));
    auto media=TakeOne(client,"r=gameid");
    assert(media.data.find(kDisc2)!=std::string::npos);
    assert(client.Respond(media.id,200,R"({"Success":true,"GameID":16546})"));
    assert(client.GetState()==State::Ready);
    assert(!client.SetMedia("00000000000000000000000000000000"));
    client.Reset();
    client.Evaluate(low,high);
    assert(client.GetState()!=State::Ready && client.TakeUnlocks().empty());
    {
        Client online(profile);
        assert(online.SetMedia(kDisc1));
        assert(online.Login("MockUser","MockToken"));
        auto request=TakeOne(online,"r=login2");
        assert(online.Respond(request.id,200,kLogin));
        request=TakeOne(online,"r=achievementsets");
        assert(online.Respond(request.id,200,kCatalog));
        request=TakeOne(online,"r=startsession");
        assert(online.Respond(request.id,200,kStart));
        low[0x11]=0;
        high[4]=0;
        online.Evaluate(low,high);
        online.Evaluate(low,high);
        low[0x11]=3;
        high[4]=7;
        online.Evaluate(low,high);
        request=TakeOne(online,"r=awardachievement");
        auto pending=AwardJournal(profile).Pending("MockUser");
        assert(pending.size()==1 && pending[0].achievement==876543 && pending[0].hash==kDisc1);
        assert(online.Respond(request.id,-2,{}));
    }
    {
        Client resumed(profile);
        assert(resumed.SetMedia(kDisc2));
        assert(resumed.Login("MockUser","MockToken"));
        auto request=TakeOne(resumed,"r=login2");
        assert(resumed.Respond(request.id,200,kLogin));
        request=TakeOne(resumed,"r=achievementsets");
        assert(resumed.Respond(request.id,200,kCatalog));
        request=TakeOne(resumed,"r=startsession");
        assert(resumed.Respond(request.id,200,kStart));
        resumed.Evaluate(low,high);
        request=TakeOne(resumed,"r=awardachievement");
        assert(request.data.find(kDisc1)!=std::string::npos);
        assert(resumed.Respond(request.id,200,kAward));
        assert(AwardJournal(profile).Pending("MockUser").empty());
        assert(resumed.TakeUnlocks().empty());
    }
}
