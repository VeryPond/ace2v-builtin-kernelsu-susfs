# 刷写说明

## 需要的三个镜像

这套方案要同时改三个分区，少一个都不行：

| 文件 | 分区 | 为什么需要 |
|---|---|---|
| `lk_a.img` | `lk_a` | 让引导链跳过镜像校验，并把启动状态报成 green |
| `vendor_boot_a.img` | `vendor_boot_a` | 去掉会顶掉 ksuinit 的 init，并让安全守卫模块失效 |
| `boot_a.img` | `boot_a` | 内建 KernelSU + SuSFS 的内核 |

`release/` 里还有一个 `SukiSU_SuSFS_Ace2V_AK3.zip`，
是卡刷包，里面装的就是上面那个 boot 镜像，刷它等于刷 boot。

## 刷之前把原厂镜像留一份

三个分区都读一遍，存好：

```sh
for p in lk_a vendor_boot_a boot_a; do
  adb shell su -c "cat /dev/block/by-name/$p > /data/local/tmp/$p.img"
  adb pull /data/local/tmp/$p.img
done
```

## 刷入

### 方式一：adb（需要 root）

```sh
adb push lk_a.img          /data/local/tmp/lk.img
adb push vendor_boot_a.img /data/local/tmp/vb.img
adb push boot_a.img        /data/local/tmp/boot.img

adb shell su -c 'dd if=/data/local/tmp/lk.img   of=/dev/block/by-name/lk_a'
adb shell su -c 'dd if=/data/local/tmp/vb.img   of=/dev/block/by-name/vendor_boot_a'
adb shell su -c 'dd if=/data/local/tmp/boot.img of=/dev/block/by-name/boot_a'
adb reboot
```

### 方式二：fastboot

```sh
fastboot flash lk_a          lk_a.img
fastboot flash vendor_boot_a vendor_boot_a.img
fastboot flash boot_a        boot_a.img
fastboot reboot
```

### 方式三：卡刷

刷 `SukiSU_SuSFS_Ace2V_AK3.zip` 只处理 boot。
lk 和 vendor_boot 仍然要用上面两种方式刷。

## 每个镜像改了什么

### lk_a.img

lk 的代码里动了 3 个字节：

| 地址 | 原来是 | 改成 | 干什么用的 |
|---|---|---|---|
| `0x51330` | `cbnz w21,...` | `nop` | 让「这个分区要不要验签」的判断失效 |
| `0x51338` | `mov w0,#2` | `mov w0,#0` | 把启动状态值改成 green |
| `0xb34a0` | `65` | `d1` | 配合上面那处，改状态表指针 |

证书部分保持原厂签名不动，只在 CERT2 里追加一段覆盖哈希的块。
这一步不需要私钥，原理见 `LK_EXPLOIT.md`。

其它看似大量的差异，是追加数据后整体往后挪造成的，不是又改了别的东西。

### vendor_boot_a.img

里面塞了两处改动：

1. **删掉 `init`**。原厂这个文件指向 `/system/bin/init`，
   启动时会盖掉 boot 里的 ksuinit，KernelSU 就起不来了。
2. **给 `lib/modules/oplus_security_guard.ko` 打补丁**。
   两个位置从 `e8079f1a` 改成 `28008052`（就是 `mov w8,#1`），
   里面的路径从 `/data/local/tmp` 改成 `/data/adb/ksud`。
   这个模块是 OPPO 的安全守卫，不改它会拦。

DTB 没动，剩下的 892 个文件也和原厂一致。

### boot_a.img

换成了重新编译的内核，KernelSU 和 SuSFS 都编在里面，不再用 `.ko`。
ramdisk 是原厂的，没改。

## 刷完确认

```sh
adb shell getprop ro.boot.verifiedbootstate   # green
adb shell getprop ro.boot.flash.locked        # 1
adb shell uname -r                            # 5.10.110-android12-9-g4d2e7c69e8b4
adb shell su -c id                            # uid=0, context=u:r:ksu:s0
adb shell su -c 'cat /proc/modules | grep kernelsu'   # 没有输出才对
```

管理器里应该显示：工作中、版本 40900、Built-in、SuSFS v2.3.0。

## 没动的分区

dtbo、vbmeta、以及锁状态（seccfg、RPMB）。

## 开不了机怎么救

第一屏能出来，说明 lk 和 fastboot 都是好的，机器没坏。
按住电源加音量下进 fastboot，把前面备份的原厂镜像刷回去：

```sh
fastboot flash lk_a          stock_lk_a.img
fastboot flash vendor_boot_a stock_vendor_boot_a.img
fastboot flash boot_a        stock_boot_a.img
fastboot reboot
```
