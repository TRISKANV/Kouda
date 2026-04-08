[app]

# (Sección 1) Información de la App
title = Kouda Tactical
package.name = koda
package.domain = org.triskanv
source.dir = .
source.include_exts = py,png,jpg,kv,json
version = 1.0.1

# (Sección 2) Requerimientos
# Incluimos pillow para las sombras y kivymd para la interfaz
requirements = python3, kivy==2.3.0, kivymd, pillow, certifi, hostpython3

orientation = portrait
fullscreen = 1

# (Sección 3) Estética de Carga (SOLUCIÓN AL "LOADING")
# Usamos el color #0F0F0F para que coincida con el fondo de tu app
android.presplash_color = #0F0F0F

# (Sección 4) Configuración de Compatibilidad
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# (Sección 5) Permisos
android.permissions = INTERNET

# (Sección 6) Versiones de Android
android.api = 34
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# (Sección 7) Python for Android
p4a.branch = master

[buildozer]
# Nivel 2 para ver errores detallados si algo fallara en el servidor de GitHub
log_level = 2
warn_on_root = 1
