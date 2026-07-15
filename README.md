# TWRP Device Tree for Lenovo Tab M11 (TB330FU)

This repository contains the Android device tree configuration required to compile Team Win Recovery Project (TWRP) for the **Lenovo Tab M11 (TB330FU)** (MediaTek MT8786 / MT6768 platform).

---

## 🤖 AI-Assisted Development
This device tree and its associated recovery fixes were developed in a pair-programming collaboration between the repository owner and **Antigravity**, Google DeepMind's agentic AI coding assistant. 

---

## 🚀 Status (TL;DR)

| Feature | Status | Notes |
| :--- | :--- | :--- |
| **Boot Recovery** | **Works** | TWRP boots successfully via repacked `vendor_boot`. |
| **Touchscreen** | **Works** | Novatek SPI Touch Panel driver firmware (`novatek_ts_tcl_fw.bin`) compiled natively. |
| **Dynamic Partitions** | **Works** | Mapping `/system`, `/vendor`, and `/product` logical partitions from the `super` device mapper is fully functional. |
| **ADB / minadbd** | **Works** | Native dynamic ADB compiled-in; ConfigFS USB controllers resolved. |
| **Decryption / Data** | **WIP** | Undergoing filesystem validation. |
| **Normal Boot (Android)**| **Standalone Mode** | Flashing this TWRP image causes normal Android (LineageOS GSI) to bootloop. Because the MediaTek bootloader and kernel decompress the recovery ramdisk during normal boot, it creates init and file structure conflicts. To use both, you must flash the stock/patched `vendor_boot` to boot Android, and this repacked TWRP image to boot TWRP. |

---

## 🛠️ Build & Compilation

To compile the `vendor_boot` image containing TWRP, follow these steps:

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

## 🔧 Repacking & Flashing (Recovery-Only Mode)

Lenovo Tab M11 is a Generic Kernel Image (GKI) device where the recovery ramdisk resides inside the `vendor_boot` partition. To prevent bootloader signature checks and load TWRP successfully with dynamic mounts and working touchscreen, you must repack the compiled TWRP image using the stock base:

1. Clone this repository on your computer.
2. Ensure you have the `magiskboot` binary and the `unpack_bootimg.py` / `mkbootimg.py` utilities in the parent folder.
3. Run the interactive repacking script:
   ```bash
   python3 repack_twrp.py
   ```
4. Flash the resulting repacked image (`twrp_tb330fu_touch_working.img`) in Fastboot mode:
   ```bash
   fastboot flash vendor_boot_a twrp_tb330fu_touch_working.img
   fastboot flash vendor_boot_b twrp_tb330fu_touch_working.img
   fastboot reboot-recovery
   ```

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
