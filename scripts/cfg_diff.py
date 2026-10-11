#!/usr/bin/env python3
"""Show only ACTIVE config differences (y / m / value), ignoring 'not set'."""
import re

DEV = "/root/op/device_config"
OUR = "/root/op/kout/.config"


def load(p):
    d = {}
    for line in open(p, errors="replace"):
        line = line.strip()
        m = re.match(r"^(CONFIG_[A-Za-z0-9_]+)=(.*)$", line)
        if m:
            d[m.group(1)] = m.group(2)
    return d


dev = load(DEV)
our = load(OUR)

print(f"device active settings: {len(dev)}")
print(f"ours   active settings: {len(our)}")

only_dev = sorted(set(dev) - set(our))
only_our = sorted(set(our) - set(dev))
both_diff = sorted(k for k in set(dev) & set(our) if dev[k] != our[k])

print(f"\n===== ACTIVE in device, ABSENT in ours ({len(only_dev)}) =====")
for k in only_dev:
    print(f"  {k}={dev[k]}")

print(f"\n===== ACTIVE in ours, ABSENT in device ({len(only_our)}) =====")
for k in only_our:
    print(f"  {k}={our[k]}")

print(f"\n===== BOTH present but DIFFERENT ({len(both_diff)}) =====")
for k in both_diff:
    print(f"  {k}: device={dev[k]}  ours={our[k]}")

# Highlight boot-critical groups
print("\n===== boot-critical spot check =====")
crit = ["CONFIG_ARM64_VA_BITS","CONFIG_ARM64_PA_BITS","CONFIG_ARM64_4K_PAGES",
        "CONFIG_PAGE_OFFSET","CONFIG_ARM64_MTE","CONFIG_KASAN_HW_TAGS",
        "CONFIG_LTO_CLANG_FULL","CONFIG_CFI_CLANG","CONFIG_SHADOW_CALL_STACK",
        "CONFIG_RANDOMIZE_BASE","CONFIG_RELOCATABLE","CONFIG_ARM64_SW_TTBR0_PAN",
        "CONFIG_ARM64_PAN","CONFIG_ARM64_TAGGED_ADDR_ABI","CONFIG_OF",
        "CONFIG_USE_OF","CONFIG_MTK_GPU_VERSION","CONFIG_CMDLINE",
        "CONFIG_BUILD_ARM64_DT_OVERLAY","CONFIG_ARM64_ERRATUM_1319367",
        "CONFIG_ARCH_MMAP_RND_BITS","CONFIG_SCHED_CLUSTER","CONFIG_HZ"]
for k in crit:
    print(f"  {k:42s} device={dev.get(k,'<none>'):18s} ours={our.get(k,'<none>')}")
