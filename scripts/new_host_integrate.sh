#!/bin/bash
set -e
OP=/root/autodl-tmp/op
K=$OP/kernel
S=$OP/susfs510
SU=$OP/sukisu
M=$OP/modules

echo "=== [1] reset kernel tree ==="
cd "$K"
git checkout -- . 2>/dev/null || true
git clean -fdq 2>/dev/null || true

echo "=== [2] merge oplus vendor sources (modules repo) as sibling 'vendor' ==="
rm -rf "$OP/vendor"
mkdir -p "$OP/vendor"
cp -a "$M/vendor/." "$OP/vendor/"
echo "vendor: $(ls $OP/vendor)"

echo "=== [3] merge oplus_cpu into kernel/kernel ==="
rm -rf "$K/kernel/oplus_cpu"
cp -a "$M/vendor/oplus/kernel/cpu" "$K/kernel/oplus_cpu"
echo "oplus_cpu: $(ls $K/kernel/oplus_cpu | tr '\n' ' ')"

echo "=== [4] copy susfs kernel files ==="
cp "$S/kernel_patches/fs/susfs.c" "$K/fs/susfs.c"
cp "$S/kernel_patches/include/linux/susfs.h" "$K/include/linux/susfs.h"
cp "$S/kernel_patches/include/linux/susfs_def.h" "$K/include/linux/susfs_def.h"

echo "=== [5] apply 50_ susfs kernel patch ==="
patch -p1 --forward --no-backup-if-mismatch < \
  "$S/kernel_patches/50_add_susfs_in_gki-android12-5.10.patch" \
  > /tmp/p50.log 2>&1 || true
grep -iE "FAILED|Reversed" /tmp/p50.log || echo "  (no failures)"
echo "  rejects: $(find . -name '*.rej' | wc -l)"

echo "=== [6] install KernelSU (builtin branch) ==="
cd "$SU"
git fetch -q --depth 1 origin builtin 2>/dev/null || true
git checkout -q FETCH_HEAD 2>/dev/null || git checkout -q origin/builtin 2>/dev/null || true
git log -1 --oneline

echo "=== [7] place KernelSU in kernel tree ==="
cd "$K"
rm -rf KernelSU
mkdir -p KernelSU
cp -a "$SU/kernel/." KernelSU/
rm -rf KernelSU/.git
rm -f drivers/kernelsu
ln -sf ../KernelSU drivers/kernelsu
grep -q "CONFIG_KSU" drivers/Makefile || printf '\nobj-$(CONFIG_KSU) += kernelsu/\n' >> drivers/Makefile
grep -q 'drivers/kernelsu/Kconfig' drivers/Kconfig || sed -i '/^endmenu/i source "drivers/kernelsu/Kconfig"' drivers/Kconfig
echo "  linked: $(ls -la drivers/kernelsu | awk '{print $NF}')"

echo "=== [8] neutralise KernelSU Makefile network calls ==="
MF="$K/KernelSU/Makefile"
sed -i 's|^\$(shell cd \$(KSU_SRC) 2>/dev/null && \[ -f ../.git/shallow \] && \$(GIT_BIN) fetch --unshallow 2>/dev/null)|# offline|' "$MF" || true
sed -i 's|^CURL_BIN.*|CURL_BIN := true|' "$MF" || true
sed -i 's|^KSU_GITHUB_VER.*|KSU_GITHUB_VER := |' "$MF" || true
sed -i 's|^GITHUB_COMMITS.*|GITHUB_COMMITS := |' "$MF" || true
grep -n "unshallow\|CURL_BIN\|KSU_GITHUB" "$MF" | head

echo "=== [9] status ==="
git status --short | wc -l
ls -la fs/susfs.c include/linux/susfs.h KernelSU/Kconfig
