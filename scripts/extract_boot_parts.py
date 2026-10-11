#!/usr/bin/env python3
import struct, sys

try:
    import lz4.block
except ImportError:
    print("need lz4: pip3 install --break-system-packages lz4")
    sys.exit(1)

PAGE = 4096
MAXB = 8 * 1024 * 1024


def lz4_legacy(d):
    out = bytearray()
    off = 4
    while off < len(d):
        sz = struct.unpack_from("<I", d, off)[0]
        off += 4
        out += lz4.block.decompress(d[off:off + sz], uncompressed_size=MAXB)
        off += sz
    return bytes(out)


def split(path):
    b = open(path, "rb").read()
    ks, rs = struct.unpack_from("<II", b, 8)
    k = b[PAGE:PAGE + ks]
    roff = PAGE + ((ks + PAGE - 1) // PAGE) * PAGE
    r = b[roff:roff + rs]
    return k, r


k, r = split("/root/op/boot_a_readback.img")
open("/tmp/boot_kernel.gz", "wb").write(k)
open("/tmp/boot_ramdisk.lz4", "wb").write(r)
open("/tmp/boot_ramdisk.cpio", "wb").write(lz4_legacy(r))
print(f"boot kernel={len(k)} ramdisk={len(r)}")

# also vendor_boot ramdisk section (useful for later)
b = open("/root/op/vendor_boot_stock.img", "rb").read()
vr = struct.unpack_from("<I", b, 24)[0]
vrd = b[PAGE:PAGE + vr]
open("/tmp/vendor_ramdisk.lz4", "wb").write(vrd)
try:
    open("/tmp/vendor_ramdisk.cpio", "wb").write(lz4_legacy(vrd))
    print(f"vendor ramdisk={len(vrd)}")
except Exception as e:
    print("vendor ramdisk decompress failed:", e)
