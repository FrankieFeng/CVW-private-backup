#!/usr/bin/env bash
set -euo pipefail
repair_root=$(cd -- "$(dirname -- "$0")/../.." && pwd)
repair_src="$repair_root/native/store-lifecycle/build-source"
if [[ -e "$repair_src" ]]; then
  echo "Refusing to overwrite existing build-source: $repair_src" >&2
  exit 1
fi
git clone --no-checkout https://github.com/TKOTKCh/wasmer_chainmaker.git "$repair_src"
git -C "$repair_src" checkout --detach 091074013fa056df0c6502262eae425927272e10
git -C "$repair_src" apply --check "$repair_root/native/store-lifecycle/selector-token.patch"
git -C "$repair_src" apply "$repair_root/native/store-lifecycle/selector-token.patch"
cd "$repair_src"
echo 'c8778c4b1e301d2d60fc07708d94593bdc5c47d79f19f28c83417dbc37005385  Cargo.lock' | sha256sum -c -
CARGO_BUILD_JOBS=1 cargo +1.81.0 build --release --manifest-path lib/c-api/Cargo.toml \
  --no-default-features --features wat,compiler,cranelift,wasi,middlewares,webc_runner --locked
# Build output remains separate for review. Installing it is an explicit local copy.
sha256sum target/release/libwasmer.so
