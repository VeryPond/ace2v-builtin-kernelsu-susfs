# OnePlus Ace 2V (PHP110 / MT6983) - 引导链与内核研究

本项目包含两部分：

1. **MTK 引导链证书校验绕过的完整分析与真机验证**（重点）
2. 内建 KernelSU + SuSFS 的内核方案（落地成果）

---

## 引导链漏洞（重点）

MTK 引导链的证书校验存在 ASN.1 解析逻辑缺陷：**无需任何私钥**，
只需向 CERT2 追加特制块，即可让被篡改的引导子镜像通过校验。

| 文档 | 内容 |
|---|---|
| [docs/LK_EXPLOIT.md](docs/LK_EXPLOIT.md) | 信任模型、容器结构、漏洞原理、反汇编证据 |
| [docs/LK_EXPLOIT_VERIFY.md](docs/LK_EXPLOIT_VERIFY.md) | 真机差分实验、完整利用链、产物哈希 |
| [docs/LK_AVB_PATCH.md](docs/LK_AVB_PATCH.md) | LK 层 AVB 门禁分析与修补 |

核心结论：

- 适用形态为 **legacy**（`BIT STRING(原 CERT2 DER)` + `A0{...}`），
  对应 `bypass_mode=1`"任意对象都进入"的宽松分支
- **new（V6）形态在本机不成立**
- 已验证目标：`lk_main_dtb`（LK 校验）与 `lk`（BL2_EXT 校验）
- 影响：绕过可信启动，等价于不依赖官方解锁取得引导链控制权

分析工具（`tools/pwnage24mtk/`、`tools/lk_analysis/`）与差分实验流程一并收录。

---

## 内核方案

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
docs/
  LK_EXPLOIT.md            引导链漏洞原理与反汇编证据
  LK_EXPLOIT_VERIFY.md     真机差分验证与完整利用链
  LK_AVB_PATCH.md          LK 层 AVB 门禁修补
  ARCHITECTURE.md          内核方案与决策记录
  BUILD.md                 内核编译流程
  FLASHING.md              刷机与回滚
  TROUBLESHOOTING.md       内核侧踩坑记录
  LK_NOTES.md              bootloader 概览
  lk/                      LK/AVB 原始分析数据
  reports/                 pwnage24mtk 探测报告 + CVE 扫描报告
tools/
  pwnage24mtk/             MTK 证书工具（parse/sign/verify/build）
  lk_analysis/             LK 反汇编与差分实验脚本
  anykernel.sh, make_ak3_zip.sh   AK3 打包
scripts/                   内核集成 / 编译 / 伪装 / 打包 / 校验
configs/                   真机 config、KSU/SuSFS 配置、模块清单
release/                   预编译产物（boot 镜像、AK3 卡刷包）
patch/                     内核改动 patch 与说明
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
