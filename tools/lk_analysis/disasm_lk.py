#!/usr/bin/env python3
"""Locate the MTK certificate parsing / xref sites in a preloader / LK image.

Usage:
    pip install capstone
    python disasm_lk.py BOOT_1.img --base 0x11e56000 --find-strings
    python disasm_lk.py BOOT_1.img --base 0x11e56000 --around 0x696b8

Notes
-----
* Cs.disasm() STOPS at the first undecodable byte. Always pass skipdata=True,
  otherwise a whole linear sweep silently yields nothing.
* The certificate parser is dispatched through a function-pointer table in
  .rodata, so it has no direct BL caller. Search for the instruction bytes
  instead of relying on xrefs.
"""
import argparse
import struct
import sys

try:
    from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN
except ImportError:
    print("需要 capstone:  pip install capstone")
    sys.exit(1)


MARKERS = {
    "MKIMG magic": 0x58881688,
    "ext_magic": 0x58891689,
}

# Interesting string anchors seen in this firmware's preloader.
STRINGS = [
    b"cert img_hdr_type",
    b"img auth ok",
    b"dump (imghdr + image) hash",
    b"sec_level",
    b"2.16.886.2454.2.4",
    b"2.16.886.2454.2.1",
]


def find_magic(data):
    print("== 32-bit magic 出现位置 ==")
    for name, val in MARKERS.items():
        pat = struct.pack("<I", val)
        offs, start = [], 0
        while True:
            i = data.find(pat, start)
            if i < 0:
                break
            offs.append(i)
            start = i + 1
        print(f"  {name} (0x{val:08x}): {len(offs)} 处")
        for o in offs[:8]:
            print(f"    0x{o:x}")


def find_strings(data):
    print("== 关键字符串 ==")
    for s in STRINGS:
        i = data.find(s)
        print(f"  {s.decode('latin1'):32s} {'0x%x' % i if i >= 0 else 'not found'}")


def disasm(data, base, start, count):
    md = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN)
    md.skipdata = True          # <-- critical
    off = start
    shown = 0
    for insn in md.disasm(data[off:], base + off):
        print(f"  0x{insn.address:08x}: {insn.mnemonic:8s} {insn.op_str}")
        shown += 1
        if count and shown >= count:
            break


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--base", type=lambda x: int(x, 0), default=0)
    ap.add_argument("--around", type=lambda x: int(x, 0), default=0)
    ap.add_argument("--count", type=int, default=60)
    ap.add_argument("--find-strings", action="store_true")
    args = ap.parse_args()

    data = open(args.image, "rb").read()
    print(f"image: {args.image}  size={len(data)}  base=0x{args.base:x}")
    find_magic(data)
    if args.find_strings:
        find_strings(data)
    if args.around:
        off = args.around - args.base
        print(f"== 反汇编 0x{args.around:x} 起 ==")
        disasm(data, args.base, off, args.count)


if __name__ == "__main__":
    main()
