[app]

# (str) Title of your application
title = Sttiten Update

# (str) Package name
package.name = sttitenupdate

# (str) Package domain (needed for android/ios packaging)
package.domain = org.sttiten

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,txt

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# يمكنك إضافة أي مكتبات أخرى يحتاجها تطبيقك هنا مفصولة بفاصلة
requirements = python3,kivy

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# android.permissions = INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API supported
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (bool) If True, then skip trying to update the Android sdk
android.skip_update = False

# (bool) If True, then accept all SDK licenses encountered
android.accept_sdk_licenses = True

# (list) The Android architectures to build for (حصر المعمارية على ARM7 فقط)
android.archs = armeabi-v7a

# (bool) Enable AndroidX
android.enable_androidx = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = disable, 1 = enable)
warn_on_root = 1
