#!/usr/bin/env python3
"""Prove KSU+SuSFS are genuinely compiled in: compare vs the STOCK kernel."""
import gzip
import hashlib
import struct

PAGE = 4096


def load(path):
    b = open(path, "rb").read()
    ks = struct.unpack_from("<I", b, 8)[0]
    return gzip.decompress(b[PAGE:PAGE + ks])


stock = load("/root/autodl-tmp/op/boot_a_readback.img")
ours = load("/root/autodl-tmp/op/boot_builtin_susfs.img")

print(f"STOCK kernel Image : {len(stock):>10} bytes  "
      f"sha256={hashlib.sha256(stock).hexdigest()[:16]}")
print(f"OURS  kernel Image : {len(ours):>10} bytes  "
      f"sha256={hashlib.sha256(ours).hexdigest()[:16]}")
print(f"size delta         : {len(ours)-len(stock):+d}")
print()

markers = {
    "KernelSU init":      b"kernelsu_init",
    "SuSFS init":         b"susfs_init",
    "SuSFS version":      b"SUSFS_VERSION",
    "SuSFS string":       b"susfs",
    "KSU supercall":      b"ksu_handle_execveat",
    "KSU ksu_cred":       b"ksu_cred",
    "SuSFS sus_path":     b"sus_path",
    "SuSFS sus_mount":    b"sus_mount",
    "SuSFS open_redirect":b"open_redirect",
    "ksud path":          b"/data/adb/ksud",
    "SukiSU tag":         b"SukiSU",
}
print(f"{'marker':22s} {'STOCK':>8s} {'OURS':>8s}")
print("-" * 42)
for name, m in markers.items():
    print(f"{name:22s} {stock.count(m):>8d} {ours.count(m):>8d}")

print()
print(f"total differing bytes vs stock: "
      f"{sum(1 for a,b in zip(stock,ours) if a!=b)}")
