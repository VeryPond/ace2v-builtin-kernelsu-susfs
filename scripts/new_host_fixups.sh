#!/bin/bash
set -e
OP=/root/autodl-tmp/op
K=$OP/kernel

echo "=== [1] restore the hand-fixed fdinfo.c ==="
cd "$K"
base64 -d /root/autodl-tmp/op/fdinfo_fixed.b64 > fs/notify/fdinfo.c
rm -f fs/notify/fdinfo.c.rej
echo "  bytes: $(wc -c < fs/notify/fdinfo.c)"
grep -c "SUSFS" fs/notify/fdinfo.c

echo "=== [2] add VMA_PAD_START compat (MTK 5.10 has no vm_pad) ==="
F="$K/include/linux/susfs_def.h"
if grep -q "SUSFS_VMA_PAD_COMPAT" "$F"; then
  echo "  already present"
else
  printf '\n/* SUSFS_VMA_PAD_COMPAT: MTK 5.10 has no vma padding (vm_pad). */\n' >> "$F"
  printf '#ifndef VMA_PAD_START\n#define VMA_PAD_START(vma) ((vma)->vm_start)\n#endif\n' >> "$F"
  echo "  appended"
fi
tail -5 "$F"

echo "=== [3] verify no rejects remain ==="
find "$K" -name "*.rej" | head
echo "  reject count: $(find $K -name '*.rej' | wc -l)"

echo "=== [4] confirm VMA_PAD_START resolves ==="
grep -n "VMA_PAD_START" "$F"
