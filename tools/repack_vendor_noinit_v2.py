import hashlib
import lz4.block
import struct
from pathlib import Path


SRC_IMAGE = Path(r"E:\_probe_pwnage24mtk\vendor_boot_a_patched_initfix.img")
ORIGINAL_IMAGE = Path(
    r"E:\GeekFlashTool_Readback_20261010230748790\vendor_boot_a.img"
)
OUT_IMAGE = Path(r"E:\_probe_pwnage24mtk\vendor_boot_a_noinit_v2.img")

PAGE = 4096
MAX_BLOCK = 8 * 1024 * 1024


def decompress_legacy(data: bytes) -> bytes:
    output = bytearray()
    offset = 4
    while offset + 4 <= len(data):
        size = struct.unpack_from("<I", data, offset)[0]
        offset += 4
        if size == 0:
            break
        if offset + size > len(data):
            break
        output += lz4.block.decompress(
            data[offset : offset + size], uncompressed_size=MAX_BLOCK
        )
        offset += size
    return bytes(output)


def compress_legacy(data: bytes) -> bytes:
    output = bytearray(struct.pack("<I", 0x184C2102))
    for start in range(0, len(data), MAX_BLOCK):
        block = data[start : start + MAX_BLOCK]
        compressed = lz4.block.compress(
            block, mode="high_compression", compression=12, store_size=False
        )
        output += struct.pack("<I", len(compressed))
        output += compressed
    return bytes(output)


def align(value: int, alignment: int) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def strip_entry(cpio: bytes, target: str) -> tuple[bytes, int]:
    output = bytearray()
    removed = 0
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
        end = (data_start + file_size + 3) & ~3
        record = cpio[offset:end]
        if name == target:
            removed += 1
        else:
            output += record
        if name == "TRAILER!!!":
            break
        offset = end
    return bytes(output), removed


def cpio_entries(cpio: bytes):
    entries = []
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
        entries.append((name, fields, data))
        if name == "TRAILER!!!":
            break
        offset = (data_start + file_size + 3) & ~3
    return entries


def main() -> None:
    src = bytearray(SRC_IMAGE.read_bytes())
    original = ORIGINAL_IMAGE.read_bytes()

    src_size = struct.unpack_from("<I", src, 24)[0]
    cpio = decompress_legacy(bytes(src[PAGE : PAGE + src_size]))
    if len(cpio) == 0:
        raise ValueError("failed to decompress source ramdisk")

    stripped, removed = strip_entry(cpio, "init")
    if removed != 1:
        raise ValueError(f"expected 1 init entry, removed {removed}")

    repacked = compress_legacy(stripped)
    new_size = len(repacked)
    print(f"new lz4 stream size: 0x{new_size:x}")

    dtb_size = struct.unpack_from("<I", original, 2100)[0]
    table_size = struct.unpack_from("<I", original, 2112)[0]
    bootconfig_size = struct.unpack_from("<I", original, 2124)[0]

    orig_dtb_off = align(PAGE + struct.unpack_from("<I", original, 24)[0], PAGE)
    orig_table_off = align(orig_dtb_off + dtb_size, PAGE)
    orig_bootconfig_off = align(orig_table_off + table_size, PAGE)

    dtb = original[orig_dtb_off : orig_dtb_off + dtb_size]
    table = bytearray(
        original[orig_table_off : orig_table_off + table_size]
    )
    bootconfig = original[
        orig_bootconfig_off : orig_bootconfig_off + bootconfig_size
    ]

    # vendor_ramdisk_table_entry: ramdisk_size is the first u32.
    if table_size >= 4:
        struct.pack_into("<I", table, 0, new_size)

    output = bytearray(src)
    output[PAGE : PAGE + new_size] = repacked

    new_dtb_off = align(PAGE + new_size, PAGE)
    new_table_off = align(new_dtb_off + dtb_size, PAGE)
    new_bootconfig_off = align(new_table_off + table_size, PAGE)

    output[new_dtb_off : new_dtb_off + dtb_size] = dtb
    output[new_table_off : new_table_off + table_size] = table
    if bootconfig_size:
        output[
            new_bootconfig_off : new_bootconfig_off + bootconfig_size
        ] = bootconfig

    struct.pack_into("<I", output, 24, new_size)
    OUT_IMAGE.write_bytes(output)

    # ---- verification ----
    verify = bytearray(OUT_IMAGE.read_bytes())
    check_size = struct.unpack_from("<I", verify, 24)[0]
    check_cpio = decompress_legacy(bytes(verify[PAGE : PAGE + check_size]))
    check_entries = cpio_entries(check_cpio)
    names = [name for name, _, _ in check_entries]
    guard = next(
        data
        for name, _, data in check_entries
        if name == "lib/modules/oplus_security_guard.ko"
    )
    check_table_off = align(
        align(PAGE + check_size, PAGE) + dtb_size, PAGE
    )
    table_readback = bytes(
        verify[check_table_off : check_table_off + table_size]
    )

    print(f"output: {OUT_IMAGE}")
    print(f"sha256: {hashlib.sha256(verify).hexdigest()}")
    print(f"header vendor_ramdisk_size: 0x{check_size:x}")
    print(
        "table ramdisk_size      : 0x"
        f"{struct.unpack_from('<I', table_readback, 0)[0]:x}"
    )
    print(f"cpio size: {len(check_cpio):x}  entries: {len(names)}")
    print(f"has init: {'init' in names}")
    print(f"guard sha256: {hashlib.sha256(guard).hexdigest()}")
    print(f"  .text+0x50c : {guard[0x150c:0x1510].hex()}")
    print(f"  .init+0xb0  : {guard[0x2c98:0x2c9c].hex()}")
    print(f"  rodata path : {bytes(guard[0x28ab:0x28ba])}")
    print(f"dtb identical: {bytes(verify[align(PAGE+check_size,PAGE):align(PAGE+check_size,PAGE)+len(dtb)]) == dtb}")
    print(f"bootconfig size: {bootconfig_size}")


if __name__ == "__main__":
    main()
