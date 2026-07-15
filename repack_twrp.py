#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import shlex

def modify_rc_file(rc_path):
    print(f"Modifying rc file: {rc_path}")
    with open(rc_path, "r") as f:
        content = f.read()
    modified_content = content.replace("on fs && property:ro.debuggable=0", "on fs")
    with open(rc_path, "w") as f:
        f.write(modified_content)

def strip_avb(fstab_path):
    print(f"Stripping AVB options from: {fstab_path}")
    with open(fstab_path, "r") as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            new_lines.append(line)
            continue
        
        parts = stripped.split()
        if len(parts) >= 5:
            opts = parts[4].split(",")
            new_opts = []
            for opt in opts:
                if opt.startswith("avb") or opt.startswith("avb_keys"):
                    continue
                new_opts.append(opt)
            parts[4] = ",".join(new_opts)
            new_lines.append("\t".join(parts) + "\n")
        else:
            new_lines.append(line)
            
    with open(fstab_path, "w") as f:
        f.writelines(new_lines)

def main():
    print("=" * 60)
    print("  LENOVO TAB M11 (TB330FU) TWRP RECOVERY REPACKER")
    print("=" * 60)
    
    base_dir = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.dirname(base_dir)
    
    # Path to magiskboot (expected to be in parent directory or system path)
    magiskboot = os.path.join(parent_dir, "magiskboot")
    if not os.path.exists(magiskboot):
        magiskboot = shutil.which("magiskboot")
        if not magiskboot:
            print("[ERROR] 'magiskboot' binary not found! Please place it in the parent directory.")
            sys.exit(1)
            
    # Input paths
    compiled_img = input("Path to compiled TWRP vendor_boot.img [default: ../TWRP-TB330FU-twrp-12.1/vendor_boot.img]: ").strip()
    if not compiled_img:
        compiled_img = os.path.join(parent_dir, "TWRP-TB330FU-twrp-12.1/vendor_boot.img")
        
    stock_img = input("Path to stock/patched vendor_boot image [default: ../TB330FU_backup/vendor_boot_a.bin]: ").strip()
    if not stock_img:
        stock_img = os.path.join(parent_dir, "TB330FU_backup/vendor_boot_a.bin")
        if not os.path.exists(stock_img):
            stock_img = os.path.join(parent_dir, "TB330FU_boot_patched/patched_vendor_boot_a.bin")
            
    output_img = input("Output file path [default: ../twrp_tb330fu_touch_working.img]: ").strip()
    if not output_img:
        output_img = os.path.join(parent_dir, "twrp_tb330fu_touch_working.img")

    if not os.path.exists(compiled_img):
        print(f"[ERROR] Compiled image not found at '{compiled_img}'!")
        sys.exit(1)
    if not os.path.exists(stock_img):
        print(f"[ERROR] Stock/patched base image not found at '{stock_img}'!")
        sys.exit(1)

    print("\n[1/7] Decompressing recovery ramdisk from compiled TWRP image...")
    compiled_out_dir = os.path.join(base_dir, "temp_compiled_unpacked")
    os.makedirs(compiled_out_dir, exist_ok=True)
    
    subprocess.run([
        sys.executable, 
        os.path.join(parent_dir, "unpack_bootimg.py"), 
        "--boot_img", compiled_img, 
        "--out", compiled_out_dir
    ], check=True)
    
    compiled_ramdisk_fragment = os.path.join(compiled_out_dir, "vendor_ramdisk01")
    twrp_cpio = os.path.join(base_dir, "temp_twrp.cpio")
    if os.path.exists(twrp_cpio):
        os.remove(twrp_cpio)
        
    subprocess.run([magiskboot, "decompress", compiled_ramdisk_fragment, twrp_cpio], check=True)

    # Modify property and configuration files
    print("[2/7] Injecting USB and adb settings in prop.default...")
    prop_path = os.path.join(base_dir, "prop_temp.default")
    if os.path.exists(prop_path):
        os.remove(prop_path)
    subprocess.run([magiskboot, "cpio", twrp_cpio, f"extract prop.default {prop_path}"], check=True)

    with open(prop_path, "r") as f:
        lines = f.readlines()
    
    modified_lines = []
    for line in lines:
        if "persist.sys.usb.config=" in line:
            modified_lines.append("persist.sys.usb.config=mtp,adb\n")
        else:
            modified_lines.append(line)
            
    modified_lines.append("\n# Recovery ConfigFS configurations\n")
    modified_lines.append("ro.recovery.usb.vid=18D1\n")
    modified_lines.append("ro.recovery.usb.adb.pid=D001\n")
    modified_lines.append("ro.recovery.usb.fastboot.pid=4EE0\n")

    with open(prop_path, "w") as f:
        f.writelines(modified_lines)

    subprocess.run([magiskboot, "cpio", twrp_cpio, f"add 644 prop.default {prop_path}"], check=True)
    os.remove(prop_path)

    # Remove conflicting rc
    subprocess.run([magiskboot, "cpio", twrp_cpio, "rm init.recovery.usb.rc"], capture_output=True)

    # Modify MediaTek triggers
    print("[3/7] Modifying MTK recovery service triggers...")
    for rc_file in ["init.recovery.mt6768.rc", "init.recovery.mt8786.rc"]:
        temp_rc_path = os.path.join(base_dir, f"temp_{rc_file}")
        if os.path.exists(temp_rc_path): os.remove(temp_rc_path)
        subprocess.run([magiskboot, "cpio", twrp_cpio, f"extract {rc_file} {temp_rc_path}"], check=True)
        modify_rc_file(temp_rc_path)
        subprocess.run([magiskboot, "cpio", twrp_cpio, f"add 755 {rc_file} {temp_rc_path}"], check=True)
        os.remove(temp_rc_path)

    print("[4/7] Decompressing base stock/patched recovery ramdisk...")
    base_unpacked_dir = os.path.join(base_dir, "temp_base_unpacked")
    os.makedirs(base_unpacked_dir, exist_ok=True)
    subprocess.run([
        sys.executable, 
        os.path.join(parent_dir, "unpack_bootimg.py"), 
        "--boot_img", stock_img, 
        "--out", base_unpacked_dir
    ], check=True)
    
    stock_cpio = os.path.join(base_dir, "temp_stock.cpio")
    stock_ramdisk_fragment = os.path.join(base_unpacked_dir, "vendor_ramdisk01")
    subprocess.run([magiskboot, "decompress", stock_ramdisk_fragment, stock_cpio], check=True)

    # Extract stock binaries for dynamic linker matching
    print("[5/7] Injecting stock adbd and minadbd binaries...")
    adbd_temp = os.path.join(base_dir, "adbd_temp")
    minadbd_temp = os.path.join(base_dir, "minadbd_temp")
    subprocess.run([magiskboot, "cpio", stock_cpio, f"extract system/bin/adbd {adbd_temp}"], check=True)
    subprocess.run([magiskboot, "cpio", stock_cpio, f"extract system/bin/minadbd {minadbd_temp}"], check=True)
    subprocess.run([magiskboot, "cpio", twrp_cpio, f"add 755 system/bin/adbd {adbd_temp}"], check=True)
    subprocess.run([magiskboot, "cpio", twrp_cpio, f"add 755 system/bin/minadbd {minadbd_temp}"], check=True)
    os.remove(adbd_temp)
    os.remove(minadbd_temp)

    # Extract and modify fstab files to bypass AVB/verity dynamic partition locks
    print("[6/7] Injecting stripped fstab context configurations...")
    subprocess.run([magiskboot, "cpio", twrp_cpio, "mkdir 755 first_stage_ramdisk"], capture_output=True)
    f1_temp = os.path.join(base_dir, "f1_temp")
    f2_temp = os.path.join(base_dir, "f2_temp")
    subprocess.run([magiskboot, "cpio", stock_cpio, f"extract first_stage_ramdisk/fstab.mt8786 {f1_temp}"], check=True)
    subprocess.run([magiskboot, "cpio", stock_cpio, f"extract first_stage_ramdisk/fstab.mt8786dm {f2_temp}"], check=True)
    strip_avb(f1_temp)
    strip_avb(f2_temp)
    subprocess.run([magiskboot, "cpio", twrp_cpio, f"add 644 first_stage_ramdisk/fstab.mt8786 {f1_temp}"], check=True)
    subprocess.run([magiskboot, "cpio", twrp_cpio, f"add 644 first_stage_ramdisk/fstab.mt8786dm {f2_temp}"], check=True)
    os.remove(f1_temp)
    os.remove(f2_temp)

    # Repack
    print("[7/7] Repacking into final TWRP recovery-only image...")
    twrp_lz4 = os.path.join(base_dir, "temp_twrp.lz4")
    if os.path.exists(twrp_lz4): os.remove(twrp_lz4)
    subprocess.run([magiskboot, "compress=lz4_legacy", twrp_cpio, twrp_lz4], check=True)

    res = subprocess.run([
        sys.executable, 
        os.path.join(parent_dir, "unpack_bootimg.py"), 
        "--boot_img", stock_img, 
        "--format", "mkbootimg"
    ], capture_output=True, text=True, check=True)
    args_str = res.stdout.strip()
    args_list = shlex.split(args_str)

    rebuilt_args = []
    i = 0
    while i < len(args_list):
        arg = args_list[i]
        if arg in ["--dtb", "--vendor_bootconfig", "--vendor_ramdisk_fragment"]:
            val = args_list[i+1]
            if val.startswith("out/"):
                val = val.replace("out/", base_unpacked_dir + "/")
            if "vendor_ramdisk01" in val:
                val = twrp_lz4
            rebuilt_args.append(arg)
            rebuilt_args.append(val)
            i += 2
        else:
            rebuilt_args.append(arg)
            rebuilt_args.append(args_list[i+1])
            i += 2

    subprocess.run([sys.executable, os.path.join(parent_dir, "mkbootimg.py")] + rebuilt_args + ["--vendor_boot", output_img], check=True)

    # Clean up
    shutil.rmtree(compiled_out_dir)
    shutil.rmtree(base_unpacked_dir)
    os.remove(twrp_cpio)
    os.remove(stock_cpio)
    os.remove(twrp_lz4)

    print("=" * 60)
    print(" SUCCESS! TWRP-only recovery image is ready at:")
    print(f" {output_img}")
    print("=" * 60)

if __name__ == "__main__":
    main()
