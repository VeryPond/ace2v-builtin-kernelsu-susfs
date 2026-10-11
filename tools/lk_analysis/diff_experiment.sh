#!/bin/bash
# 复现 LK 证书校验绕过的差分实验。
# 改动点选在 lk_main_dtb 内 DTB+0x30 的 8 个零字节（惰性、在 data 区）。
#
# 依赖: pwnage24mtk 的 parse-part-img.py / sign_mtk_cert.py / build-part-img.py
set -e

SRC=${1:?用法: diff_experiment.sh <lk_a.img> <pwnage24mtk 目录>}
TOOLS=${2:?}
OUT=lk_diff_out

echo "=== [0] 准备 ==="
rm -rf "$OUT" && mkdir -p "$OUT"
python3 "$TOOLS/parse-part-img.py" "$SRC" --split -o "$OUT/split"
ls -la "$OUT/split"

DTB="$OUT/split/lk_main_dtb.bin"
echo "=== [1] 基线哈希 ==="
sha256sum "$SRC" "$DTB"

# 容器内子镜像数据从 0x200 开始；DTB 数据区起点之后 0x30 处
echo
echo "--- 手工步骤提示 ---"
echo "1) 复制 lk_main_dtb.bin 为两个副本"
echo "2) 两个副本都在 DTB 数据偏移 +0x30 处翻转一个零字节（惰性）"
echo "   plain : 不注入"
echo "   legacy: python sign_mtk_cert.py <副本> -w --legacy -o ..."
echo "3) 分别回填:"
echo "   python build-part-img.py replace $SRC --name lk_main_dtb --file <副本> -o out.img"
echo
echo "=== [2] 预期结果 ==="
echo "   plain  注入 无     -> 不亮机（证明校验在执行）"
echo "   legacy 注入 legacy -> 开机（证明哈希被顶替）"
echo
echo "=== [3] 回滚 ==="
echo "   实验后用原始 lk_a.img 刷回，恢复出厂校验状态"
