# Boot, DTBO and AVB Metadata

## boot_a.img

### Android boot

```json
{
  "kernel_size": 20317798,
  "ramdisk_size": 1650577,
  "os_version": 402653554,
  "header_size": 1584,
  "header_version": 4,
  "cmdline": "",
  "signature_size": 0
}
```

## boot_b.img

### Android boot

```json
{
  "kernel_size": 13245833,
  "ramdisk_size": 2021586,
  "os_version": 402653602,
  "header_size": 1584,
  "header_version": 4,
  "cmdline": "",
  "signature_size": 4096
}
```

## vendor_boot_a.img

### Vendor boot

```json
{
  "header_version": 4,
  "page_size": 4096,
  "kernel_addr": 1073741824,
  "ramdisk_addr": 1727004672,
  "vendor_ramdisk_size": 32476753,
  "cmdline": "bootopt=64S3,32N2,64N2 buildvariant=user",
  "tags_addr": 1204289536,
  "name": "",
  "header_size": 2128,
  "dtb_size": 321654,
  "dtb_addr": 1204289536,
  "vendor_ramdisk_table_size": 108,
  "vendor_ramdisk_table_entry_num": 1,
  "vendor_ramdisk_table_entry_size": 108,
  "bootconfig_size": 0,
  "vendor_ramdisk_table": [
    {
      "size": 32476753,
      "offset": 0,
      "type": 1,
      "name": ""
    }
  ]
}
```

## vendor_boot_b.img

### Vendor boot

```json
{
  "header_version": 4,
  "page_size": 4096,
  "kernel_addr": 1073741824,
  "ramdisk_addr": 1727004672,
  "vendor_ramdisk_size": 36111773,
  "cmdline": "bootopt=64S3,32N2,64N2 buildvariant=user",
  "tags_addr": 1204289536,
  "name": "",
  "header_size": 2128,
  "dtb_size": 321678,
  "dtb_addr": 1204289536,
  "vendor_ramdisk_table_size": 108,
  "vendor_ramdisk_table_entry_num": 1,
  "vendor_ramdisk_table_entry_size": 108,
  "bootconfig_size": 0,
  "vendor_ramdisk_table": [
    {
      "size": 36111773,
      "offset": 0,
      "type": 1,
      "name": ""
    }
  ]
}
```

## dtbo_a.img

### DTBO

```json
{
  "magic": "0xd7b7ab1e",
  "total_size": 1011389,
  "header_size": 32,
  "entry_size": 32,
  "entry_count": 6,
  "entries_offset": 32,
  "page_size": 2048,
  "version": 0,
  "entries": [
    {
      "size": 158694,
      "offset": 224,
      "id": 0,
      "rev": 0
    },
    {
      "size": 160165,
      "offset": 158918,
      "id": 1,
      "rev": 0
    },
    {
      "size": 124096,
      "offset": 319083,
      "id": 2,
      "rev": 0
    },
    {
      "size": 121043,
      "offset": 443179,
      "id": 3,
      "rev": 0
    },
    {
      "size": 320657,
      "offset": 564222,
      "id": 4,
      "rev": 0
    },
    {
      "size": 126510,
      "offset": 884879,
      "id": 5,
      "rev": 0
    }
  ]
}
```

## dtbo_b.img

### DTBO

```json
{
  "magic": "0xd7b7ab1e",
  "total_size": 1085848,
  "header_size": 32,
  "entry_size": 32,
  "entry_count": 6,
  "entries_offset": 32,
  "page_size": 2048,
  "version": 0,
  "entries": [
    {
      "size": 159775,
      "offset": 224,
      "id": 0,
      "rev": 0
    },
    {
      "size": 161312,
      "offset": 159999,
      "id": 1,
      "rev": 0
    },
    {
      "size": 127438,
      "offset": 321311,
      "id": 2,
      "rev": 0
    },
    {
      "size": 124235,
      "offset": 448749,
      "id": 3,
      "rev": 0
    },
    {
      "size": 381902,
      "offset": 572984,
      "id": 4,
      "rev": 0
    },
    {
      "size": 130962,
      "offset": 954886,
      "id": 5,
      "rev": 0
    }
  ]
}
```

## vbmeta_a.img

### AVB

