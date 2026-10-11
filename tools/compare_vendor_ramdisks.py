import hashlib
import lz4.block
import struct
from pathlib import Path


MAX_BLOCK = 8 * 1024 * 1024

ORIGINAL_CPIO = Path(r"E:\_probe_pwnage24mtk\vb_cpio_orig.bin")
PATCHED_IMAGE = Path(r"E:\_probe_pwnage24mtk\vendor_boot_a_patched_initfix.img")
ORIGINAL_IMAGE = Path(
    r"E:\GeekFlashTool_Readback_20261010230748790\vendor_boot_a.img"
)


def decompress_legacy(data: bytes) -> bytes:
    output = bytearray()
    offset = 4
    while offset < len(data):
        if offset + 4 > len(data):
            break
        size = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        if offset + size > len(data):
            break
        output += lz4.block.decompress(
            data[offset : offset + size], uncompressed_size=MAX_BLOCK
        )
        offset += size
    return bytes(output)


def ramdisk_from_vendor_boot(data: bytes) -> bytes:
    size = struct.unpack_from("<I", data, 24)[0]
    return data[4096 : 4096 + size]


def cpio_entries(cpio: bytes):
    entries = {}
    order = []
    offset = 0
    while offset + 110 <= len(cpio):
        if cpio[offset : offset + 6] not in (b"070701", b"070702"):
            break
        fields = [
            int(cpio[offset + 6 + i * 8 : offset + 14 + i * 8], 16)
            for i in range(13)
        ]
        name_size = fields[11]
        file_size = fields[6]
        name = cpio[offset + 110 : offset + 110 + name_size - 1].decode(
            "latin1", errors="replace"
        )
        data_start = (offset + 110 + name_size + 3) & ~3
        data = cpio[data_start : data_start + file_size]
        entries[name] = (fields[0], fields[1], file_size, data)
        order.append(name)
        if name == "TRAILER!!!":
            break
        offset = (data_start + file_size + 3) & ~3
    return entries, order


def main() -> None:
    original_cpio = ORIGINAL_CPIO.read_bytes()

    patched_raw = PATCHED_IMAGE.read_bytes()
    patched_cpio = decompress_legacy(
        ramdisk_from_vendor_boot(patched_raw)
    )

    original_entries, original_order = cpio_entries(original_cpio)
    patched_entries, patched_order = cpio_entries(patched_cpio)

    print(f"original entries: {len(original_entries)}")
    print(f"patched  entries: {len(patched_entries)}")
    print(f"order identical: {original_order == patched_order}")

    only_original = [n for n in original_order if n not in patched_entries]
    only_patched = [n for n in patched_order if n not in original_entries]
    print(f"only in original: {only_original}")
    print(f"only in patched : {only_patched}")

    changed = []
    for name in original_order:
        if name not in patched_entries:
            continue
        of, op, osz, odata = original_entries[name]
        pf, pp, psz, pdata = patched_entries[name]
        if odata != pdata or osz != psz or of != pf or op != pp:
            changed.append((name, osz, psz, of, pf, op, pp))

    print(f"\nchanged entries: {len(changed)}")
    for name, osz, psz, of, pf, op, pp in changed:
        print(
            f"  {name}: size {osz} -> {psz}, mode {oct(of)} -> {oct(pf)}, "
            f"perm {oct(op)} -> {oct(pp)}"
        )

    print("\ninit / kernelsu related entries (patched):")
    for name in patched_order:
        if (
            name.strip("/") in ("init", "init.real")
            or "kernelsu" in name.lower()
            or "ksu" in name.lower()
        ):
            fields0, fields1, size, data = patched_entries[name]
            print(
                f"  {name} size={size} mode={oct(fields0)} perm={oct(fields1)} "
                f"sha={hashlib.sha256(data).hexdigest()[:16]}"
            )

    print("\ninit / kernelsu related entries (original):")
    for name in original_order:
        if (
            name.strip("/") in ("init", "init.real")
            or "kernelsu" in name.lower()
            or "ksu" in name.lower()
        ):
            fields0, fields1, size, data = original_entries[name]
            print(
                f"  {name} size={size} mode={oct(fields0)} perm={oct(fields1)} "
                f"sha={hashlib.sha256(data).hexdigest()[:16]}"
            )

    original_raw = ORIGINAL_IMAGE.read_bytes()
    print(
        f"\noriginal header vendor_ramdisk_size: "
        f"0x{struct.unpack_from('<I', original_raw, 24)[0]:x}"
    )
    print(
        f"patched  header vendor_ramdisk_size: "
        f"0x{struct.unpack_from('<I', patched_raw, 24)[0]:x}"
    )
    print(
        f"original lz4 magic: "
        f"{struct.unpack_from('<I', ramdisk_from_vendor_boot(original_raw), 0)[0]:08x}"
    )
    print(
        f"patched  lz4 magic: "
        f"{struct.unpack_from('<I', ramdisk_from_vendor_boot(patched_raw), 0)[0]:08x}"
    )


if __name__ == "__main__":
    main()
