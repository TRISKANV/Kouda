[app]

# (str) Title of your application
title = Kouda Tactical

# (str) Package name
package.name = koda

# (str) Package domain (needed for android packaging)
package.domain = org.triskanv

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,json

# (str) Application versioning (method 1)
version = 1.0.1

# (list) Application requirements
# NOTA: Agregamos 'requests' por si lo usas y aseguramos versiones estables
requirements = python3, kivy==2.3.0, kivymd==1.2.0, pillow, certifi, openssl, hostpython3

# (str) Supported orientation (one of landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# --- PRE-SPLASH / LOADING SCREEN CONTROL ---
# Ponemos el color de fondo igual al de tu app (#0F0F0F)
android.presplash_color = #0F0F0F

# ESTA LÍNEA ES LA MAGIA: Permite que la UI se dibuje mientras el splash está activo,
# haciendo que desaparezca mucho más rápido o sea casi invisible.
android.meta_data = android.window.allow_ui_interaction_during_splash=true

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
android.ndk_path = 

# (list) The Android architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Allow backup
android.allow_backup = True

# (bool) Accept SDK license
android.accept_sdk_license = True

# --- OTROS AJUSTES ---
android.skip_update = False
android.force_build = False

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1
