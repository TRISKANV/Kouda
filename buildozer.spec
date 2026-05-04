[app]

# (str) Title of your application
title = Kouda Tactical

# (str) Package name
package.name = koda

# (str) Package domain (needed for android packaging)
package.domain = org.triskanv

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,json

# (str) Application versioning
version = 1.0.1

# --- REQUIREMENTS (ACTUALIZADOS PARA V6) ---
# Se agregaron: requests, urllib3, idna (para Geo-IP) y certifi/openssl (para HTTPS)
requirements = python3, kivy==2.3.0, kivymd@https://github.com/kivymd/KivyMD/archive/master.zip, pillow, requests, urllib3, idna, certifi, openssl

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# --- INTERFAZ Y SPLASH ---
android.presplash_color = #0F0F0F
android.meta_data = android.window.allow_ui_interaction_during_splash=true

# --- PERMISOS ---
# INTERNET para los servidores y FOREGROUND_SERVICE para que la vigilancia no muera al minimizar
android.permissions = INTERNET, FOREGROUND_SERVICE

# (int) Target Android API
android.api = 33

# (int) Minimum API
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (list) The Android architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Accept SDK license
android.accept_sdk_license = True

# --- AJUSTES DE COMPILACIÓN ---
android.skip_update = False
android.force_build = False

[buildozer]
# (int) Log level (2 = debug para ver errores de red si ocurren)
log_level = 2
warn_on_root = 1
