[app]
title = Koda Tactical
package.name = koda.app.tactical
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,json
version = 0.1

requirements = python3,kivy==2.2.1,valve-python,certifi,setuptools,Cython==0.29.33

orientation = portrait
fullscreen = 1
android.archs = arm64-v8a
android.allow_backup = True
android.permissions = INTERNET

# --- ESTO ES LO QUE FALTABA ---
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
# ------------------------------

[buildozer]
log_level = 2
warn_on_root = 1
