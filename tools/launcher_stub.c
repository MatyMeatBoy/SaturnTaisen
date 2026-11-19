// SPDX-License-Identifier: GPL-3.0-only
// The only program at the release root. Everything else (launcher, game, helpers, DLLs) lives in app/;
// this starts app\SaturnTaisen.exe with the same arguments and the same console, waits for it and returns
// its exit code, so --help, --integration-info and frontends behave exactly as with the real launcher.
// Built statically (no DLL beside it): tools/package_release.py compiles it with the toolchain's clang.
#include <windows.h>
#include <wchar.h>
#include <stdio.h>

static void fail(const wchar_t* text) {
    MessageBoxW(NULL, text, L"SaturnTaisen", MB_OK | MB_ICONERROR);
}

// The arguments after the program name, exactly as typed (quotes kept).
static const wchar_t* arguments_of(const wchar_t* line) {
    int quoted = 0;
    for (; *line; line++) {
        if (*line == L'"') quoted = !quoted;
        else if (!quoted && (*line == L' ' || *line == L'\t')) break;
    }
    while (*line == L' ' || *line == L'\t') line++;
    return line;
}

static wchar_t self[32768], folder[32768], program[32768], command[65536];

int main(void) {
    // Built as a window program (-mwindows): a double click never opens a console. Started from a terminal,
    // it borrows that console so --help and --integration-info still print there; otherwise the launcher
    // (a console program) is started with its console hidden, and everything it starts inherits that.
    const BOOL terminal = AttachConsole(ATTACH_PARENT_PROCESS);
    const wchar_t* arguments = arguments_of(GetCommandLineW());
    DWORD length = GetModuleFileNameW(NULL, self, 32768);
    if (!length || length >= 32768) { fail(L"No se pudo localizar SaturnTaisen.exe."); return 1; }
    wchar_t* slash = wcsrchr(self, L'\\');
    if (!slash) { fail(L"Ruta no válida."); return 1; }
    slash[1] = 0;
    _snwprintf(folder, 32768, L"%lsapp", self);
    _snwprintf(program, 32768, L"%ls\\SaturnTaisen.exe", folder);
    if (GetFileAttributesW(program) == INVALID_FILE_ATTRIBUTES) {
        fail(L"Falta la carpeta «app» junto a SaturnTaisen.exe. Descomprime el ZIP completo.");
        return 1;
    }
    _snwprintf(command, 65536, L"\"%ls\" %ls", program, arguments);
    STARTUPINFOW startup = {0};
    startup.cb = sizeof startup;
    PROCESS_INFORMATION process = {0};
    if (terminal) {  // (a window program gets no standard handles of its own: hand over the terminal's)
        startup.dwFlags = STARTF_USESTDHANDLES;
        startup.hStdInput = CreateFileW(L"CONIN$", GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, OPEN_EXISTING, 0, NULL);
        startup.hStdOutput = CreateFileW(L"CONOUT$", GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, OPEN_EXISTING, 0, NULL);
        startup.hStdError = startup.hStdOutput;
        HANDLE given = GetStdHandle(STD_OUTPUT_HANDLE);  // (redirected to a file or pipe by a frontend: keep that)
        if (given && given != INVALID_HANDLE_VALUE) startup.hStdOutput = given;
    }
    if (!CreateProcessW(program, command, NULL, NULL, TRUE, terminal ? 0 : CREATE_NO_WINDOW, NULL, folder, &startup, &process)) {
        fail(L"No se pudo iniciar app\\SaturnTaisen.exe.");
        return 1;
    }
    CloseHandle(process.hThread);
    WaitForSingleObject(process.hProcess, INFINITE);
    DWORD code = 1;
    GetExitCodeProcess(process.hProcess, &code);
    CloseHandle(process.hProcess);
    return (int)code;
}
