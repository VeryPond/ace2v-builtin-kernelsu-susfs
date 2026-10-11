#!/usr/bin/env python3
"""Compare stock vendor module symbol CRCs against the freshly built kernel.

Kernel built with CONFIG_MODVERSIONS=y. On module load, the kernel compares
the __versions CRCs recorded in the .ko against its own __crc_* symbols.
If they all match, the module loads regardless of the vermagic version string.
"""
import glob
import struct
import subprocess
import sys

from elftools.elf.elffile import ELFFile

VMLINUX = "/root/op/kout/vmlinux"
MODS = sorted(glob.glob("/root/op/stockmods/*.ko"))


def kernel_crcs():
    out = subprocess.check_output(["nm", VMLINUX], text=True, errors="replace")
    crcs = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[2].startswith("__crc_"):
            try:
                crcs[parts[2][len("__crc_"):]] = int(parts[0], 16) & 0xFFFFFFFF
            except ValueError:
                pass
    return crcs


def section_data(elf, name):
    for sec in elf.iter_sections():
        if sec.name == name:
            return sec.data()
    return None


def sym_strings(elf):
    for sec in elf.iter_sections():
        if sec.name == "__versions":
            strtab = elf.get_section(sec["sh_link"])
            data = sec.data()
            entsize = 64
            for off in range(0, len(data), entsize):
                chunk = data[off:off + entsize]
                if len(chunk) < 64:
                    continue
                # struct modversion_info { unsigned long crc; char name[MODULE_NAME_LEN=56]; }
                crc = struct.unpack_from("<Q", chunk, 0)[0] & 0xFFFFFFFF
                name = chunk[8:64].split(b"\x00")[0].decode("ascii", "replace")
                yield name, crc
            return


def main():
    kcrc = kernel_crcs()
    print(f"[kernel] exported crc symbols: {len(kcrc)}")
    overall_ok = True
    for mod in MODS:
        with open(mod, "rb") as fh:
            elf = ELFFile(fh)
            vermagic = "?"
            for sec in elf.iter_sections():
                if sec.name == ".modinfo":
                    for line in sec.data().split(b"\x00"):
                        if line.startswith(b"vermagic="):
                            vermagic = line[9:].decode("ascii", "replace")
            want = list(sym_strings(elf))
            mismatch = []
            missing = []
            for name, crc in want:
                if name not in kcrc:
                    missing.append(name)
                elif kcrc[name] != crc:
                    mismatch.append((name, crc, kcrc[name]))
            status = "OK" if not mismatch and not missing else "FAIL"
            if status == "FAIL":
                overall_ok = False
            print(f"\n[{status}] {mod.split('/')[-1]}")
            print(f"   vermagic: {vermagic}")
            print(f"   versioned symbols: {len(want)}"
                  f"  mismatch: {len(mismatch)}  missing: {len(missing)}")
            for name, c, k in mismatch[:12]:
                print(f"     MISMATCH {name}: ko=0x{c:08x} kernel=0x{k:08x}")
            for name in missing[:12]:
                print(f"     MISSING  {name}")
    print("\n==== RESULT:", "ALL MODULES COMPATIBLE" if overall_ok
          else "ABI MISMATCH DETECTED", "====")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
