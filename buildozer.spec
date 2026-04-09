[app]

# (Sección 1) Información de la App
title = Kouda Tactical
package.name = koda
package.domain = org.triskanv
source.dir = .
source.include_exts = py,png,jpg,kv,json
version = 1.0.1

# (Sección 2) Requerimientos
# ELIMINAMOS 'hostpython3' de aquí para evitar el AttributeError
requirements = python3, kivy==2.3.0, kivymd, pillow, certifi

orientation = portrait
fullscreen = 1

# (Sección 3) Estética de Carga
android.presplash_color = #0F0F0F

# (Sección 4) Configuración de Compatibilidad
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# (Sección 5) Permisos
android.permissions = INTERNET

# (Sección 6) Versiones de Android
# Bajamos a API 33 para máxima estabilidad con el NDK 25b
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# (Sección 7) Python for Android
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