```json
{
  "magic": "AVB0",
  "required_major": 1,
  "required_minor": 0,
  "auth_block_size": 320,
  "auxiliary_block_size": 4544,
  "algorithm_type": 1,
  "hash_offset": 0,
  "hash_size": 32,
  "signature_offset": 32,
  "signature_size": 256,
  "public_key_offset": 3976,
  "public_key_size": 520,
  "public_key_metadata_offset": 4496,
  "public_key_metadata_size": 0,
  "descriptors_offset": 0,
  "descriptors_size": 3976,
  "rollback_index": 0,
  "flags": 0,
  "rollback_index_location": 0,
  "release_string": "avbtool 1.2.0",
  "descriptors": [
    {
      "tag": "chain_partition",
      "rollback_index_location": 3,
      "partition_name": "",
      "public_key_len": 0
    },
    {
      "tag": "chain_partition",
      "rollback_index_location": 2,
      "partition_name": "",
      "public_key_len": 0
    },
    {
      "tag": "chain_partition",
      "rollback_index_location": 4,
      "partition_name": "",
      "public_key_len": 0
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000!\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.boot.os_version\u000012\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000%\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.boot.security_patch\u00002023-02-05\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000%\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.boot.security_patch\u00002023-02-05\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000)\u0000\u0000\u0000\u0000\u0000\u0000\u0000Ycom.android.build.vendor_boot.fingerprint\u0000alps/hal_mgvi_64_armv82/mgvi_64_armv82:12/SP1A.210812.016/1678055723093:user/release-keys\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000!\u0000\u0000\u0000\u0000\u0000\u0000\u0000Ycom.android.build.odm.fingerprint\u0000alps/hal_mgvi_64_armv82/mgvi_64_armv82:12/SP1A.210812.016/1678055723093:user/release-keys\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000 \u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.odm.os_version\u000012\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000&\u0000\u0000\u0000\u0000\u0000\u0000\u0000Ycom.android.build.odm_dlkm.fingerprint\u0000alps/hal_mgvi_64_armv82/mgvi_64_armv82:12/SP1A.210812.016/1678055723093:user/release-keys\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000%\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.odm_dlkm.os_version\u000012\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000)\u0000\u0000\u0000\u0000\u0000\u0000\u0000Ycom.android.build.vendor_dlkm.fingerprint\u0000alps/hal_mgvi_64_armv82/mgvi_64_armv82:12/SP1A.210812.016/1678055723093:user/release-keys\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000(\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.vendor_dlkm.os_version\u000012\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "hash",
      "image_size": 32808960,
      "hash_algorithm": "sha256",
      "salt_len": 11,
      "digest_len": 16
    },
    {
      "tag": "hashtree",
      "image_size": 4294967296,
      "tree_offset": 72110370596061184,
      "tree_size": 72110370596061184,
      "data_block_size": 598134325514240,
      "hash_block_size": 17592186044418,
      "fdt_offset": 16928768,
      "fdt_size": 139264
    },
    {
      "tag": "hashtree",
      "image_size": 4294967296,
      "tree_offset": 1125899906842624,
      "tree_size": 1125899906842624,
      "data_block_size": 17592186048512,
      "hash_block_size": 17592186044418,
      "fdt_offset": 266240,
      "fdt_size": 8192
    },
    {
      "tag": "hashtree",
      "image_size": 4294967296,
      "tree_offset": 247733163877466112,
      "tree_size": 247733163877466112,
      "data_block_size": 1970324836978688,
      "hash_block_size": 17592186044418,
      "fdt_offset": 58138624,
      "fdt_size": 466944
    }
  ]
}
```

## vbmeta_b.img

### AVB

