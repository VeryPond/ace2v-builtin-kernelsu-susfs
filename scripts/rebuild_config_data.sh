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

echo "=== [1] force regenerate config_data from stock_defconfig ==="
rm -f "$O/kernel/config_data" "$O/kernel/config_data.gz" "$O/kernel/configs.o"
make -C "$K" O="$O" kernel/configs.o 2>&1 | tail -8 || true

echo "=== [2] inspect the embedded config_data ==="
ls -la "$O/kernel/config_data" "$O/kernel/config_data.gz" 2>&1
echo "  KSU lines embedded: $(zcat $O/kernel/config_data.gz 2>/dev/null | grep -cE 'KSU|SUSFS' || echo '?')"
echo "  XT_TARGET_CHECKSUM line (expected false positive):"
zcat "$O/kernel/config_data.gz" 2>/dev/null | grep -E "KSU|SUSFS" || echo "    (none)"

echo "=== [3] full relink ==="
make -C "$K" O="$O" -j32 KSU_VERSION=40900 Image 2>&1 | tail -12

echo "=== [4] verify ==="
ls -la "$O/arch/arm64/boot/Image"
strings "$O/vmlinux" | grep -m1 "5.10.110"
