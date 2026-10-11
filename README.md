# OnePlus Ace 2V (PHP110 / MT6983) 引导链与内核

> 本仓库由 Codex 生成。供研究与个人设备维护使用。刷机有风险，务必先阅读回滚章节。

针对 OnePlus Ace 2V 做了两件事：

1. 搞清楚 MTK 引导链的证书校验是怎么被绕过的，并在真机上验证
2. 把 KernelSU 和 SuSFS 编进内核（不用 `.ko`），同时让内核看起来还是原厂的

## 三个镜像

完整方案要改三个分区，缺一不可：

| 文件 | 分区 | 改了什么 |
|---|---|---|
| `lk_a_green_patched.img` | `lk_a` | 跳过镜像校验，启动状态报 green |
| `vendor_boot_a_noinit_v2.img` | `vendor_boot_a` | 删掉顶掉 ksuinit 的 init，安全守卫模块失效 |
| `boot_builtin_susfs_spoofed_v3.img` | `boot_a` | 内建 KernelSU + SuSFS 的内核 |

细节看 [docs/FLASHING.md](docs/FLASHING.md)。

## 做了什么

引导链这边：MTK 用 CERT1/CERT2 给引导镜像签名，但解析证书的那段代码有
个毛病 —— 往 CERT2 前面塞一段自己造的哈希块，它会拿这里面的值，
把证书里真正的哈希忽略掉。**整个过程不需要私钥。**

内核这边：SukiSU-Ultra 和 SuSFS 编进内核本体，
`/proc/modules` 里看不到 `kernelsu.ko`。内核版本串、`/proc/config.gz`
都伪装成原厂的样子。

当前设备状态：

| 项目 | 值 |
|---|---|
| Bootloader | `flash.locked=1`、`verifiedbootstate=green` |
| Root | `uid=0`、`context=u:r:ksu:s0` |
| KernelSU | 内建，版本 40900 |
| SuSFS | v2.3.0 |
| 内核版本串 | 和原厂一样 |
| `/proc/config.gz` | 和原厂一样，看不出 KSU/SuSFS |

## 文档

| 文件 | 内容 |
|---|---|
| [docs/LK_EXPLOIT.md](docs/LK_EXPLOIT.md) | 引导链漏洞怎么回事，以及反汇编证据 |
| [docs/LK_EXPLOIT_VERIFY.md](docs/LK_EXPLOIT_VERIFY.md) | 真机上怎么验证出来的 |
| [docs/LK_AVB_PATCH.md](docs/LK_AVB_PATCH.md) | LK 里 AVB 校验那部分怎么改 |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 内核方案的思路和踩过的坑 |
| [docs/BUILD.md](docs/BUILD.md) | 内核怎么编译 |
| [docs/FLASHING.md](docs/FLASHING.md) | 三个镜像怎么刷、怎么救回来 |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | 遇到的问题和解决办法 |
| [docs/DEVICE_INFO.md](docs/DEVICE_INFO.md) | 设备、分区、固件信息 |
| [docs/CVE_COMPARISON.md](docs/CVE_COMPARISON.md) | 和 CVE-2023-20696 / CVE-2025-20730 的关系 |
| [docs/CREDITS.md](docs/CREDITS.md) | 用到的 CVE、上游仓库和作者 |

引导链那部分用的是 **kasnria001** 的
[pwnage24mtk](https://github.com/kasnria001/pwnage24mtk)。

---

## 目录

```
docs/          说明文档（见上表）
tools/         证书处理、LK 反汇编、boot 重打包、AK3 打包
scripts/       内核集成、编译、伪装、校验脚本
configs/       原厂 config、KSU/SuSFS 配置片段、模块清单
release/       编好的镜像
patch/         对内核源码的改动
```

## 编译内核时注意

三件事不注意就会白忙（详见 `docs/ARCHITECTURE.md`）：

1. 打包 boot 时要把原厂签名的 vbmeta 原样搬过去，
   用 `avbtool --algorithm NONE` 生成的无签名结构刷了会一直重启
2. 内核 gzip 的头部要和原厂一致（`FLG=0x00`、`OS=3`）
3. 要用完整的 LLVM 工具链。用默认的 GNU nm/ar 会让
   LTO/CFI/KASAN 在配置阶段被悄悄去掉，厂商模块就对不上了

## 兼容性

- 设备：OnePlus Ace 2V（`OP5927` / `PHP110`）
- 固件：`PHP110_11_A.08`
- 内核：`5.10.110-android12-9`
- 平台：MediaTek MT6983
