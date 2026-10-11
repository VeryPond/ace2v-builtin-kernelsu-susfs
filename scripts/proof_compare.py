#!/usr/bin/env python3
"""Prove what actually differs between the previously-booted image and this one."""
import gzip
import hashlib
import struct

PAGE = 4096


def parts(path):
    b = open(path, "rb").read()
    ks, rs = struct.unpack_from("<II", b, 8)
    k = b[PAGE:PAGE + ks]
    roff = PAGE + ((ks + PAGE - 1) // PAGE) * PAGE
    r = b[roff:roff + rs]
    return k, r


prev = "/root/autodl-tmp/op/boot_prev.img"
now = "/root/autodl-tmp/op/boot_builtin_susfs.img"

ok = open("/root/autodl-tmp/op/boot_a_readback.img", "rb").read()

for tag, p in (("PREV (booted)", prev), ("NOW  (flashed)", now)):
    k, r = parts(p)
    img = gzip.decompress(k)
    print(f"{tag}: kernel_gz={len(k)} image={len(img)} "
          f"img_sha256={hashlib.sha256(img).hexdigest()[:16]} "
          f"ramdisk={len(r)} ram_sha256={hashlib.sha256(r).hexdigest()[:16]}")

k_prev, r_prev = parts(prev)
k_now, r_now = parts(now)
img_prev = gzip.decompress(k_prev)
img_now = gzip.decompress(k_now)

print()
print(f"kernel gz identical?   {k_prev == k_now}")
print(f"kernel raw identical?  {img_prev == img_now}")
print(f"ramdisk identical?     {r_prev == r_now}")

if img_prev != img_now:
    diff = sum(1 for a, b in zip(img_prev, img_now) if a != b)
    print(f"kernel raw differing bytes: {diff} / {len(img_prev)}")
    # where do they differ
    first = next(i for i, (a, b) in enumerate(zip(img_prev, img_now)) if a != b)
    print(f"first difference at offset 0x{first:x}")

# Show the version strings embedded in each
def ver(img):
    out = []
    for m in (b"5.10.110-android12-9-g4d2e7c69e8b4", b"40900", b"13000",
              b"SUSFS_VERSION", b"v2.3.0"):
        if m in img:
            out.append(m.decode())
    return out


print()
print("markers in PREV kernel:", ver(img_prev))
print("markers in NOW  kernel:", ver(img_now))
