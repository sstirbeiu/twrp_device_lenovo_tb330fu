#
# Copyright (C) 2024 The Android Open Source Project
# Copyright (C) 2024 SebaUbuntu's TWRP device tree generator
#
# SPDX-License-Identifier: Apache-2.0
#

# Inherit from those products. Most specific first.
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)

# Inherit some common TWRP stuff.
$(call inherit-product, vendor/twrp/config/common.mk)

# Inherit from TB330FU device
$(call inherit-product, device/lenovo/TB330FU/device.mk)

PRODUCT_DEVICE := TB330FU
PRODUCT_NAME := omni_TB330FU
PRODUCT_BRAND := Lenovo
PRODUCT_MODEL := TB330FU
PRODUCT_MANUFACTURER := lenovo

PRODUCT_GMS_CLIENTID_BASE := android-lenovo

PRODUCT_BUILD_PROP_OVERRIDES += \
    PRIVATE_BUILD_DESC="vnd_barley_prc_commercial_wifi-user 12 SP1A.210812.016 1rctb8786p164P20 test-keys"

BUILD_FINGERPRINT := Lenovo/TB330FU/TB330FU:12/SP1A.210812.016/42__PRC:user/test-keys
