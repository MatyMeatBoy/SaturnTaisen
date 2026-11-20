// T116: the reuse of unchanged VDP2 lines must give the picture (and the presentation planes) the line-by-line
// composition gives, whatever is written and whenever it is written. Two renderers run in lockstep over invented
// memory: one composes every line, one may replay lines of an unchanged frame. Writes go through the same
// "write, and tell the renderer if the value changed" rule the machine uses.
#include "renderer.h"
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <random>
#include <vector>

using namespace satrecomp::video;

namespace {
struct Side {
    std::vector<uint8_t> vram1, vram2, cram, fb0, fb1;
    std::vector<uint32_t> picture;
    Renderer renderer;
    bool reuse;
    explicit Side(bool on)
        : vram1(0x80000), vram2(0x80000), cram(0x1000), fb0(0x40000), fb1(0x40000), renderer({vram1.data(), {fb0.data(), fb1.data()}, vram2.data(), cram.data()}),
          reuse(on) {
        renderer.SetMode(Renderer::Mode::Software, [this](uint32_t *pixels, uint32_t w, uint32_t h) { picture.assign(pixels, pixels + size_t(w) * h); });
        renderer.SetLineReuse(on);
    }
    void Reg(unsigned address, unsigned value) { renderer.WriteVdp2Reg(address, value); }
    void Vram(uint32_t address, uint8_t value) {
        if (vram2[address] != value) {
            vram2[address] = value;
            // (T116_MUTATE=1 forgets to tell the renderer: the test must then fail, which proves it can see a missed write)
            static const bool forget = std::getenv("T116_MUTATE") != nullptr;
            if (!forget) {
                renderer.NoteVideoMemoryWrite();
            }
        }
    }
    void Cram(uint32_t address, uint8_t value) {
        if (cram[address] != value) {
            cram[address] = value;
            renderer.NoteVideoMemoryWrite();
        }
    }
};

struct Op {
    enum Kind { Vram, Cram, Reg } kind;
    uint32_t line, address, value;
};
} // namespace

int main() {
    Side plain(false), reused(true);
    std::mt19937 rng(12345);
    for (Side *side : {&plain, &reused}) {
        std::mt19937 fill(777);
        for (auto &b : side->vram2) {
            b = static_cast<uint8_t>(fill());
        }
        for (auto &b : side->cram) {
            b = static_cast<uint8_t>(fill());
        }
        Side &s = *side;
        // The setup of tests/test_vdp2_color.cpp: NBG0 and NBG1 as 32,768-colour bitmaps, split VRAM-A banks
        s.Reg(0x00, 0x8000);
        s.Reg(0x0e, 0x0100);
        s.Reg(0x10, 0x4444);
        s.Reg(0x12, 0x4444);
        s.Reg(0x14, 0x5555);
        s.Reg(0x16, 0x5555);
        s.Reg(0x20, 3);
        s.Reg(0x28, 0x3232);
        s.Reg(0x3c, 0x0010);
        s.Reg(0xf8, 0x0102);
        s.Reg(0xec, 0);
        s.Reg(0xac, 0x8000); // the back screen takes one colour per line from VRAM, so a write to VRAM shows in the picture
        s.renderer.SetResolution(320, 224, false);
        s.renderer.LatchDisplayMode();
        s.renderer.CapturePresentation(true);
    }
    const unsigned frames = 600;
    unsigned compared = 0, withWrites = 0, changedFrames = 0;
    for (unsigned frame = 0; frame < frames; frame++) {
        // What happens this frame: mostly nothing, so that runs of unchanged frames appear
        std::vector<Op> ops;
        const unsigned roll = rng() % 100;
        const unsigned count = roll < 62 ? 0 : roll < 90 ? 1 : 2 + rng() % 3;
        for (unsigned i = 0; i < count; i++) {
            Op op{};
            op.line = rng() % 232; // (some after the last line: a write between frames)
            const unsigned kind = rng() % 10;
            if (kind < 5) {
                op.kind = Op::Vram;
                op.address = rng() % 8 == 0 ? 0x20000 + rng() % 0x10000 : rng() % 448; // (mostly the per-line back screen colours)
                op.value = rng();
            } else if (kind < 7) {
                op.kind = Op::Cram;
                op.address = rng() % 0x1000;
                op.value = rng();
            } else {
                op.kind = Op::Reg;
                const unsigned regs[] = {0x70, 0x74, 0x78, 0x80, 0xf0, 0x100, 0x108};
                op.address = regs[rng() % 7];
                op.value = (rng() % 3 == 0) ? 0 : rng() % 40;
            }
            ops.push_back(op);
            withWrites++;
        }
        const bool fbChange = rng() % 25 == 0;
        const uint8_t fbValue = rng();
        const unsigned fbIndex = rng() % 1000;
        for (Side *side : {&plain, &reused}) {
            Side &s = *side;
            if (fbChange) {
                s.fb0[fbIndex] = fbValue; // (the displayed framebuffer changes between frames only)
            }
            s.renderer.BeginFrame();
            for (unsigned y = 0; y < 224; y++) {
                for (const Op &op : ops) {
                    if (op.line == y) {
                        switch (op.kind) {
                        case Op::Vram: s.Vram(op.address, static_cast<uint8_t>(op.value)); break;
                        case Op::Cram: s.Cram(op.address, static_cast<uint8_t>(op.value)); break;
                        case Op::Reg: s.Reg(op.address, op.value); break;
                        }
                    }
                }
                s.renderer.RenderLine(y);
            }
            for (const Op &op : ops) {
                if (op.line >= 224) { // (between frames)
                    switch (op.kind) {
                    case Op::Vram: s.Vram(op.address, static_cast<uint8_t>(op.value)); break;
                    case Op::Cram: s.Cram(op.address, static_cast<uint8_t>(op.value)); break;
                    case Op::Reg: s.Reg(op.address, op.value); break;
                    }
                }
            }
            s.renderer.EndFrame();
        }
        const auto &a = plain.renderer.PresentationFrame(), &b = reused.renderer.PresentationFrame();
        const bool same = plain.picture == reused.picture && a.foreground == b.foreground && a.underSprites == b.underSprites &&
                          a.source == b.source && a.topSource == b.topSource && a.underSource == b.underSource &&
                          a.spriteWhiteWeight == b.spriteWhiteWeight;
        if (!same) {
            fprintf(stderr, "frame %u: the reused picture differs from the composed one\n", frame);
            return 1;
        }
        compared++;
        static std::vector<uint32_t> last;
        if (last != plain.picture) {
            changedFrames++;
        }
        last = plain.picture;
    }
    fprintf(stderr, "vdp2 line reuse: %u frames identical (the picture changed in %u), %u writes, %llu lines replayed\n", compared,
            changedFrames, withWrites, static_cast<unsigned long long>(reused.renderer.ReusedLines()));
    if (changedFrames < 50) {
        fprintf(stderr, "the invented writes hardly changed the picture: the test is blind\n");
        return 1;
    }
    if (reused.renderer.ReusedLines() == 0) {
        fprintf(stderr, "the test never exercised a replay\n");
        return 1;
    }
    return 0;
}
