[app]
# (Sección 1) Información de la App
title = Kouda Tactical
package.name = koda
package.domain = org.triskanv
source.dir = .
source.include_exts = py,png,jpg,kv,json
version = 1.0.1

# (Sección 2) Requerimientos - ESTO EVITA EL CRASH
requirements = python3, kivy==2.3.0, kivymd, pillow, certifi, hostpython3

orientation = portrait
fullscreen = 1

# (Sección 3) Configuración de Compatibilidad
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# (Sección 4) Permisos
android.permissions = INTERNET

# (Sección 5) Versiones de Android (Actualizado a API 34)
android.api = 34
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# (Sección 6) Python for Android
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
