#!/usr/bin/env python3
"""What is in the stock decompressed kernel beyond image_size?"""
import gzip, struct

PAGE = 4096
DTB = b"\xd0\x0d\xfe\xed"

sb = open("/root/op/boot_a_readback.img", "rb").read()
ks = struct.unpack_from("<I", sb, 8)[0]
img = gzip.decompress(sb[PAGE:PAGE + ks])
image_size = struct.unpack_from("<Q", img, 16)[0]
print(f"decompressed len = {len(img)}")
print(f"image_size field = {image_size}")
print(f"extra            = {len(img) - image_size}")

extra = img[image_size:]
print(f"\nextra region first 64 bytes:\n  {extra[:64].hex(' ')}")
print(f"extra region last  64 bytes:\n  {extra[-64:].hex(' ')}")
nz = sum(1 for b in extra if b)
print(f"non-zero bytes in extra: {nz} / {len(extra)}")
print(f"DTB magic in extra: {extra.find(DTB)}")
print(f"DTB magic anywhere in whole image: {img.find(DTB)}")

# how many 4K pages of padding at the end (all zero)?
pad = 0
while pad < len(img) and img[len(img) - 1 - pad] == 0:
    pad += 1
print(f"trailing zero bytes in whole image: {pad}")

# Show boundary context
lo = max(0, image_size - 32)
print(f"\nbytes around image_size boundary:")
seg = img[lo:image_size + 32]
for i in range(0, len(seg), 16):
    row = seg[i:i + 16]
    asc = "".join(chr(c) if 32 <= c < 127 else "." for c in row)
    print(f"  {lo+i:9d}: {row.hex(' ')}  {asc}")

# our kernel
our = open("/root/op/kout/arch/arm64/boot/Image", "rb").read()
ois = struct.unpack_from("<Q", our, 16)[0]
print(f"\nOUR Image: len={len(our)} image_size={ois} extra={len(our)-ois}")
oe = our[ois:]
print(f"  our extra nonzero: {sum(1 for b in oe if b)} / {len(oe)}")
