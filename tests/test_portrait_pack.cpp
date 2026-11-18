#include "portrait_pack.h"
#include <cassert>
#include <sstream>

namespace fs = std::filesystem;

static std::string manifest(const fs::path &folder, unsigned count, unsigned first = 1) {
    fs::create_directories(folder);
    const std::vector<uint8_t> native(count * 3200, 1);
    {
        std::ofstream dst(folder / "native.bin", std::ios::binary);
        dst.write(reinterpret_cast<const char *>(native.data()), native.size());
    }
    std::ostringstream ini;
    ini << "[pack]\nschema=1\nsource_bytes=" << port::kPortraitSourceBytes
        << "\nsource_hash=" << port::kPortraitSourceHash << "\npalette_hash=42\ncount=" << count
        << "\nnative_file=native.bin\nnative_hash=" << port::AtlasFingerprint(native) << "\n";
    for (unsigned i=0;i<count;++i) {
        const auto raw=std::span{native}.subspan(i*3200,3200);
        ini << "\n[portrait-" << i << "]\nnative_id=" << first+i << "\noffset=" << i*3200
            << "\nraw_hash=" << port::AtlasFingerprint(raw)
            << "\nfile1=one.png\nhash1=7\nfile2=two.png\nhash2=8\n";
    }
    const auto text=ini.str();
    std::ofstream(folder / "manifest.ini",std::ios::binary) << text;
    return text;
}

static void receipt(const fs::path &bundle, const std::string &text, unsigned count) {
    std::array<uint8_t,48> raw{};
    std::memcpy(raw.data(),"STFHD01",8);
    auto put=[&](size_t offset,uint64_t value,int size) {
        for(int i=0;i<size;i++)raw[offset+i]=uint8_t(value>>(i*8));
    };
    put(8,1,4);
    put(16,port::kPortraitSourceBytes,8);
    put(24,port::kPortraitSourceHash,8);
    put(32,port::PreparedHash(std::span(reinterpret_cast<const uint8_t *>(text.data()),text.size())),8);
    put(40,count,4);
    std::ofstream dst(bundle / "hd-pack.stfp",std::ios::binary);
    dst.write(reinterpret_cast<const char *>(raw.data()),raw.size());
}

static void verifyFallback(const fs::path& root) {
    const auto bundle=root/"hd-resources", personal=root/"user/mods/hd-portraits";
    const auto bundled=manifest(bundle/"portraits",2);
    receipt(bundle,bundled,2);
    port::PortraitPack pack;
    const auto open=[&](size_t variants) {
        pack.Open(personal,bundle);
        assert(pack.VariantCount()==variants);
    };
    open(4); // missing personal manifest
    fs::create_directories(personal);
    std::ofstream(personal/"manifest.ini") << "invalid";
    open(4);
    manifest(personal,1);
    open(4); // parses, but count is stale
    manifest(personal,2,3);
    open(4); // same count, different manifest
    manifest(personal,2);
    open(4); // personal manifest bound to the receipt
    manifest(personal,1);
    receipt(bundle,bundled,1);
    open(0); // both candidates unverified
}

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
    verifyFallback(root);
}
