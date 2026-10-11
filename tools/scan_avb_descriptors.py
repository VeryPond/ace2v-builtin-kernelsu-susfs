from pathlib import Path


ROOT = Path(r"E:\GeekFlashTool_Readback_20261010230748790")


def main() -> None:
    for name in sorted(ROOT.glob("vbmeta*.img")):
        data = name.read_bytes()
        auth = int.from_bytes(data[12:20], "big")
        aux = int.from_bytes(data[20:28], "big")
        desc_off = int.from_bytes(data[96:104], "big")
        desc_size = int.from_bytes(data[104:112], "big")
        base = 256 + auth + desc_off
        print(
            name.name,
            f"auth={auth}",
            f"aux={aux}",
            f"desc_off={desc_off}",
            f"desc_size={desc_size}",
            f"base=0x{base:x}",
        )
        candidates = []
        for offset in range(base, min(base + desc_size, len(data)) - 16, 8):
            tag = int.from_bytes(data[offset : offset + 8], "big")
            length = int.from_bytes(data[offset + 8 : offset + 16], "big")
            if tag <= 16 and 0 < length <= desc_size:
                candidates.append((offset, tag, length))
        print("candidates", [(hex(off), tag, length) for off, tag, length in candidates[:30]])

        offset = base
        for index in range(20):
            if offset + 16 > len(data):
                break
            tag = int.from_bytes(data[offset : offset + 8], "big")
            length = int.from_bytes(data[offset + 8 : offset + 16], "big")
            print(
                f"  d{index} off=0x{offset:x} tag={tag} len={length} "
                f"preview={data[offset:offset+80].hex()}"
            )
            if length == 0 or offset + 16 + length > len(data):
                break
            offset += 16 + length
        print()


if __name__ == "__main__":
    main()
