#!/usr/bin/env python3
import gzip, hashlib, struct, subprocess, sys

PAGE = 4096
PART = 67108864
STOCK = "/root/op/boot_a_readback.img"
NEW = "/root/op/boot_builtin_susfs.img"
OURIMG = "/root/op/kout/arch/arm64/boot/Image"


def align(x):
    return (x + PAGE - 1) // PAGE * PAGE


ok = True


def check(cond, msg):
    global ok
    print(("  PASS  " if cond else "  FAIL  ") + msg)
    if not cond:
        ok = False


sb = open(STOCK, "rb").read()
nb = open(NEW, "rb").read()
ourimg = open(OURIMG, "rb").read()

print("=== size / header ===")
check(len(nb) == PART, f"size == {PART}")
check(nb[:8] == b"ANDROID!", "ANDROID! magic")
nks, nrs, nosv, nhs, nhv = struct.unpack_from("<IIIII", nb, 8)
sks, srs, sosv, shs, shv = struct.unpack_from("<IIIII", sb, 8)
print(f"    stock: ks={sks} rs={srs} osv=0x{sosv:08x} hs={shs} hv={shv}")
print(f"    new  : ks={nks} rs={nrs} osv=0x{nosv:08x} hs={nhs} hv={nhv}")
check(nosv == sosv and nhs == shs and nhv == shv,
      "header fields (os_version/header_size/header_version) match stock")
check(nb[:PAGE] != b"", "header present")
# non-size fields of header identical
hdr_s, hdr_n = bytearray(sb[:PAGE]), bytearray(nb[:PAGE])
struct.pack_into("<I", hdr_s, 8, 0); struct.pack_into("<I", hdr_s, 12, 0)
struct.pack_into("<I", hdr_n, 8, 0); struct.pack_into("<I", hdr_n, 12, 0)
check(bytes(hdr_s) == bytes(hdr_n), "all header bytes except sizes identical")

print("=== kernel ===")
k = nb[PAGE:PAGE + nks]
check(k[:2] == b"\x1f\x8b", "kernel is gzip")
d = gzip.decompress(k)
check(d == ourimg, f"gunzip(kernel) == our built Image ({len(d)} bytes)")
stockimg = gzip.decompress(sb[PAGE:PAGE + sks])
check(d[:4] == stockimg[:4] == b"\x4d\x5a\x00\x91",
      "kernel begins like a valid ARM64 Image")
print(f"    our Image {len(d)} vs stock Image {len(stockimg)} "
      f"({len(d)-len(stockimg):+d})")

print("=== ramdisk ===")
roff_n = PAGE + align(nks)
r = nb[roff_n:roff_n + nrs]
roff_s = PAGE + align(sks)
rsd = sb[roff_s:roff_s + srs]
check(r == rsd, "ramdisk is BYTE-IDENTICAL to stock (unchanged)")

print("=== padding ===")
content_end = roff_n + align(nrs)
tail = nb[content_end:]
print(f"    content_end=0x{content_end:x}, tail={len(tail)}")
print(f"    tail[:4]={tail[:4]}")

print("=== AVB ===")
r1 = subprocess.run(["python3", "/root/op/avbtool.py", "verify_image",
                     "--image", NEW], capture_output=True, text=True)
print("    " + (r1.stdout + r1.stderr).strip().splitlines()[0] if
      (r1.stdout + r1.stderr).strip() else "    (no output)")
r2 = subprocess.run(["python3", "/root/op/avbtool.py", "info_image",
                     "--image", NEW], capture_output=True, text=True)
for line in r2.stdout.strip().splitlines()[:12]:
    print("    " + line)

print("=== sha256 ===")
print(f"    NEW : {hashlib.sha256(nb).hexdigest()}")
print(f"    STOCK: {hashlib.sha256(sb).hexdigest()}")

print()
print("RESULT:", "ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED")
sys.exit(0 if ok else 1)
