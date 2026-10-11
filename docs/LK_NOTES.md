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
- 因此替换内核时**无需改动 vendor_boot**，DTB 自然保持一致
- boot 分区末尾的 AVB 结构需正确搬运（见 ARCHITECTURE.md 第 4.1 节）

## 注意

不同固件版本之间，LK 与 boot 的配合关系可能变化。
本记录仅对应 `PHP110_11_A.08`。
