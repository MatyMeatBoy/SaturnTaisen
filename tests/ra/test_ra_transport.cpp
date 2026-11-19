#include "ra_transport.h"
#include <cassert>
#include <chrono>
#include <thread>

using namespace port::ra;

int main() {
    constexpr auto api="https://retroachievements.org/dorequest.php";
    constexpr auto badge="https://media.retroachievements.org/Badge/00234_lock.png";
    assert(ClassifyEndpoint(api,true)==Endpoint::Api);
    assert(ClassifyEndpoint(api,false)==Endpoint::Invalid);
    assert(ClassifyEndpoint(badge,false)==Endpoint::Badge);
    assert(ClassifyEndpoint(badge,true)==Endpoint::Invalid);
    assert(ClassifyEndpoint("http://retroachievements.org/dorequest.php",true)==Endpoint::Invalid);
    assert(ClassifyEndpoint("https://retroachievements.org.attacker.invalid/dorequest.php",true)==Endpoint::Invalid);
    assert(ClassifyEndpoint("https://retroachievements.org/dorequest.php?x=1",true)==Endpoint::Invalid);
    assert(ClassifyEndpoint("https://media.retroachievements.org/Badge/../00328.png",false)==Endpoint::Invalid);
    assert(ClassifyEndpoint("https://media.retroachievements.org/Badge/%2f00328.png",false)==Endpoint::Invalid);

    const auto owner=std::this_thread::get_id();
    RequestWorker worker([owner](const Request& request) {
        assert(std::this_thread::get_id()!=owner);
        if(request.id==2) throw 0;
        return Response{request.id,200,"synthetic"};
    });
    assert(worker.Submit({1,api,"simulated","application/x-www-form-urlencoded"}));
    assert(worker.Submit({2,badge,{},{}}));
    std::vector<Response> output;
    for(int attempt=0;attempt<50 && output.size()<2;++attempt) {
        auto next=worker.TakeResponses();
        output.insert(output.end(),next.begin(),next.end());
        std::this_thread::sleep_for(std::chrono::milliseconds(2));
    }
    assert(output.size()==2);
    assert(output[0].id==1 && output[0].status==200 && output[0].body=="synthetic");
    assert(output[1].id==2 && output[1].status<0 && output[1].body.empty());
}
