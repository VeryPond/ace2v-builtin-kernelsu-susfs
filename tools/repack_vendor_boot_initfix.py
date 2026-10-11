import hashlib
import lz4.block
import struct
from pathlib import Path


BASE_IMAGE = Path(r"E:\_probe_pwnage24mtk\vendor_boot_a_patched.img")
ORIGINAL_IMAGE = Path(
    r"E:\GeekFlashTool_Readback_20261010230748790\vendor_boot_a.img"
)
OUTPUT_IMAGE = Path(r"E:\_probe_pwnage24mtk\vendor_boot_a_patched_initfix.img")

PAGE_SIZE = 4096
HEADER_SIZE = PAGE_SIZE
CPIO_SIZE = 87_254_272
MODULE_CPIO_OFFSET = 0x26B9714
INIT_TEXT_CSET_OFFSET = 0x2C98
TEXT_UNLOCK_OFFSET = 0x150C
RODATA_PATH_OFFSET = 0x28AB

LZ4_MAGIC = 0x184C2102
MAX_LZ4_BLOCK = 8 * 1024 * 1024
CSET_NE = bytes.fromhex("e8079f1a")
MOV_W8_1 = bytes.fromhex("28008052")


def align_up(value: int, alignment: int) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def read_u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def write_u32(data: bytearray, offset: int, value: int) -> None:
    struct.pack_into("<I", data, offset, value)


def decompress_legacy_lz4(data: bytes) -> bytes:
    if read_u32(data, 0) != LZ4_MAGIC:
        raise ValueError("unexpected LZ4 magic")

    output = bytearray()
    offset = 4
    block_index = 0

    while offset < len(data):
        compressed_size = read_u32(data, offset)
        offset += 4
        compressed = data[offset : offset + compressed_size]
        if len(compressed) != compressed_size:
            raise ValueError(f"truncated LZ4 block {block_index}")

        output += lz4.block.decompress(
            compressed,
            uncompressed_size=MAX_LZ4_BLOCK,
        )
        offset += compressed_size
        block_index += 1

    if len(output) != CPIO_SIZE:
        raise ValueError(f"unexpected cpio size: {len(output)}")
    return bytes(output)


def compress_legacy_lz4(data: bytes) -> bytes:
    output = bytearray(struct.pack("<I", LZ4_MAGIC))

    for block_start in range(0, len(data), MAX_LZ4_BLOCK):
        block = data[block_start : block_start + MAX_LZ4_BLOCK]
        compressed = lz4.block.compress(
            block,
            mode="high_compression",
            compression=12,
            store_size=False,
        )
        output += struct.pack("<I", len(compressed))
        output += compressed

    return bytes(output)


