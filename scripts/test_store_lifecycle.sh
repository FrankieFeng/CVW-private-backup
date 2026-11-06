#!/usr/bin/env bash
set -euo pipefail
repair_root=$(cd -- "$(dirname -- "$0")/.." && pwd)
repair_vm="$repair_root/chainmaker/chainmaker-vm-wasmer/vm-wasmer/v2@v2.4.0"
repair_lib="$repair_vm/wasmer-go/packaged/lib/linux-amd64"
repair_out="$repair_root/audit/store-lifecycle/bin"
if [[ $(uname -s) != Linux || $(uname -m) != x86_64 ]]; then
  echo 'This port is validated with the packaged Linux amd64 Cranelift runtime.' >&2
  exit 2
fi
mkdir -p "$repair_out"
# Keep the test independent of an older Wasmer installed elsewhere on this host.
export LD_LIBRARY_PATH="$repair_lib"
export GOMAXPROCS=${GOMAXPROCS:-2}
cd "$repair_vm"
go build -p=2 .
go test -race -p=2 . -run '^TestStoreRepair' -count=1 -timeout=120s -v
go test -p=2 -c -o "$repair_out/store-lifecycle.test" .
"$repair_out/store-lifecycle.test" -test.run '^TestStoreRepair' -test.timeout=120s
cc -std=c11 -Wall -Wextra -Werror "$repair_root/native/store-lifecycle/wasi_thread_test.c" \
  -I"$repair_vm/wasmer-go/packaged/include" -L"$repair_lib" -lwasmer \
  -o "$repair_out/wasi_thread_test"
"$repair_out/wasi_thread_test"