```json
{
  "magic": "AVB0",
  "required_major": 1,
  "required_minor": 0,
  "auth_block_size": 320,
  "auxiliary_block_size": 4032,
  "algorithm_type": 1,
  "hash_offset": 0,
  "hash_size": 32,
  "signature_offset": 32,
  "signature_size": 256,
  "public_key_offset": 3496,
  "public_key_size": 520,
  "public_key_metadata_offset": 4016,
  "public_key_metadata_size": 0,
  "descriptors_offset": 0,
  "descriptors_size": 3496,
  "rollback_index": 0,
  "flags": 0,
  "rollback_index_location": 0,
  "release_string": "avbtool 1.2.0",
  "descriptors": [
    {
      "tag": "chain_partition",
      "rollback_index_location": 3,
      "partition_name": "",
      "public_key_len": 0
    },
    {
      "tag": "chain_partition",
      "rollback_index_location": 2,
      "partition_name": "",
      "public_key_len": 0
    },
    {
      "tag": "chain_partition",
      "rollback_index_location": 4,
      "partition_name": "",
      "public_key_len": 0
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000!\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.boot.os_version\u000012\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000%\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.boot.security_patch\u00002026-04-01\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000%\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.boot.security_patch\u00002026-04-01\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000)\u0000\u0000\u0000\u0000\u0000\u0000\u0000Ycom.android.build.vendor_boot.fingerprint\u0000alps/hal_mgvi_64_armv82/mgvi_64_armv82:12/SP1A.210812.016/1775721599816:user/release-keys\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000&\u0000\u0000\u0000\u0000\u0000\u0000\u0000Ycom.android.build.odm_dlkm.fingerprint\u0000alps/hal_mgvi_64_armv82/mgvi_64_armv82:12/SP1A.210812.016/1775721599816:user/release-keys\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000%\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.odm_dlkm.os_version\u000012\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000)\u0000\u0000\u0000\u0000\u0000\u0000\u0000Ycom.android.build.vendor_dlkm.fingerprint\u0000alps/hal_mgvi_64_armv82/mgvi_64_armv82:12/SP1A.210812.016/1775721599816:user/release-keys\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000(\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.vendor_dlkm.os_version\u000012\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "hash",
      "image_size": 36446208,
      "hash_algorithm": "sha256",
      "salt_len": 11,
      "digest_len": 16
    },
    {
      "tag": "hashtree",
      "image_size": 4294967296,
      "tree_offset": 1125899906842624,
      "tree_size": 1125899906842624,
      "data_block_size": 17592186048512,
      "hash_block_size": 17592186044418,
      "fdt_offset": 266240,
      "fdt_size": 8192
    },
    {
      "tag": "hashtree",
      "image_size": 4294967296,
      "tree_offset": 285028598291628032,
      "tree_size": 285028598291628032,
      "data_block_size": 2251799813689344,
      "hash_block_size": 17592186044418,
      "fdt_offset": 66887680,
      "fdt_size": 532480
    }
  ]
}
```

## vbmeta_system_a.img

### AVB

```json
{
  "magic": "AVB0",
  "required_major": 1,
  "required_minor": 0,
  "auth_block_size": 320,
  "auxiliary_block_size": 3264,
  "algorithm_type": 1,
  "hash_offset": 0,
  "hash_size": 32,
  "signature_offset": 32,
  "signature_size": 256,
  "public_key_offset": 2696,
  "public_key_size": 520,
  "public_key_metadata_offset": 3216,
  "public_key_metadata_size": 0,
  "descriptors_offset": 0,
  "descriptors_size": 2696,
  "rollback_index": 0,
  "flags": 0,
  "rollback_index_location": 0,
  "release_string": "avbtool 1.2.0",
  "descriptors": [
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000#\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.system.os_version\u000013\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000$\u0000\u0000\u0000\u0000\u0000\u0000\u0000_com.android.build.system.fingerprint\u0000alps/sys_mssi_64_cn_armv82/mssi_64_cn_armv82:13/TP1A.220905.001/1678012415445:user/release-keys\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000'\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.system.security_patch\u00002023-02-05\u0000\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000'\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.system.security_patch\u00002023-02-05\u0000\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000$\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.product.os_version\u000013\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000%\u0000\u0000\u0000\u0000\u0000\u0000\u0000_com.android.build.product.fingerprint\u0000alps/sys_mssi_64_cn_armv82/mssi_64_cn_armv82:13/TP1A.220905.001/1678012415445:user/release-keys\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000(\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.product.security_patch\u00002023-02-05\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000(\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.product.security_patch\u00002023-02-05\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000'\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.system_ext.os_version\u000013\u0000\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000(\u0000\u0000\u0000\u0000\u0000\u0000\u0000_com.android.build.system_ext.fingerprint\u0000alps/sys_mssi_64_cn_armv82/mssi_64_cn_armv82:13/TP1A.220905.001/1678012415445:user/release-keys\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000+\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.system_ext.security_patch\u00002023-02-05\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u00000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.oplus_custom_images.os_version\u000011\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u00004\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.oplus_custom_images.security_patch\u00002020-10-05\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000$\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.product.os_version\u000013\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000%\u0000\u0000\u0000\u0000\u0000\u0000\u0000_com.android.build.product.fingerprint\u0000alps/sys_mssi_64_cn_armv82/mssi_64_cn_armv82:13/TP1A.220905.001/1678012415445:user/release-keys\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000(\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.product.security_patch\u00002023-02-05\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000(\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.product.security_patch\u00002023-02-05\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u00000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.oplus_custom_images.os_version\u000011\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u00004\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.oplus_custom_images.security_patch\u00002020-10-05\u0000"
    },
    {
      "tag": "hashtree",
      "image_size": 4294967296,
      "tree_offset": 7054466603810816,
      "tree_size": 7054466603810816,
      "data_block_size": 87960930226176,
      "hash_block_size": 17592186044418,
      "fdt_offset": 1662976,
      "fdt_size": 16384
    },
    {
      "tag": "hashtree",
      "image_size": 4294967296,
      "tree_offset": 3247517543799193600,
      "tree_size": 3247517543799193600,
      "data_block_size": 25614222880673792,
      "hash_block_size": 17592186044416,
      "fdt_offset": 0,
      "fdt_size": 0
    },
    {
      "tag": "hashtree",
      "image_size": 4294967296,
      "tree_offset": 4337881234832097280,
      "tree_size": 4337881234832097280,
      "data_block_size": 34199209670348800,
      "hash_block_size": 17592186044416,
      "fdt_offset": 0,
      "fdt_size": 0
    }
  ]
}
```

