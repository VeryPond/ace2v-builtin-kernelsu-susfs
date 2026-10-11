#!/usr/bin/env python3
"""Repack boot the SAME way as the known-good kernelsu_patched.img:
keep the ORIGINAL signed AVB vbmeta blob verbatim, relocate it to the new
content end, and rewrite the footer. No avbtool, no algorithm NONE."""
import gzip
import hashlib
import struct

PAGE = 4096
PART = 67108864
STOCK = "/root/op/boot_a_readback.img"
GOOD = "/root/op/kernelsu_patched.img"   # known-good: modified ramdisk, booted
OURIMG = "/root/op/kout/arch/arm64/boot/Image.gz"
OUT = "/root/op/boot_builtin_susfs.img"


def align(x):
    return (x + PAGE - 1) // PAGE * PAGE


stock = open(STOCK, "rb").read()
kernel = open(OURIMG, "rb").read()

# --- take the stock ramdisk verbatim ---
ks, rs = struct.unpack_from("<II", stock, 8)
roff = PAGE + align(ks)
stock_ramdisk = stock[roff:roff + rs]

# --- locate the stock AVB vbmeta blob via the footer ---
ftr = stock[-64:]
assert ftr[:4] == b"AVBf", "no AVB footer in stock"
# AVB integer fields are BIG-ENDIAN
orig_size, vb_off, vb_size = struct.unpack_from(">QQQ", ftr, 12)
vbmeta = stock[vb_off:vb_off + vb_size]
print(f"stock footer: orig={orig_size} vbmeta_off={vb_off} vbmeta_size={vb_size}")
print(f"stock vbmeta head: {vbmeta[:8].hex(' ')}")
assert vbmeta[:4] == b"AVB0", "stock vbmeta magic missing"

# --- build new content ---
header = bytearray(stock[:PAGE])
content = bytearray()
content += header
content += kernel
content += b"\x00" * (align(len(kernel)) - len(kernel))
content += stock_ramdisk
content += b"\x00" * (align(len(stock_ramdisk)) - len(stock_ramdisk))
struct.pack_into("<I", content, 8, len(kernel))
struct.pack_into("<I", content, 12, len(stock_ramdisk))
content_end = len(content)
print(f"new content_end = {content_end} (0x{content_end:x})")

# --- assemble: content + relocated original vbmeta + pad + footer ---
out = bytearray(content)
assert len(out) == content_end
out += vbmeta                       # verbatim signed struct, just moved
vb_new_off = content_end
out += b"\x00" * (PART - 64 - len(out))

footer = bytearray(64)
footer[0:4] = b"AVBf"
struct.pack_into(">I", footer, 4, 1)       # version_major
struct.pack_into(">I", footer, 8, 0)       # version_minor
struct.pack_into(">Q", footer, 12, content_end)   # original_image_size
struct.pack_into(">Q", footer, 20, vb_new_off)    # vbmeta_offset
struct.pack_into(">Q", footer, 28, len(vbmeta))   # vbmeta_size
out += footer
assert len(out) == PART

open(OUT, "wb").write(out)
print(f"OUT {OUT} size={len(out)} sha256={hashlib.sha256(out).hexdigest()}")

# --- sanity vs the known-good image's footer style ---
g = open(GOOD, "rb").read()
gf = g[-64:]
go, gv, gs = struct.unpack_from(">QQQ", gf, 12)
print(f"known-good footer: orig={go} vbmeta_off={gv} vbmeta_size={gs} "
      f"magic={gf[:4]}")
print(f"ours footer     : orig={content_end} vbmeta_off={vb_new_off} "
      f"vbmeta_size={len(vbmeta)} magic={footer[:4]}")
