[app]
title = Kouda Tactical
package.name = koda
package.domain = org.triskanv
source.dir = .
source.include_exts = py,png,jpg,kv,json
version = 1.0.1

# REQUERIMIENTOS
requirements = python3, kivy==2.3.0, kivymd, pillow, certifi

orientation = portrait
fullscreen = 1
android.presplash_color = #0F0F0F
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.permissions = INTERNET

# VERSIONES DE MÁXIMA COMPATIBILIDAD
android.api = 33
android.minapi = 21
# Cambiamos a r23b porque la r25b está fallando en el runner de GitHub
android.ndk = 23b
android.accept_sdk_license = True

android.skip_update = False
android.force_build = False

[buildozer]
log_level = 2
warn_on_root = 1
