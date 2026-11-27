// SaturnTaisen GA36: the frontend's picture path through SDL's software renderer, for comparing SDL builds
// pixel for pixel: an XBGR8888 streaming texture of 320x224 (random pixels, the X byte too), uploaded with
// SDL_UpdateTexture and drawn nearest at exactly 2x into an XRGB8888 640x480 surface (over a clear and a
// filled rectangle), then also at a non-integer size. Prints an FNV-1a hash of the surface and the time.
#include <SDL3/SDL.h>
#include <stdint.h>
#include <stdio.h>

static uint64_t fnv(const void *data, size_t n, uint64_t h) {
    const uint8_t *p = data;
    for (size_t i = 0; i < n; i++) h = (h ^ p[i]) * 1099511628211ull;
    return h;
}

int main(void) {
    SDL_Surface *surface = SDL_CreateSurface(640, 480, SDL_PIXELFORMAT_XRGB8888);
    SDL_Renderer *renderer = SDL_CreateSoftwareRenderer(surface);
    SDL_Texture *texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_XBGR8888, SDL_TEXTUREACCESS_STREAMING, 320, 224);
    if (!surface || !renderer || !texture) { printf("setup: %s\n", SDL_GetError()); return 1; }
    SDL_SetTextureScaleMode(texture, SDL_SCALEMODE_NEAREST);
    static uint32_t pixels[320 * 224];
    uint32_t seed = 12345;
    uint64_t h = 14695981039346656037ull;
    const uint64_t start = SDL_GetTicksNS();
    for (int frame = 0; frame < 60; frame++) {
        for (int i = 0; i < 320 * 224; i++) { seed = seed * 1103515245u + 12345u; pixels[i] = seed ^ (seed >> 13); }
        SDL_UpdateTexture(texture, NULL, pixels, 320 * 4);
        SDL_SetRenderDrawColor(renderer, 10, 20, 30, 255);
        SDL_RenderClear(renderer);
        const SDL_FRect edge = {-3, 13, 646, 454};
        SDL_SetRenderDrawColor(renderer, 129, 65, 76, 255);
        SDL_RenderFillRect(renderer, &edge);
        const SDL_FRect where = {0, 16, 640, 448};
        SDL_RenderTexture(renderer, texture, NULL, &where);
        if (frame % 10 == 9) {
            const SDL_FRect odd = {7, 5, 501, 333};
            SDL_RenderTexture(renderer, texture, NULL, &odd);
        }
        SDL_RenderPresent(renderer);
        SDL_FlushRenderer(renderer);
        h = fnv(surface->pixels, (size_t)surface->pitch * 480, h);
    }
    printf("hash %016llx  %.1f ms for 60 frames\n", (unsigned long long)h, (SDL_GetTicksNS() - start) / 1e6);
    return 0;
}
