#!/bin/bash
set -e
OP=/root/autodl-tmp/op
K=$OP/kernel

echo "=== [1] put the STOCK config into the tree as a defconfig ==="
cp "$OP/device_config" "$K/arch/arm64/configs/stock_defconfig"
wc -l "$K/arch/arm64/configs/stock_defconfig"
echo "  KSU lines in stock defconfig: $(grep -cE '^CONFIG_KSU|^# CONFIG_KSU' $K/arch/arm64/configs/stock_defconfig)"

echo "=== [2] point config_data at stock_defconfig ==="
MF="$K/kernel/Makefile"
if grep -q "stock_defconfig" "$MF"; then
  echo "  already patched"
else
  # replace only the config_data rule's prerequisite
  sed -i 's|^\$(obj)/config_data: \$(KCONFIG_CONFIG) FORCE$|$(obj)/config_data: arch/arm64/configs/stock_defconfig FORCE|' "$MF"
  echo "  patched"
fi
grep -n -A2 "config_data:" "$MF" | head -12

echo "=== [3] remember original KCONFIG_CONFIG value for reference ==="
grep -n "KCONFIG_CONFIG" "$K/kernel/Makefile" | head

echo "=== [4] sanity: stock_defconfig must have NO KSU/SUSFS ==="
grep -nE "KSU|SUSFS" "$K/arch/arm64/configs/stock_defconfig" || echo "  clean (only the XT_TARGET_CHECKSUM false positive may appear)"
grep -E "KSU|SUSFS" "$K/arch/arm64/configs/stock_defconfig" | grep -v CHECKSUM || echo "  CONFIRMED: zero KSU/SUSFS entries"
