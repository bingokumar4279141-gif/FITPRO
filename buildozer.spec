[app]
title = FITPRO
package.name = fitpro
package.domain = org.fitpro

source.dir = .
source.include_exts = py,png,jpg,kv,ttf

version = 1.0

requirements = kivy==2.1.0,plyer,pillow

orientation = portrait

# --- Android specific ---
android.permissions = ACTIVITY_RECOGNITION,READ_PHONE_STATE,INTERNET
android.api = 31
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True

# For real step counter access on Android 10+
# ACTIVITY_RECOGNITION permission is required for access to the step counter sensor
android.features = android.hardware.sensor.stepcounter

[buildozer]
log_level = 2
warn_on_root = 1
