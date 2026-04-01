[app]
title = Koda Tactical
package.name = koda.app.tactical
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,json
version = 0.1

# REQUERIMIENTOS: Aquí está la magia nativa
requirements = python3,kivy==2.2.1,valve-python,certifi

orientation = portrait
fullscreen = 1
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# PERMISOS: Adiós al CORS y a los proxies
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1
