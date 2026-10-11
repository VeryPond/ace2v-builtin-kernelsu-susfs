#!/usr/bin/env python3
import gzip, struct, subprocess

STOCK_BOOT = "/root/op/boot_a_readback.img"
OUR_GZ = "/root/op/kout/arch/arm64/boot/Image.gz"
OUR_RAW = "/root/op/kout/arch/arm64/boot/Image"
PAGE = 4096


def hdr(name, img):
    print(f"--- {name}  ({len(img)} bytes) ---")
    code0, code1 = struct.unpack_from("<II", img, 0)
    text_off, image_size, flags = struct.unpack_from("<QQQ", img, 8)
    res2, res3, res4 = struct.unpack_from("<QQQ", img, 32)
    magic, res5 = struct.unpack_from("<II", img, 56)
    print(f"  code0      = 0x{code0:08x}")
    print(f"  code1      = 0x{code1:08x}")
    print(f"  text_offset= 0x{text_off:x}")
    print(f"  image_size = 0x{image_size:x}  ({image_size})")
    print(f"  flags      = 0x{flags:x}")
    print(f"  res2/3/4   = {res2:#x}/{res3:#x}/{res4:#x}")
    print(f"  magic      = 0x{magic:08x}  "
          f"({'ARM64 OK' if magic == 0x644d5241 else 'NOT 0x644d5241!'})")
    print(f"  res5       = 0x{res5:x}")
    print(f"  file size  = {len(img)}  "
          f"({'>= image_size OK' if len(img) >= image_size else 'SMALLER than image_size!'})")
    return image_size


sb = open(STOCK_BOOT, "rb").read()
ks = struct.unpack_from("<I", sb, 8)[0]
stock_img = gzip.decompress(sb[PAGE:PAGE + ks])
si = hdr("STOCK decompressed Image", stock_img)

our = open(OUR_RAW, "rb").read()
oi = hdr("OUR built Image", our)

print()
print(f"image_size delta: ours - stock = {oi - si} ({oi-si:+d})")
print(f"raw     delta: ours - stock = {len(our)-len(stock_img)}")

print()
print("=== gzip header bytes ===")
print(f"  stock : {sb[PAGE:PAGE+10].hex()}")
gz = open(OUR_GZ, "rb").read()
print(f"  ours  : {gz[:10].hex()}")
print(f"  ours gz size = {len(gz)}")

print()
print("=== did the build also produce dtb / dtbo images? ===")
for p in ["/root/op/kout/arch/arm64/boot/dts/mediatek/oplus6983_22823.dtb",
          "/root/op/kout/arch/arm64/boot/dtb.img",
          "/root/op/kout/arch/arm64/boot/dtbo.img",
          "/root/op/kout/arch/arm64/boot/Image.gz-dtb"]:
    r = subprocess.run(["ls", "-la", p], capture_output=True, text=True)
    print("  " + (r.stdout.strip() if r.returncode == 0 else f"(absent) {p}"))

print()
print("=== KSU initcall level (builtin branch) ===")
print(subprocess.run(
    ["grep", "-n", "kernelsu_init\\|module_init\\|core_initcall\\|late_initcall",
     "/root/op/kernel/KernelSU/ksu.c"],
    capture_output=True, text=True).stdout)
