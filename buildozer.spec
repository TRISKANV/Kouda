[app]

# (Sección 1) Información de la App
title = Koda Tactical
package.name = kodatacticalpro
package.domain = org.triskanv
source.dir = .
source.include_exts = py,png,jpg,kv,json
version = 1.0.0

# (Sección 2) Requerimientos
# Usamos solo lo esencial para que el build sea rápido y no falle
requirements = python3,kivy==2.2.1,certifi

orientation = portrait
fullscreen = 1

# (Sección 3) Configuración de Compatibilidad (CRÍTICO)
# Incluimos 32 y 64 bits para que funcione en CUALQUIER celular
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# (Sección 4) Permisos
android.permissions = INTERNET

# (Sección 5) Versiones de Android y SDK
# API 33 es el estándar actual de Google Play (Android 13)
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_path = 
android.sdk_path = 
android.accept_sdk_license = True

# (Sección 6) Python for Android - Configuración Avanzada
p4a.branch = master

# (Sección 7) Estética del Icono (Opcional por ahora)
# android.presplash_color = #010105
# android.icon.adaptive_foreground.filename = %(source.dir)s/icon.png

[buildozer]
# Nivel de log 2 para ver errores detallados si algo falla
log_level = 2
warn_on_root = 1

# --- FIN DEL ARCHIVO ---
