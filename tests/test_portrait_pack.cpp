#include "portrait_pack.h"
#include <cassert>
int main(int argc,char** argv) {
    assert(argc==2);const auto root=std::filesystem::path(argv[1]);
    std::vector<uint8_t> raw(3200,1);
    {std::ofstream file(root/"native.bin",std::ios::binary);file.write(reinterpret_cast<char*>(raw.data()),raw.size());}
    auto write=[&](unsigned count,const char* name,uint64_t hash) {
        std::ofstream file(root/"manifest.ini");
        file<<"[pack]\nschema=1\nsource_bytes=5505346\nsource_hash=17275614850567186526\npalette_hash=42\ncount="<<count
            <<"\nnative_file="<<name<<"\nnative_hash="<<port::AtlasFingerprint(raw)
            <<"\n[portrait-0]\nnative_id=21\noffset=0\nraw_hash="<<hash
            <<"\nfile1=one.png\nhash1=7\nfile2=two.png\nhash2=8\n";
    };
    port::PortraitPackData data;
    write(1,"native.bin",port::AtlasFingerprint(raw));assert(port::ReadPortraitPack(root,data));
    assert(data.records.size()==1 && data.paletteHash==42 && data.records[0].identity==21);
    write(395,"native.bin",port::AtlasFingerprint(raw));assert(!port::ReadPortraitPack(root,data));
    write(1,"../native.bin",port::AtlasFingerprint(raw));assert(!port::ReadPortraitPack(root,data));
    write(1,"native.bin",7);assert(!port::ReadPortraitPack(root,data));
    {std::ofstream file(root/"native.bin",std::ios::binary|std::ios::trunc);file.put(0);}
    write(1,"native.bin",port::AtlasFingerprint(raw));assert(!port::ReadPortraitPack(root,data));
    assert(!port::KnownPortraitSource(root));
}
