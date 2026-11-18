#include "background_workers.h"
#include <cassert>
#include <atomic>
#include <chrono>
#include <stdexcept>
#include <thread>
using namespace std::chrono_literals;
int main() {
    port::BackgroundWorkers workers;
    std::atomic<unsigned> active=0,peak=0,completed=0;
    std::vector<port::BackgroundWorkers::Job> jobs;
    for(unsigned i=0;i<40;i++) jobs.push_back([&]{
        const auto now=++active;auto old=peak.load();
        while(old<now && !peak.compare_exchange_weak(old,now)) {}
        std::this_thread::sleep_for(2ms);--active;++completed;return true;
    });
    workers.Start(std::move(jobs),3);workers.Wait();
    assert(completed==40 && active==0 && peak<=3 && peak>=2);
    assert(workers.Completed()==40 && workers.Failed()==0);
    jobs.clear();jobs.push_back([]()->bool {throw std::runtime_error("bad asset");});
    jobs.push_back([]{return false;});jobs.push_back([]{return true;});
    workers.Start(std::move(jobs),2);workers.Wait();
    assert(workers.Completed()==3 && workers.Failed()==2);
    // Cancellation must join in-flight jobs and skip those not yet started.
    completed=0;active=0;jobs.clear();std::atomic<bool> release=false;
    for(unsigned i=0;i<40;i++)jobs.push_back([&]{
        ++active;while(!release.load())std::this_thread::yield();
        --active;++completed;return true;
    });
    workers.Start(std::move(jobs),2);
    const auto deadline=std::chrono::steady_clock::now()+2s;
    while(active!=2 && std::chrono::steady_clock::now()<deadline)std::this_thread::yield();
    assert(active==2);
    workers.Cancel();release=true;workers.Wait();
    assert(completed==2 && active==0);
    // Empty/disabled work must never start a worker; counts reset on restart.
    workers.Start({[] {return true;}},0);workers.Wait();assert(workers.Completed()==0);
    assert(port::BackgroundWorkers::Bound(100,100)==8);
    assert(port::BackgroundWorkers::Bound(100,2)==2);
    assert(port::BackgroundWorkers::Bound(0,3)==0);
    // The interactive budget leaves cores for game/audio; preparation can use more.
    assert(port::BackgroundWorkerCount(false,16)==4);
    assert(port::BackgroundWorkerCount(true,16)==8);
    assert(port::BackgroundWorkerCount(false,0)==1);
}
