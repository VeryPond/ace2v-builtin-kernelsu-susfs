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

echo "=== [0] toolchain sanity ==="
which clang ld.lld llvm-nm llvm-ar
nm --version | head -1
ar --version | head -1

echo "=== [1] seed config from device /proc/config.gz ==="
mkdir -p "$O"
cp "$OP/device_config" "$O/.config"
cat "$OP/ksu_susfs.config" >> "$O/.config"
sed -i 's/^CONFIG_LOCALVERSION=.*/CONFIG_LOCALVERSION="-android12-9-g4d2e7c69e8b4"/' "$O/.config"
sed -i 's/^CONFIG_LOCALVERSION_AUTO=.*/# CONFIG_LOCALVERSION_AUTO is not set/' "$O/.config"

echo "=== [2] strip auto '+' suffix ==="
python3 "$OP/strip_plus.py"
grep -n 'scm:++' "$K/scripts/setlocalversion" || echo "  '+' marker removed"

echo "=== [3] olddefconfig ==="
make -C "$K" O="$O" olddefconfig > /tmp/cfg.log 2>&1
tail -3 /tmp/cfg.log

echo "=== [4] verify critical config ==="
for o in CONFIG_KSU CONFIG_KSU_SUSFS CONFIG_KSU_SUSFS_SUS_PATH CONFIG_KSU_SUSFS_SUS_MOUNT CONFIG_KSU_SUSFS_SUS_KSTAT CONFIG_KSU_SUSFS_SUS_MAP CONFIG_KSU_SUSFS_OPEN_REDIRECT CONFIG_KSU_SUSFS_HIDE_KSU_SUSFS_SYMBOLS CONFIG_LTO_CLANG_FULL CONFIG_CFI_CLANG CONFIG_KASAN_HW_TAGS CONFIG_SHADOW_CALL_STACK CONFIG_MODVERSIONS CONFIG_LOCALVERSION; do
  printf "  %-44s " "$o"
  grep "^$o=" "$O/.config" || grep "^# $o is not set" "$O/.config" || echo MISSING
done

echo "=== [5] build Image (KSU_VERSION=40900) $(date) ==="
make -C "$K" O="$O" -j32 KSU_VERSION=40900 Image 2>&1
rc=$?
echo "=== [6] rc=$rc $(date) ==="
ls -la "$O/arch/arm64/boot/Image"
strings "$O/vmlinux" | grep -m1 "5.10.110"
nm "$O/vmlinux" | grep -E " (T|t) (kernelsu_init|susfs_init)$"
exit $rc
