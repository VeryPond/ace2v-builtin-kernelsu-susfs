### AnyKernel3 - SukiSU-Ultra (builtin) + SuSFS for OnePlus Ace 2V (PHP110 / MTK6983)
## Flashes a complete prebuilt boot image so the stock ramdisk is preserved.

properties() { '
kernel.string=SukiSU-Ultra builtin + SuSFS - Ace 2V (PHP110/MT6983)
do.devicecheck=1
do.modules=0
do.systemless=0
do.cleanup=1
do.cleanuponabort=0
device.name1=OP5927
device.name2=PHP110
device.name3=mt6983
device.name4=
device.name5=
supported.versions=
supported.patchlevels=
supported.vendorpatchlevels=
'; } # end properties

### Install
BLOCK=boot;
IS_SLOT_DEVICE=1;
RAMDISK_COMPRESSION=auto;
PATCH_VBMETA_FLAG=auto;

. tools/ak3-core.sh;

# Flash the complete prebuilt boot image (stock ramdisk + builtin-KSU kernel).
flash_generic boot;
