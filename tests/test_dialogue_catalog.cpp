#include "dialogue_catalog.h"
#include <cassert>
#include <vector>
int main() {
    std::vector<uint8_t> data(24);
    auto put=[&](size_t at,unsigned value){for(int n=0;n<4;n++)data[at+n]=uint8_t(value>>(24-n*8));};
    std::vector<uint8_t> first{0,21,1,88,'O','n','e',13,'T','w','o',133,0,0};
    std::vector<uint8_t> second{0,0,0,0,'Y','e','s','!',0,0};
    put(0,12);put(4,(24+first.size()+second.size())/2);put(8,40001);put(12,0);put(16,40002);put(20,first.size());
    data.insert(data.end(),first.begin(),first.end());data.insert(data.end(),second.begin(),second.end());
    std::vector<port::DialogueRecord> records;
    assert(port::ParseEnglishTable(data,records) && records.size()==2);
    assert(records[0].id==40001 && records[0].prefix0==21 && records[0].prefix1==344);
    assert(records[0].raw==std::string("One\rTwo\x85") && records[1].raw=="Yes!");
    assert(records[1].offset==24+first.size());
    auto changed=data;changed[0]=0xFF;assert(!port::ParseEnglishTable(changed,records) && records.empty());
    changed=data;changed[23]=255;assert(!port::ParseEnglishTable(changed,records));
    changed=data;for(size_t i=24+first.size();i<changed.size();i++)changed[i]='X';
    assert(!port::ParseEnglishTable(changed,records));
    assert(!port::ParseEnglishTable(std::span<const uint8_t>(data).first(20),records));
}
