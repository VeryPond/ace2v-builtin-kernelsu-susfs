#!/bin/bash
set -e
OP=/root/autodl-tmp/op
SRC=$OP/AnyKernel3
STAGE=$OP/ak3_stage
OUTZIP=$OP/SukiSU_SuSFS_Ace2V_AK3.zip

echo "=== [1] stage ==="
rm -rf $STAGE $OUTZIP
mkdir -p $STAGE
cp -a $SRC/tools $STAGE/tools
cp -a $SRC/META-INF $STAGE/META-INF
cp $OP/anykernel.sh $STAGE/anykernel.sh

echo "=== [2] the prebuilt boot image must be named boot.img ==="
cp $OP/boot_builtin_susfs.img $STAGE/boot.img
ls -la $STAGE
echo "  sha256:"; sha256sum $STAGE/boot.img

echo "=== [3] version banner ==="
cat > $STAGE/version <<'EOF'
Kernel : 5.10.110-android12-9 (MTK6983 / OnePlus Ace 2V)
         SukiSU-Ultra builtin  (no kernelsu.ko, zero module)
         SuSFS v2.3.0
Config : stock-aligned LTO_CLANG_FULL + CFI_CLANG + KASAN_HW_TAGS + SHADOW_CALL_STACK
Mode   : flashes a complete boot image, stock ramdisk preserved
EOF

echo "=== [4] permissions ==="
chmod -R 755 $STAGE/tools
chmod 755 $STAGE/META-INF/com/google/android/update-binary

echo "=== [5] zip ==="
( cd $STAGE && zip -r9 -q $OUTZIP . -x '.*' )
ls -la $OUTZIP
sha256sum $OUTZIP
echo
echo "=== [6] contents ==="
unzip -l $OUTZIP | head -30
