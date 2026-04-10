[app]
title = Kouda Tactical
package.name = koda
package.domain = org.triskanv
source.dir = .
source.include_exts = py,png,jpg,kv,json
version = 1.0.1

# REQUERIMIENTOS LIMPIOS (Sin hostpython3)
requirements = python3, kivy==2.3.0, kivymd, pillow, certifi

orientation = portrait
fullscreen = 1
android.presplash_color = #0F0F0F
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.permissions = INTERNET

# VERSIONES ESTABLES
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# ESTO ES LO QUE FALTABA: Forzar la descarga si no existe
android.skip_update = False
android.force_build = False

[buildozer]
log_level = 2
warn_on_root = 1
