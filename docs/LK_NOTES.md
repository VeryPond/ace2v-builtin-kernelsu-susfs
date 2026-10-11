# Bootloader (LK) 相关记录

本仓库主线是内核（boot）层面的工作。LK 的探测在早期阶段完成，
结论记录在此，供理解整机状态。

## 背景

为实现 `verifiedbootstate=green` 且保持 `flash.locked=1`，
曾对 LK 分区做过多轮参数探测（产物见原始工作区的 `lk_*` 文件）。
该部分不属于本仓库发布内容，此处仅记录结论。

## 观测到的行为

| 镜像 | 结果 |
|---|---|
| 原厂 `lk_a.img` | 正常 |
| 参数表/DTB 变体（`lk_a_probe_dtb*`） | 部分变体黑屏或进系统，差异体现在 DTB 处理 |
| `lk_a_probe_green.img` | 达成 green 状态 |

## 与内核的关系

- DTB **不在 boot 分区**，而在 `vendor_boot`
  （头部 `dtb_size=321654`、`dtb_addr=0x47c80000`）
- 换内核时 DTB 不用碰，但它放在 vendor_boot 里，所以本方案
  仍然替换了整个 vendor_boot 分区（改的是 ramdisk，DTB 原样保留）
- boot 分区末尾的 AVB 结构需正确搬运（见 ARCHITECTURE.md 第 4.1 节）

> 本文件是早期记录。三个分区各自改了什么，以 `FLASHING.md` 为准。

## 注意

不同固件版本之间，LK 与 boot 的配合关系可能变化。
本记录仅对应 `PHP110_11_A.08`。
