// SaturnTaisen GA36 sampling profiler (LD_PRELOAD). Every STPROF_US microseconds of CPU time of the process
// (ITIMER_PROF) the interrupted thread's PC and LR are recorded; at exit the samples are written to STPROF_OUT
// as "pc lr tid" lines, with the load base of the main executable on the first line.
#define _GNU_SOURCE
#include <link.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/syscall.h>
#include <sys/time.h>
#include <ucontext.h>
#include <unistd.h>

#define MAXS (1 << 20)
static unsigned long s_pc[MAXS], s_lr[MAXS];
static unsigned short s_tid[MAXS];
static volatile int s_n;
static unsigned long s_base;
static int s_pid;

static void on_prof(int sig, siginfo_t *si, void *ctx) {
    (void)sig; (void)si;
    int i = __sync_fetch_and_add(&s_n, 1);
    if (i >= MAXS) return;
    ucontext_t *u = (ucontext_t *)ctx;
    s_pc[i] = u->uc_mcontext.arm_pc;
    s_lr[i] = u->uc_mcontext.arm_lr;
    s_tid[i] = (unsigned short)(syscall(SYS_gettid) - s_pid);
}

static int find_base(struct dl_phdr_info *info, size_t size, void *data) {
    (void)size; (void)data;
    if (info->dlpi_name == NULL || info->dlpi_name[0] == 0) { s_base = info->dlpi_addr; return 1; }
    return 0;
}

static void dump(void) {
    const char *out = getenv("STPROF_OUT");
    struct itimerval off = {0};
    setitimer(ITIMER_PROF, &off, NULL);
    FILE *f = fopen(out ? out : "stprof.txt", "w");
    if (!f) return;
    int n = s_n < MAXS ? s_n : MAXS;
    fprintf(f, "base %lx samples %d\n", s_base, n);
    for (int i = 0; i < n; i++) fprintf(f, "%lx %lx %u\n", s_pc[i] - s_base, s_lr[i] - s_base, s_tid[i]);
    // (the libraries' places, to tell samples in SDL or libc apart: "map start end offset path" lines)
    FILE *maps = fopen("/proc/self/maps", "r");
    if (maps) {
        char line[512];
        while (fgets(line, sizeof line, maps)) {
            if (strstr(line, " r-xp ") || strstr(line, " r-xs ")) fprintf(f, "map %s", line);
        }
        fclose(maps);
    }
    fclose(f);
}

__attribute__((constructor)) static void start(void) {
    if (!getenv("STPROF_OUT")) return;
    s_pid = getpid();
    dl_iterate_phdr(find_base, NULL);
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_sigaction = on_prof;
    sa.sa_flags = SA_SIGINFO | SA_RESTART;
    sigaction(SIGPROF, &sa, NULL);
    const char *us = getenv("STPROF_US");
    long period = us ? atol(us) : 1000;
    struct itimerval it = {{0, period}, {0, period}};
    setitimer(ITIMER_PROF, &it, NULL);
    atexit(dump);
}
