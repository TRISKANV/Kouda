[app]
title = Koda Tactical
package.name = koda.app.tactical
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,json
version = 0.1

# Paso 1: Solo lo básico para que el compilador no explote
requirements = python3,kivy==2.2.1,certifi

orientation = portrait
fullscreen = 1
android.archs = arm64-v8a
android.allow_backup = True
android.permissions = INTERNET

# Paso 2: Forzamos versiones ultra-estables
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# Paso 3: Usamos la rama master de p4a para compatibilidad con Ubuntu nuevo
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