## vbmeta_system_b.img

### AVB

```json
{
  "magic": "AVB0",
  "required_major": 1,
  "required_minor": 0,
  "auth_block_size": 320,
  "auxiliary_block_size": 2816,
  "algorithm_type": 1,
  "hash_offset": 0,
  "hash_size": 32,
  "signature_offset": 32,
  "signature_size": 256,
  "public_key_offset": 2272,
  "public_key_size": 520,
  "public_key_metadata_offset": 2792,
  "public_key_metadata_size": 0,
  "descriptors_offset": 0,
  "descriptors_size": 2272,
  "rollback_index": 0,
  "flags": 0,
  "rollback_index_location": 0,
  "release_string": "avbtool 1.2.0",
  "descriptors": [
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000#\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.system.os_version\u000016\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000$\u0000\u0000\u0000\u0000\u0000\u0000\u0000_com.android.build.system.fingerprint\u0000alps/sys_mssi_64_cn_armv82/mssi_64_cn_armv82:16/BP2A.250605.015/1775718162338:user/release-keys\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000'\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.system.security_patch\u00002026-04-01\u0000\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000$\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.product.os_version\u000016\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000%\u0000\u0000\u0000\u0000\u0000\u0000\u0000_com.android.build.product.fingerprint\u0000alps/sys_mssi_64_cn_armv82/mssi_64_cn_armv82:16/BP2A.250605.015/1775718162338:user/release-keys\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000(\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.product.security_patch\u00002026-04-01\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000'\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.system_ext.os_version\u000016\u0000\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000(\u0000\u0000\u0000\u0000\u0000\u0000\u0000_com.android.build.system_ext.fingerprint\u0000alps/sys_mssi_64_cn_armv82/mssi_64_cn_armv82:16/BP2A.250605.015/1775718162338:user/release-keys\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000+\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.system_ext.security_patch\u00002026-04-01\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u00000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.oplus_custom_images.os_version\u000011\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u00004\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.oplus_custom_images.security_patch\u00002020-10-05\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u00000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.oplus_custom_images.os_version\u000011\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u00004\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.oplus_custom_images.security_patch\u00002020-10-05\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u00000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.oplus_custom_images.os_version\u000011\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u00004\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.oplus_custom_images.security_patch\u00002020-10-05\u0000"
    },
    {
      "tag": "hashtree",
      "image_size": 4294967296,
      "tree_offset": 12508044277579776,
      "tree_size": 12508044277579776,
      "data_block_size": 123145302315008,
      "hash_block_size": 17592186044416,
      "fdt_offset": 0,
      "fdt_size": 0
    },
    {
      "tag": "hashtree",
      "image_size": 4294967296,
      "tree_offset": 4153743823505195008,
      "tree_size": 4153743823505195008,
      "data_block_size": 32739058228662272,
      "hash_block_size": 17592186044416,
      "fdt_offset": 0,
      "fdt_size": 0
    },
    {
      "tag": "hashtree",
      "image_size": 4294967296,
      "tree_offset": 4283626933071118336,
      "tree_size": 4283626933071118336,
      "data_block_size": 33759405019238400,
      "hash_block_size": 17592186044416,
      "fdt_offset": 0,
      "fdt_size": 0
    }
  ]
}
```

