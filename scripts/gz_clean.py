#!/usr/bin/env python3
import zlib
import struct
import sys


def gz_pure(raw, level=9):
    co = zlib.compressobj(level, zlib.DEFLATED, -zlib.MAX_WBITS, 9)
    body = co.compress(raw) + co.flush()
    hdr = b"\x1f\x8b\x08\x00" + struct.pack("<I", 0) + b"\x02\x03"
    crc = zlib.crc32(raw) & 0xffffffff
    isz = len(raw) & 0xffffffff
    return hdr + body + struct.pack("<II", crc, isz)


src = sys.argv[1] if len(sys.argv) > 1 else "/root/op/kout/arch/arm64/boot/Image"
dst = sys.argv[2] if len(sys.argv) > 2 else "/root/op/kout/arch/arm64/boot/Image.gz"
raw = open(src, "rb").read()
out = gz_pure(raw, 9)
open(dst, "wb").write(out)
print(f"src={len(raw)} gz={len(out)} head={out[:10].hex(' ')}")
import gzip as _gz
print(f"roundtrip ok: {_gz.decompress(out) == raw}")

PAGE = 4096
sb = open("/root/op/boot_a_readback.img", "rb").read()
ks = struct.unpack_from("<I", sb, 8)[0]
sk = sb[PAGE:PAGE + ks]
print(f"stock gz size={len(sk)} head={sk[:10].hex(' ')}")
