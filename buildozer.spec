[app]
title = Sttiten Update
package.name = sttitenupdate
package.domain = org.sttiten

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0
requirements = python3,kivy==2.2.1,tftpy

orientation = portrait
fullscreen = 0

# الصلاحيات المطلوبة في نظام الأندرويد
android.permissions = INTERNET, ACCESS_NETWORK_STATE, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.skip_update = False
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
