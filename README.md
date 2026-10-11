# OnePlus Ace 2V (PHP110 / MT6983) - 内建 KernelSU + SuSFS 方案

把 SukiSU-Ultra（内建）与 SuSFS 编进 OnePlus Ace 2V 的内核，实现
**无内核模块的 root**，并让内核对外呈现与厂商原厂一致。

刷机后状态：

| 项目 | 结果 |
|---|---|
| Bootloader | `ro.boot.flash.locked=1`、`ro.boot.verifiedbootstate=green` |
| Root | `uid=0` / `context=u:r:ksu:s0`（SELinux enforcing） |
| KernelSU | **builtin**，`/proc/modules` 中无 `kernelsu.ko` |
| SuSFS | v2.3.0（inline hook） |
| 内核版本串 | 与厂商原厂逐字符一致 |
| `/proc/config.gz` | 内嵌**原厂 config**，不含任何 KSU/SUSFS 条目 |

---

## 目录结构

```
docs/            技术说明与报告
  reports/       原始探测报告（pwnage24mtk / CVE 扫描）
  BUILD.md       完整编译流程
  FLASHING.md    刷机与回滚
  ARCHITECTURE.md 方案与决策记录
  TROUBLESHOOTING.md 踩过的坑
scripts/         内核集成 / 编译 / 打包脚本
tools/           AnyKernel3 打包、boot 重打包工具
configs/         真机 config、KSU/SuSFS 配置片段、模块清单
release/         预编译产物（boot 镜像、AK3 卡刷包）
patch/           本仓库对上游做的必要修改
```

---

## 快速开始

1. 阅读 `docs/BUILD.md` 了解完整构建链路
2. 预编译产物在 `release/`
3. 刷机与回滚见 `docs/FLASHING.md`

## 关键结论（务必先读）

见 `docs/ARCHITECTURE.md`。其中三条是这条路能否走通的硬约束：

1. **AVB 必须搬运原厂签名 vbmeta**，不能用 `avbtool --algorithm NONE`
2. **gzip 头必须是纯净格式**（`FLG=0x00, OS=3`）
3. **必须使用完整 LLVM 工具链**，否则 LTO/CFI/KASAN 会被静默丢弃

## 兼容性

- 设备：OnePlus Ace 2V（`OP5927` / `PHP110`）
- 固件：`PHP110_11_A.08`
- 内核：`5.10.110-android12-9`
- 平台：MediaTek MT6983

> 供研究与个人设备维护使用。刷机有风险，务必先阅读回滚章节。
