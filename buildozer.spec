[app]

# (Sección 1) Información de la App
title = Koda Tactical
package.name = koda.app.tactical
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,json
version = 0.1

# (Sección 2) Requerimientos
# Nota: He dejado los esenciales. Si 'valve-python' falla, 
# prueba quitándolo primero para asegurar que el APK base salga.
requirements = python3,kivy==2.2.1,valve-python,certifi,setuptools

orientation = portrait
fullscreen = 1

# (Sección 3) Configuración Crítica para GitHub Actions
# IMPORTANTE: Solo dejamos una arquitectura para evitar que el servidor se quede sin RAM.
android.archs = arm64-v8a
android.allow_backup = True

# (Sección 4) Permisos
android.permissions = INTERNET

# (Sección 5) Versiones de Android (Alineadas con Ubuntu 24.04)
# Usar API 33 o 34 es lo más estable para evitar errores de licencias antiguas.
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# (Sección 6) Python for Android - Rama Master
# Esto soluciona muchos errores de compilación en sistemas Linux nuevos.
p4a.branch = master

[buildozer]
# Nivel 1 para que el log no sea infinito y corte la conexión de GitHub.
log_level = 1
warn_on_root = 1

# --- Fin del archivo ---
