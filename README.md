# TWRP Device Tree for Lenovo Tab M11 (TB330FU)

This repository contains the Android device tree configuration required to compile Team Win Recovery Project (TWRP) for the **Lenovo Tab M11 (TB330FU)** (MediaTek MT8786 / MT6768 platform).

---

## ⚠️ Disclaimer

```text
/*
 * Your warranty is now void.
 *
 * I am not responsible for bricked devices, dead SD cards,
 * thermonuclear war, or you getting fired because the alarm app failed. Please
 * do some research if you have any concerns about features included in this ROM/Recovery
 * before flashing it! You are choosing to make these modifications, and if
 * you point the finger at me for messing up your device, I will laugh at you.
 */
```

---

## 🤖 AI-Assisted Development

This device tree, dynamic touch screen firmware injection, ConfigFS USB/ADB resolution, and slot-specific dual-ramdisk repack mechanisms were developed in a pair-programming collaboration between the repository owner and:
- **Antigravity** (Google DeepMind's agentic AI coding assistant, using the **Gemini 3.5 Flash** model)
- **Claude 4.6 (thinking)** (used during critical stage ramoops crash log parsing and dual-slot debugging)

---

## 🚀 Status

| Feature | Status | Notes |
| :--- | :--- | :--- |
| **Boot Recovery** | **Works** | TWRP boots successfully via repacked `vendor_boot`. |
| **Touchscreen** | **Works** | Novatek SPI Touch Panel driver firmware (`novatek_ts_tcl_fw.bin`) compiled natively. |
| **Dynamic Partitions** | **Works** | Mapping `/system`, `/vendor`, and `/product` logical partitions from the `super` device mapper is fully functional. |
| **ADB Shell** | **Works** | Native dynamic ADB compiled-in; shell access works. |
| **Normal Boot (Android)**| **Works** | Using the dual-slot repack script, Android (LineageOS GSI) and TWRP boot successfully together. |
| **Decryption / Data** | **Broken** | Fails to mount `/data` with "Invalid argument" (common on FBE v2 / GKI devices). |
| **MTP** | **Broken** | Media Transfer Protocol is not working due to missing ConfigFS routing. |
| **ADB Sideload** | **Broken** | Sideload hangs and device is not recognized in sideload mode due to missing ConfigFS routing. |
| **USB OTG** | **Partial** | Manual mount via shell works, but does not appear in the TWRP Mount menu. |

---

## 📲 Prerequisites & Unlocking

Before flashing anything to your device:

1. **Unlock the Bootloader**: You must unlock your bootloader. Since MediaTek devices can be tricky, it is highly recommended to use [mtkclient](https://github.com/bkerler/mtkclient) to bypass lock restrictions and unlock the bootloader:
   ```bash
   python mtk oem unlock
   ```
2. **Back up your Partitions**: Do a full partition backup of your device using `mtkclient` or fastboot before writing custom images:
   ```bash
   python mtk r vendor_boot_a,vendor_boot_b backup_vendor_boot.bin
   ```
   Keep these backups safe in case you need to revert to stock.

---

## 🛠️ Build & Compilation

To compile the base `vendor_boot` image containing TWRP:

### 1. Set Up the Build Environment
Initialize your Android build environment (Android 12.1 / TWRP-12 branch):
```bash
repo init -u https://github.com/minimal-manifest-twrp/platform_manifest_twrp_aosp.git -b twrp-12.1
repo sync -c -j$(nproc)
```

### 2. Clone the Device Tree
Clone this repository into the appropriate path:
```bash
git clone https://github.com/sstirbeiu/twrp_device_lenovo_tb330fu.git device/lenovo/TB330FU
```

### 3. Compile
```bash
. build/envsetup.sh
lunch omni_TB330FU-eng
mka vendorbootimage
```

The compiled output will be generated at `out/target/product/TB330FU/vendor_boot.img`.

---

## 🔧 Repacking & Flashing (Dual-Slot A/B Repack)

Because the Lenovo Tab M11 is a Generic Kernel Image (GKI) device, the recovery ramdisk resides inside the `vendor_boot` partition. Slot A and Slot B contain different kernel modules and slot-specific fstab mounts required for Android (GSI) to boot successfully. To prevent bootloops and keep both Android and TWRP functioning, you must use the slot-specific repacker:

1. Clone this repository on your computer.
2. The repository includes all required repacking helper scripts under the `repack_tools/` directory.
3. Run the repacking script:
   ```bash
   python3 repack_twrp.py
   ```
   *Note: The script will ask for the path to your compiled TWRP image, and the path to your working patched `vendor_boot_a` and `vendor_boot_b` images.*
4. The repacker will produce two slot-specific images:
   - `twrp_tb330fu_dual_a.img`
   - `twrp_tb330fu_dual_b.img`
5. Flash them to their respective slots in Fastboot mode:
   ```bash
   fastboot flash vendor_boot_a twrp_tb330fu_dual_a.img
   fastboot flash vendor_boot_b twrp_tb330fu_dual_b.img
   fastboot reboot
   ```

---

## 🤝 Acknowledgements & Thanks

- **DiaoLin** (for the base MT8786 device tree)
- **TeamWin** (for the recovery platform)
- **AOSP** & the Android developer community
- The contributors of **mtkclient** and **magiskboot** utilities

---

## 📄 License
```
Copyright (C) 2026 The Android Open Source Project
Copyright (C) 2026 SebaUbuntu's TWRP device tree generator

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
