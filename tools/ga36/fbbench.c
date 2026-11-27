// SaturnTaisen GA36: how fast can a frame go to /dev/fb0? Reads what the screen shows and writes the same
// pixels back (the screen does not change), timing memcpy, NEON 64-byte stores and a copy to plain RAM.
// Build: clang --target=arm-linux-gnueabihf -mcpu=cortex-a7 -mfpu=neon-vfpv4 -mfloat-abi=hard -O2
#include <arm_neon.h>
#include <fcntl.h>
#include <linux/fb.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>

static double now_ms(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e3 + t.tv_nsec / 1e6;
}

static void neon_copy(uint8_t *dst, const uint8_t *src, size_t n) {
    for (size_t i = 0; i + 64 <= n; i += 64) {
        uint8x16x4_t v = vld1q_u8_x4(src + i);
        vst1q_u8_x4(dst + i, v);
    }
}

static void neon_copy_pld(uint8_t *dst, const uint8_t *src, size_t n) {
    for (size_t i = 0; i + 64 <= n; i += 64) {
        __builtin_prefetch(src + i + 256);
        uint8x16_t a = vld1q_u8(src + i), b = vld1q_u8(src + i + 16), c = vld1q_u8(src + i + 32), d = vld1q_u8(src + i + 48);
        vst1q_u8(dst + i, a);
        vst1q_u8(dst + i + 16, b);
        vst1q_u8(dst + i + 32, c);
        vst1q_u8(dst + i + 48, d);
    }
}

int main(void) {
    int fd = open("/dev/fb0", O_RDWR);
    if (fd < 0) { perror("fb0"); return 1; }
    struct fb_var_screeninfo var;
    struct fb_fix_screeninfo fix;
    ioctl(fd, FBIOGET_VSCREENINFO, &var);
    ioctl(fd, FBIOGET_FSCREENINFO, &fix);
    printf("fb %ux%u bpp %u stride %u smem %u\n", var.xres, var.yres, var.bits_per_pixel, fix.line_length, fix.smem_len);
    const size_t bytes = (size_t)fix.line_length * var.yres;
    uint8_t *fb = mmap(NULL, fix.smem_len, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    if (fb == MAP_FAILED) { perror("mmap"); return 1; }
    uint8_t *ram = aligned_alloc(64, bytes), *ram2 = aligned_alloc(64, bytes);
    double t = now_ms();
    memcpy(ram, fb, bytes); // (what the screen shows now: written back below)
    printf("read fb->ram memcpy: %.2f ms\n", now_ms() - t);
    memcpy(ram2, ram, bytes);
    const int reps = 30;
    struct { const char *name; int kind; } tests[] = {
        {"memcpy ram->fb", 0}, {"neon64 ram->fb", 1}, {"neon64+pld ram->fb", 2}, {"memcpy ram->ram", 3}, {"neon64 ram->ram", 4},
    };
    for (unsigned k = 0; k < sizeof tests / sizeof tests[0]; k++) {
        double best = 1e9, sum = 0;
        for (int r = 0; r < reps; r++) {
            t = now_ms();
            switch (tests[k].kind) {
            case 0: memcpy(fb, ram, bytes); break;
            case 1: neon_copy(fb, ram, bytes); break;
            case 2: neon_copy_pld(fb, ram, bytes); break;
            case 3: memcpy(ram2, ram, bytes); break;
            case 4: neon_copy(ram2, ram, bytes); break;
            }
            const double d = now_ms() - t;
            sum += d;
            if (d < best) best = d;
        }
        printf("%-20s best %.2f ms, mean %.2f ms (%u bytes)\n", tests[k].name, best, sum / reps, (unsigned)bytes);
    }
    memcpy(fb, ram, bytes);
    return 0;
}
