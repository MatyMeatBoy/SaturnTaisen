#include "ra_journal.h"
#include <cassert>
#include <string>

using namespace port::ra;
constexpr auto kFirst="c4db9d08d56d1fbf78322852775d4818";
constexpr auto kSecond="c306c094d0177459b31f411cd4cd44a9";

int main(int argc,char** argv) {
    assert(argc==2);
    const std::filesystem::path profile(argv[1]);
    const PendingAward original{"MockUser", kFirst, 16546, 876543, 1700000000};
    const PendingAward other{"OtherUser", kSecond, 16546, 876543, 1700000010};
    {
        AwardJournal journal(profile);
        assert(journal.Enqueue(original));
        auto duplicate=original;
        duplicate.username="mockuser";
        duplicate.hash=kSecond;
        assert(journal.Enqueue(duplicate));
        assert(journal.Enqueue(other));
        auto invalid=original;
        invalid.username="X\nInjected";
        assert(!journal.Enqueue(invalid));
        invalid=original;
        invalid.hash="../../../other-directory/file.txt";
        assert(!journal.Enqueue(invalid));
    }
    {
        AwardJournal journal(profile);
        const auto pending=journal.Pending("MOCKUSER");
        assert(pending.size()==1 && pending[0]==original);
        assert(journal.Pending("OtherUSER")==std::vector<PendingAward>{other});
        assert(journal.Pending("WrongUser").empty());
        auto wrong=original;
        wrong.achievement++;
        assert(!journal.Acknowledge(wrong));
        assert(journal.Acknowledge(original));
        assert(journal.Pending("MockUser").empty());
        assert(journal.Pending("OtherUser").size()==1);
    }
}
