#!/bin/bash
set -e
OP=/root/autodl-tmp/op
K=$OP/kernel
O=$OP/kout
TC=$OP/toolchain/clang/bin

export PATH=$TC:$PATH
export ARCH=arm64
export LLVM=1
export LLVM_IAS=1
export CROSS_COMPILE=aarch64-linux-gnu-
export CLANG_TRIPLE=aarch64-linux-gnu-

# ---- spoof build identity to match the factory kernel exactly ----
export KBUILD_BUILD_VERSION=1
export KBUILD_BUILD_USER=build-user
export KBUILD_BUILD_HOST=build-host
export KBUILD_BUILD_TIMESTAMP="Sun Mar 5 22:34:08 UTC 2023"

echo "=== [0] spoof settings ==="
echo "  VERSION=$KBUILD_BUILD_VERSION USER=$KBUILD_BUILD_USER HOST=$KBUILD_BUILD_HOST"
echo "  TIMESTAMP=$KBUILD_BUILD_TIMESTAMP"

echo "=== [1] confirm config_data now embeds the stock config ==="
grep -n -A1 "config_data:" "$K/kernel/Makefile" | head -4
rm -f "$O/kernel/config_data" "$O/kernel/config_data.gz" "$O/kernel/configs.o"

echo "=== [2] rebuild version.o + configs.o + relink ($(date)) ==="
rm -f "$O/include/generated/compile.h" "$O/include/generated/utsrelease.h" \
      "$O/init/version.o" "$O/.version"
echo 1 > "$O/.version"

make -C "$K" O="$O" -j32 KSU_VERSION=40900 Image 2>&1 | tail -20
rc=$?
echo "=== [3] rc=$rc ==="

echo "=== [4] verify the spoofed UTS string ==="
strings "$O/vmlinux" | grep -m1 "Linux version 5.10.110"
echo "--- expected: (build-user@build-host) ... #1 SMP PREEMPT Sun Mar 5 22:34:08 UTC 2023"

echo "=== [5] verify embedded config has no KSU ==="
echo "  KSU lines: $(zcat $O/kernel/config_data.gz 2>/dev/null | grep -cE 'KSU|SUSFS')"
zcat "$O/kernel/config_data.gz" 2>/dev/null | grep -E "KSU|SUSFS" || echo "  (none except checksum false positive)"

echo "=== [6] KSU/SuSFS still compiled in? ==="
nm "$O/vmlinux" | grep -cE " (T|t|D|d|B|b) (ksu_|susfs_|kernelsu_)"
exit $rc
