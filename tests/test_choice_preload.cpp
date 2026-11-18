// SPDX-License-Identifier: GPL-3.0-only
#include "choice_preload.h"

#include <algorithm>
#include <array>
#include <cassert>
#include <string>
#include <vector>

namespace {
void be32(std::vector<uint8_t>& bytes, size_t at, uint32_t value) {
    for (unsigned i = 0; i < 4; ++i) bytes[at + i] = uint8_t(value >> (24 - i * 8));
}

std::vector<uint8_t> table() {
    const std::array<std::string, 7> raw{"A\rB", "C\rD\rE", "one", "A\r", "A\rB", "C\rD", "A\tB\rC"};
    const std::array<uint32_t, 7> ids{100, 101, 102, 103, 104, 104, 105};
    const size_t start = 8 + 8 * raw.size();
    std::vector<uint8_t> bytes(start);
    be32(bytes, 0, uint32_t(start / 2));
    for (size_t i = 0; i < raw.size(); ++i) {
        be32(bytes, 8 + 8 * i, ids[i]);
        be32(bytes, 12 + 8 * i, uint32_t(bytes.size() - start));
        bytes.insert(bytes.end(), 4, 0);
        bytes.insert(bytes.end(), raw[i].begin(), raw[i].end());
        bytes.push_back(0);
        if (bytes.size() % 2) bytes.push_back(0);
    }
    be32(bytes, 4, uint32_t(bytes.size() / 2));
    return bytes;
}

void command(std::vector<uint8_t>& script, size_t at, uint8_t id, uint8_t opcode = 0x2e) {
    const std::array<uint8_t, 9> bytes{opcode, 0x80, 0, 0, id, 0x31, 0x22, 0x13, 0x07};
    std::copy(bytes.begin(), bytes.end(), script.begin() + at);
}
}

int main() {
    using port::ChoicePreload;
    using port::DialoguePreload;
    using port::DialogueWitness;
    const auto bytes = table();
    DialoguePreload catalog;
    ChoicePreload choices;
    std::vector<uint8_t> low(0x100000), high(0x100000);
    std::vector<uint8_t> script(85, 0x42);
    command(script, 1, 100);
    command(script, 11, 101);
    command(script, 21, 102);
    command(script, 31, 103);
    command(script, 41, 104);
    command(script, 51, 105);
    command(script, 61, 100, 0x17);
    command(script, 71, 106);
    script[80] = 0x2e;
    script[81] = 0x80;
    script[82] = 0;
    script[83] = 0;
    script[84] = 100; // Truncated nine-byte command.
    assert(catalog.Add("synthetic table", bytes));
    assert(!choices.Add("synthetic script", script, 0, catalog));
    catalog.Seal();
    assert(!choices.Add("bad index", script, 1, catalog));
    assert(!choices.Add("", script, 0, catalog));
    assert(!choices.Add("short", std::span(script).first(8), 0, catalog));
    assert(choices.Add("synthetic script", script, 0, catalog));
    assert(!choices.Add("synthetic script", script, 0, catalog));
    assert(choices.Commands() == 2);

    std::copy(script.begin(), script.end(), low.begin() + 0x4000);
    std::copy(bytes.begin(), bytes.end(), low.begin() + 0x24000);
    const auto cursor = [&](uint32_t value) { be32(high, 0x685b4, value); };
    cursor(0x0020400a);
    assert(!choices.Locate(low, high, catalog).valid);
    choices.Seal();
    assert(!choices.Add("after sealing", script, 0, catalog));
    assert((choices.Locate(low, high, catalog) == DialogueWitness{true, 0, 0, 0}));
    cursor(0x00204014);
    assert((choices.Locate(low, high, catalog) == DialogueWitness{true, 0, 1, 0}));
    for (uint32_t address : std::array<uint32_t, 11>{0x00204013, 0x0020401e, 0x00204028, 0x00204032, 0x0020403c,
                             0x00204046, 0x00204050, 0x00204059, 0x00203fff, 0x00224001, 0xffffffffu}) {
        cursor(address);
        assert(!choices.Locate(low, high, catalog).valid);
    }
    cursor(0x0020400a);
    low[0x4000 + script.size() - 1] ^= 1;
    assert(!choices.Locate(low, high, catalog).valid);
    low[0x4000 + script.size() - 1] ^= 1;
    low[0x24000 + bytes.size() - 1] ^= 1;
    assert(!choices.Locate(low, high, catalog).valid);
    low[0x24000 + bytes.size() - 1] ^= 1;
    assert(!choices.Locate(std::span(low).first(low.size() - 1), high, catalog).valid);
    assert(!choices.Locate(low, std::span(high).first(high.size() - 1), catalog).valid);

    ChoicePreload ambiguous;
    assert(ambiguous.Add("first", script, 0, catalog));
    assert(ambiguous.Add("second", script, 0, catalog));
    ambiguous.Seal();
    assert(!ambiguous.Locate(low, high, catalog).valid);

    DialoguePreload differentCatalog;
    auto differentBytes = bytes;
    differentBytes[catalog.Tables()[0].records[0].offset] ^= 1;
    assert(differentCatalog.Add("synthetic table", differentBytes));
    differentCatalog.Seal();
    std::copy(differentBytes.begin(), differentBytes.end(), low.begin() + 0x24000);
    assert(!choices.Locate(low, high, differentCatalog).valid);
    std::copy(bytes.begin(), bytes.end(), low.begin() + 0x24000);

    ChoicePreload bounds;
    std::vector<uint8_t> full(128 * 1024, 0);
    command(full, full.size() - 9, 100);
    auto oversized = full;
    oversized.push_back(0);
    assert(!bounds.Add("crosses table base", oversized, 0, catalog));
    for (size_t i = 0; i < 64; ++i) assert(bounds.Add(std::to_string(i), full, 0, catalog));
    assert(!bounds.Add("above source byte budget", script, 0, catalog));
    assert(bounds.Commands() == 64);

    ChoicePreload count;
    for (size_t i = 0; i < 128; ++i) assert(count.Add(std::to_string(i), script, 0, catalog));
    assert(!count.Add("129th", script, 0, catalog));

    ChoicePreload commands;
    for (size_t i = 0; i + 9 <= full.size(); i += 9) command(full, i, 100);
    const auto dense = std::span(full).first(full.size() - (full.size() % 9));
    for (size_t i = 0; i < 4; ++i) assert(commands.Add(std::to_string(i), dense, 0, catalog));
    assert(!commands.Add("above command budget", dense, 0, catalog));
    assert(commands.Commands() == 4 * (dense.size() / 9));
}