def main() -> None:
    base = bytearray(BASE_IMAGE.read_bytes())
    original = ORIGINAL_IMAGE.read_bytes()

    if base[:8] != b"VNDRBOOT" or original[:8] != b"VNDRBOOT":
        raise ValueError("not a vendor_boot image")
    if read_u32(base, 8) != 4 or read_u32(base, 12) != PAGE_SIZE:
        raise ValueError("unexpected vendor_boot version/page size")

    original_ramdisk_size = read_u32(original, 24)
    base_ramdisk_size = read_u32(base, 24)
    if base_ramdisk_size != original_ramdisk_size - 1:
        raise ValueError(
            "base image ramdisk size differs from the expected prior patch"
        )

    # The stock header counts one trailing pad byte; the legacy LZ4 stream itself
    # ends at the size stored in the already-patched image.
    compressed = bytes(base[HEADER_SIZE : HEADER_SIZE + base_ramdisk_size])
    cpio = bytearray(decompress_legacy_lz4(compressed))

    module = cpio[
        MODULE_CPIO_OFFSET : MODULE_CPIO_OFFSET + 0x2F70
    ]
    if module[TEXT_UNLOCK_OFFSET : TEXT_UNLOCK_OFFSET + 4] != MOV_W8_1:
        raise ValueError("prior .text is_unlocked patch is missing")
    if (
        module[RODATA_PATH_OFFSET : RODATA_PATH_OFFSET + 15]
        != b"/data/adb/ksud\x00"
    ):
        raise ValueError("prior ksud path patch is missing")

    init_text_patch = MODULE_CPIO_OFFSET + INIT_TEXT_CSET_OFFSET
    if cpio[init_text_patch : init_text_patch + 4] != CSET_NE:
        raise ValueError("unexpected bytes at .init.text+0xb0")
    cpio[init_text_patch : init_text_patch + 4] = MOV_W8_1

    repacked_ramdisk = compress_legacy_lz4(cpio)
    repacked_ramdisk_size = len(repacked_ramdisk)

    output = bytearray(base)
    output[HEADER_SIZE : HEADER_SIZE + repacked_ramdisk_size] = repacked_ramdisk
    # v4 records the aggregate vendor-ramdisk span in both the header and the
    # table entry. Keep that span identical to stock and leave zero padding
    # after the shorter LZ4 stream, just like the original image.
    output[
        HEADER_SIZE + repacked_ramdisk_size :
        HEADER_SIZE + original_ramdisk_size
    ] = b"\x00" * (original_ramdisk_size - repacked_ramdisk_size)
    write_u32(output, 24, original_ramdisk_size)

    original_dtb_offset = align_up(
        HEADER_SIZE + original_ramdisk_size,
        PAGE_SIZE,
    )
    dtb_size = read_u32(original, 2100)
    vendor_ramdisk_table_size = read_u32(original, 2112)
    bootconfig_size = read_u32(original, 2124)

    original_table_offset = align_up(
        original_dtb_offset + dtb_size,
        PAGE_SIZE,
    )
    original_bootconfig_offset = align_up(
        original_table_offset + vendor_ramdisk_table_size,
        PAGE_SIZE,
    )

    dtb = bytes(original[original_dtb_offset : original_dtb_offset + dtb_size])
    vendor_ramdisk_table = bytes(
        original[
            original_table_offset : original_table_offset
            + vendor_ramdisk_table_size
        ]
    )
    bootconfig = bytes(
        original[
            original_bootconfig_offset : original_bootconfig_offset
            + bootconfig_size
        ]
    )

    new_dtb_offset = align_up(
        HEADER_SIZE + repacked_ramdisk_size,
        PAGE_SIZE,
    )
    new_table_offset = align_up(new_dtb_offset + dtb_size, PAGE_SIZE)
    new_bootconfig_offset = align_up(
        new_table_offset + vendor_ramdisk_table_size,
        PAGE_SIZE,
    )

    output[new_dtb_offset : new_dtb_offset + dtb_size] = dtb
    output[
        new_table_offset : new_table_offset + vendor_ramdisk_table_size
    ] = vendor_ramdisk_table
    if bootconfig:
        output[
            new_bootconfig_offset : new_bootconfig_offset + bootconfig_size
        ] = bootconfig

    OUTPUT_IMAGE.write_bytes(output)

    verify = decompress_legacy_lz4(
        bytes(output[HEADER_SIZE : HEADER_SIZE + repacked_ramdisk_size])
    )
    verify_module = verify[
        MODULE_CPIO_OFFSET : MODULE_CPIO_OFFSET + 0x2F70
    ]
    if verify_module[
        INIT_TEXT_CSET_OFFSET : INIT_TEXT_CSET_OFFSET + 4
    ] != MOV_W8_1:
        raise ValueError("init.text patch verification failed")
    if verify != cpio:
        raise ValueError("repacked ramdisk changed beyond the intended patch")

    print(f"output: {OUTPUT_IMAGE}")
    print(f"size: {len(output)}")
    print(f"sha256: {hashlib.sha256(output).hexdigest()}")
    print(f"lz4_stream_size: 0x{repacked_ramdisk_size:x}")
    print(f"vendor_ramdisk_size: 0x{original_ramdisk_size:x}")
    print(f"dtb_offset: 0x{new_dtb_offset:x}")
    print(f"table_offset: 0x{new_table_offset:x}")
    print(f"bootconfig_offset: 0x{new_bootconfig_offset:x}")
    print("verify .init.text+0xb0: mov w8, #1")
    print("verify ksud path: /data/adb/ksud")


if __name__ == "__main__":
    main()
