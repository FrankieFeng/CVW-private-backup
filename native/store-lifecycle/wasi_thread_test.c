#define _DEFAULT_SOURCE
#include <wasmer.h>
#include <dirent.h>
#include <stdio.h>
#include <time.h>
static int threads(void) {
    DIR *dir = opendir("/proc/self/task");
    if (!dir) return -1;
    int n = 0; struct dirent *entry;
    while ((entry = readdir(dir))) if (entry->d_name[0] != '.') ++n;
    closedir(dir); return n;
}
int main(void) {
    int before = threads();
    if (before < 1) return 2;
    wasm_engine_t *engine = wasm_engine_new();
    if (!engine) return 3;
    for (int i = 0; i < 4; ++i) {
        wasm_store_t *store = wasm_store_new(engine);
        if (!store) return 4;
        wasi_config_t *config = wasi_config_new("store-lifecycle-test");
        if (!config) return 5;
        wasi_env_t *env = wasi_env_new(store, config);
        if (!env) return 6;
        wasi_env_delete(env);
        wasm_store_delete(store);
    }
    wasm_engine_delete(engine);
    for (int i = 0; i < 100 && threads() != before; ++i) {
        struct timespec delay = {0, 20000000}; nanosleep(&delay, 0);
    }
    int after = threads();
    printf("runtime=%s threads_before=%d threads_after=%d\n", wasmer_version(), before, after);
    return before == after ? 0 : 1;
}
