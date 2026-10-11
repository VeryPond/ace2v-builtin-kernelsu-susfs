# 刷机与回滚

## 前提

- 设备已连接（`adb devices` 可见）
- 目标槽位：引导当前为 A 槽（`ro.boot.slot_suffix=_a`）
- 已备份原厂 boot（`release/` 或自行读回）

## 回滚镜像（务必先准备）

原厂 boot 请自行从设备读回，或使用与厂商 OTA 一致的 boot 镜像。
读回命令（设备需 root）：

```sh
adb shell su -c 'cat /dev/block/by-name/boot_a > /data/local/tmp/boot_stock.img'
adb pull /data/local/tmp/boot_stock.img stock_boot_a.img
```

## 方式一：adb 直接写分区（需要 root）

```sh
adb push release/boot_builtin_susfs_spoofed_v3.img /data/local/tmp/boot_new.img
adb shell su -c 'dd if=/data/local/tmp/boot_new.img of=/dev/block/by-name/boot_a bs=4096'
adb shell su -c 'sha256sum /dev/block/by-name/boot_a'
adb reboot
```

## 方式二：fastboot

```sh
fastboot flash boot_a release/boot_builtin_susfs_spoofed_v3.img
fastboot reboot
```

## 方式三：AnyKernel3 卡刷

在 KernelSU 管理器或 recovery 中刷入 `release/SukiSU_SuSFS_Ace2V_AK3_v2.zip`。
该包内嵌完整 boot 镜像（`flash_generic boot`），会整镜像写入。

## 回滚

```sh
# adb 方式
adb push stock_boot_a.img /data/local/tmp/boot_stock.img
adb shell su -c 'dd if=/data/local/tmp/boot_stock.img of=/dev/block/by-name/boot_a bs=4096'
adb reboot

# fastboot 方式
fastboot flash boot_a stock_boot_a.img
```

## 刷后验证

```sh
adb shell getprop ro.boot.verifiedbootstate   # green
adb shell getprop ro.boot.flash.locked        # 1
adb shell uname -r                            # 5.10.110-android12-9-g4d2e7c69e8b4
adb shell su -c id                            # uid=0 context=u:r:ksu:s0
adb shell su -c 'cat /proc/modules | grep -c ^kernelsu'   # 0（内建）
```

管理器内应显示：工作中、版本 40900、Built-in、SuSFS v2.3.0。

## 故障恢复

若出现"第一屏 logo 后无限重启"：

1. 长按电源加音量下进入 fastboot
2. 刷回原厂 boot：`fastboot flash boot_a stock_boot_a.img`
3. `fastboot reboot`

该状态**不是砖**——能出第一屏说明 lk 与 fastboot 均正常。