## vbmeta_vendor_a.img

### AVB

```json
{
  "magic": "AVB0",
  "required_major": 1,
  "required_minor": 0,
  "auth_block_size": 320,
  "auxiliary_block_size": 1280,
  "algorithm_type": 1,
  "hash_offset": 0,
  "hash_size": 32,
  "signature_offset": 32,
  "signature_size": 256,
  "public_key_offset": 744,
  "public_key_size": 520,
  "public_key_metadata_offset": 1264,
  "public_key_metadata_size": 0,
  "descriptors_offset": 0,
  "descriptors_size": 744,
  "rollback_index": 0,
  "flags": 0,
  "rollback_index_location": 0,
  "release_string": "avbtool 1.2.0",
  "descriptors": [
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000$\u0000\u0000\u0000\u0000\u0000\u0000\u0000Ycom.android.build.vendor.fingerprint\u0000alps/hal_mgvi_64_armv82/mgvi_64_armv82:12/SP1A.210812.016/1678055723093:user/release-keys\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000#\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.vendor.os_version\u000012\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000'\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.vendor.security_patch\u00002023-02-05\u0000\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u00000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.oplus_custom_images.os_version\u000011\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u00004\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.oplus_custom_images.security_patch\u00002020-10-05\u0000"
    },
    {
      "tag": "hashtree",
      "image_size": 4294967296,
      "tree_offset": 4723836204460539904,
      "tree_size": 4723836204460539904,
      "data_block_size": 37225065669988352,
      "hash_block_size": 17592186044416,
      "fdt_offset": 0,
      "fdt_size": 0
    }
  ]
}
```

## vbmeta_vendor_b.img

### AVB

```json
{
  "magic": "AVB0",
  "required_major": 1,
  "required_minor": 0,
  "auth_block_size": 320,
  "auxiliary_block_size": 1280,
  "algorithm_type": 1,
  "hash_offset": 0,
  "hash_size": 32,
  "signature_offset": 32,
  "signature_size": 256,
  "public_key_offset": 744,
  "public_key_size": 520,
  "public_key_metadata_offset": 1264,
  "public_key_metadata_size": 0,
  "descriptors_offset": 0,
  "descriptors_size": 744,
  "rollback_index": 0,
  "flags": 0,
  "rollback_index_location": 0,
  "release_string": "avbtool 1.2.0",
  "descriptors": [
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000$\u0000\u0000\u0000\u0000\u0000\u0000\u0000Ycom.android.build.vendor.fingerprint\u0000alps/hal_mgvi_64_armv82/mgvi_64_armv82:12/SP1A.210812.016/1775721599816:user/release-keys\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000#\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.vendor.os_version\u000012\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u0000'\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.vendor.security_patch\u00002026-04-01\u0000\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u00000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0002com.android.build.oplus_custom_images.os_version\u000011\u0000\u0000\u0000\u0000\u0000"
    },
    {
      "tag": "property",
      "key": "",
      "value": "\u0000\u0000\u0000\u0000\u0000\u00004\u0000\u0000\u0000\u0000\u0000\u0000\u0000\ncom.android.build.oplus_custom_images.security_patch\u00002020-10-05\u0000"
    },
    {
      "tag": "hashtree",
      "image_size": 4294967296,
      "tree_offset": 4352834592969850880,
      "tree_size": 4352834592969850880,
      "data_block_size": 34322354972659712,
      "hash_block_size": 17592186044416,
      "fdt_offset": 0,
      "fdt_size": 0
    }
  ]
}
```
