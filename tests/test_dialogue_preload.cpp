// SPDX-License-Identifier: GPL-3.0-only
#include "dialogue_preload.h"

#include <cassert>
#include <string>
#include <vector>

namespace {
void be32(std::vector<uint8_t>& data, size_t at, uint32_t value) {
    for (unsigned byte = 0; byte < 4; ++byte)
        data[at + byte] = uint8_t(value >> (24 - 8 * byte));
}

std::vector<uint8_t> table(const std::vector<std::string>& raw, size_t totalBytes = 0) {
    const size_t start = 8 + 8 * raw.size();
    std::vector<uint8_t> data(start);
    be32(data, 0, uint32_t(start / 2));
    for (size_t i = 0; i < raw.size(); ++i) {
        be32(data, 8 + 8 * i, uint32_t(50000 + i));
        be32(data, 12 + 8 * i, uint32_t(data.size() - start));
        data.insert(data.end(), {0x00, 0x05, 0x12, 0x34});
        data.insert(data.end(), raw[i].begin(), raw[i].end());
        data.push_back(0);
        if (data.size() % 2) data.push_back(0);
    }
    be32(data, 4, uint32_t(data.size() / 2));
    if (totalBytes) data.resize(totalBytes, 0x77);
    return data;
}
}

int main() {
    using port::DialoguePreload;
    DialoguePreload cache;
    const std::string sample = "It\x92s\r\x80\x85";
    const auto data = table({sample, "a\tb", std::string(32, 'x'), "1\r2\r3\r4\r5", "\x81"});
    assert(cache.Add("0100TBL.BIN", data));
    assert(!cache.Add("0100TBL.BIN", data));
    assert(cache.TableCount() == 1 && cache.SourceBytes() == data.size());
    assert(cache.RecordCount() == 5 && cache.ReadyCount() == 1);
    assert(!cache.Sealed() && cache.Tables().empty());

    std::vector<uint8_t> low(0x100000), high(0x100000);
    constexpr size_t tableAt = 0x24000, textPointer = 0x6851c;
    std::copy(data.begin(), data.end(), low.begin() + tableAt);
    const uint32_t textAddress = 0x00224000 + 8 + 8 * 5 + 4;
    be32(high, textPointer, textAddress);
    assert(!cache.Locate(low, high).valid);
    cache.Seal();
    assert(cache.Sealed() && !cache.Add("another.bin", data));
    const auto tables = cache.Tables();
    assert(tables.size() == 1 && tables[0].name == "0100TBL.BIN");
    assert(tables[0].bytes == data && tables[0].fingerprint != 0);
    const auto witness = cache.Locate(low, high);
    assert(witness.valid && witness.table == 0 && witness.record == 0 && witness.offset == 0);
    const auto* record = cache.Get(witness);
    assert(record && record->id == 50000 && record->index == 0 && record->offset == 48);
    assert(record->prefix0 == 5 && record->prefix1 == 0x1234 && record->raw == sample);
    assert(record->simple && record->lineCount == 2);
    assert(record->lines[0].text == U"It\u2019s" && record->lines[0].rawOffset == 0);
    assert(record->lines[1].text == U"\u20ac\u2026" && record->lines[1].rawOffset == 5);
    assert(tables[0].records[1].raw == "a\tb" && !tables[0].records[1].simple);
    assert(!cache.Get({false, 0, 0, 0}));
    assert(!cache.Get({true, 1, 0, 0}));
    assert(!cache.Get({true, 0, 5, 0}));
    assert(!cache.Get({true, 0, 0, uint32_t(sample.size() + 1)}));
    be32(high, textPointer, textAddress + uint32_t(sample.size()));
    assert(cache.Locate(low, high).offset == sample.size());
    assert(cache.Locate(low, high).valid);
    be32(high, textPointer, textAddress + uint32_t(sample.size() + 1));
    assert(!cache.Locate(low, high).valid);
    be32(high, textPointer, textAddress - 1);
    assert(!cache.Locate(low, high).valid);
    be32(high, textPointer, 0x06000000);
    assert(!cache.Locate(low, high).valid);
    be32(high, textPointer, textAddress);
    low[tableAt + data.size() - 1] ^= 1;
    assert(!cache.Locate(low, high).valid); // altered tail, same header and pointed record
    low[tableAt + data.size() - 1] ^= 1;
    assert(!cache.Locate(std::span(low).first(low.size() - 1), high).valid);
    assert(!cache.Locate(low, std::span(high).first(high.size() - 1)).valid);

    DialoguePreload layout;
    const std::string fullLine(31, 'z');
    assert(layout.Add("four-lines", table({
        fullLine + "\r" + fullLine + "\r" + fullLine + "\r" + fullLine, "", "A\r\rB",
    })));
    layout.Seal();
    const auto preparedTables = layout.Tables();
    const auto& prepared = preparedTables.front().records;
    assert(layout.ReadyCount() == 3 && prepared[0].lineCount == 4);
    assert(prepared[0].lines[3].rawOffset == 96 && prepared[0].lines[3].text.size() == 31);
    assert(prepared[1].raw.empty() && prepared[1].lineCount == 1);
    assert(prepared[2].lines[1].text.empty() && prepared[2].lines[2].rawOffset == 3);

    DialoguePreload ambiguous;
    assert(ambiguous.Add("a", data) && ambiguous.Add("b", data));
    ambiguous.Seal();
    assert(!ambiguous.Locate(low, high).valid);

    DialoguePreload bounded;
    assert(!bounded.Add("truncated", std::span(data).first(data.size() - 1)));
    const auto large = table({"a"}, 4 * 1024 * 1024);
    assert(bounded.Add("large1", large) && bounded.Add("large2", large));
    assert(!bounded.Add("above-byte-budget", table({"a"})));
    assert(bounded.SourceBytes() == 8 * 1024 * 1024);
    DialoguePreload maxTables;
    const auto small = table({"x"});
    for (size_t i = 0; i < 128; ++i) assert(maxTables.Add(std::to_string(i), small));
    assert(!maxTables.Add("129th", small));
    DialoguePreload maxRecords;
    assert(maxRecords.Add("65k", table(std::vector<std::string>(65535, "x"))));
    assert(maxRecords.RecordCount() == 65535 && !maxRecords.Add("overflow", small));
}
