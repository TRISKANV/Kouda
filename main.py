from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.properties import StringProperty, ListProperty

# Configuración de ventana para pruebas en PC (simula móvil)
Window.clearcolor = (0.02, 0.02, 0.03, 1) # Fondo azul-negro muy oscuro
Window.size = (360, 640)

# ==========================================
# DEFINICIÓN DE LA ESTÉTICA (Lenguaje KV)
# ==========================================
KV = """
# Definimos colores globales para reusar
#:set color_back [0.02, 0.02, 0.03, 1]      # Fondo Profundo
#:set color_neon [0.0, 1.0, 0.25, 1]       # Verde Neón Koda
#:set color_neon_dim [0.0, 1.0, 0.25, 0.2] # Neón atenuado para bordes

# --- Estilo Global para Botones Tácticos ---
<TacticalButton@Button>:
    background_normal: ''
    background_down: ''
    background_color: [0, 0, 0, 0] # Hacemos el fondo nativo invisible
    color: color_neon              # Texto en neón
    font_size: '16sp'
    bold: True
    size_hint_y: None
    height: '55dp'
    
    # Dibujamos el borde neón manualmente
    canvas.before:
        Color:
            rgba: color_neon if self.state == 'normal' else [1, 1, 1, 0.1]
        Line:
            width: 1.5 if self.state == 'normal' else 2
            rectangle: (self.x, self.y, self.width, self.height)
            
        # Efecto de 'resplandor' (Glow) suave detrás del borde
        Color:
            rgba: color_neon_dim if self.state == 'normal' else [1, 1, 1, 0.05]
        Line:
            width: 3
            rectangle: (self.x-1, self.y-1, self.width+2, self.height+2)

# --- Estilo para Tarjetas de Servidor ---
<ServerCard@BoxLayout>:
    orientation: 'horizontal'
    size_hint_y: None
    height: '80dp'
    padding: '10dp'
    spacing: '10dp'
    server_name: ''
    server_ip: ''
    player_count: ''
    
    # Borde de la tarjeta
    canvas.before:
        Color:
            rgba: [0.1, 0.1, 0.15, 1] # Fondo de la tarjeta un poco más claro
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: color_neon_dim
        Line:
            width: 1
            rectangle: (self.x, self.y, self.width, self.height)

    Label:
        text: root.server_name
        text_size: self.size
        halign: 'left'
        valign: 'middle'
        color: [1, 1, 1, 1]
        bold: True
        font_size: '16sp'
        size_hint_x: 0.7
        
    BoxLayout:
        orientation: 'vertical'
        size_hint_x: 0.3
        Label:
            text: root.player_count
            color: color_neon
            font_size: '20sp'
            bold: True
        Label:
            text: "PLAYERS"
            color: [0.6, 0.6, 0.6, 1]
            font_size: '10sp'

# ==========================================
# DEFINICIÓN DE PANTALLAS (Lógica)
# ==========================================
ScreenManager:
    MenuScreen:
    ServerListScreen:

<MenuScreen>:
    name: 'menu'
    BoxLayout:
        orientation: 'vertical'
        padding: ['20dp', '60dp', '20dp', '20dp']
        spacing: '20dp'

        # Logo/Título Táctico
        Label:
            text: "KODA\\nTACTICAL"
            font_size: '40sp'
            bold: True
            color: color_neon
            halign: 'center'
            valign: 'middle'
            size_hint_y: None
            height: '120dp'
            # Efecto de texto 'Cyber' (opcional si tienes la fuente)
            # font_name: 'path/to/cyber_font.ttf' 

        # Subtítulo/Estado
        Label:
            text: "OPERATOR_ID: TRISKANV | STATUS: ONLINE"
            font_size: '12sp'
            color: [0.5, 0.5, 0.5, 1]
            size_hint_y: None
            height: '30dp'

        Widget: # Espaciador flexible

        # Botones Principales
        TacticalButton:
            text: "BUSCAR SERVIDORES"
            on_release: app.root.current = 'servers'
            
        TacticalButton:
            text: "ESTADO DE RED"
            color: [0.5, 0.5, 0.5, 1] # Deshabilitado estéticamente
            
        TacticalButton:
            text: "CONFIGURACIÓN"
            color: [0.5, 0.5, 0.5, 1] # Deshabilitado estéticamente

<ServerListScreen>:
    name: 'servers'
    BoxLayout:
        orientation: 'vertical'
        
        # Barra superior (Header)
        BoxLayout:
            size_hint_y: None
            height: '60dp'
            padding: '10dp'
            canvas.before:
                Color:
                    rgba: [0, 0, 0, 0.3]
                Rectangle:
                    pos: self.pos
                    size: self.size
            
            Button:
                text: "< VOLVER"
                size_hint_x: None
                width: '80dp'
                background_color: [0,0,0,0]
                color: color_neon
                on_release: app.root.current = 'menu'
            
            Label:
                text: "LISTA DE SERVIDORES"
                bold: True
                color: color_neon
                font_size: '18sp'

        # Contenedor de la lista (Aquí irían los datos reales)
        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                padding: '15dp'
                spacing: '10dp'
                size_hint_y: None
                height: self.minimum_height
                
                # Ejemplos estéticos de cómo se verían los servidores
                ServerCard:
                    server_name: "KODA | OFICIAL [ARG]"
                    player_count: "24/32"
                ServerCard:
                    server_name: "LATAM TACTICAL | DUST2"
                    player_count: "12/16"
                ServerCard:
                    server_name: "RESERVA KODA [PRIVADO]"
                    player_count: "0/10"
                    
"""

# ==========================================
# CLASES DE PYTHON
# ==========================================
class MenuScreen(Screen):
    pass

class ServerListScreen(Screen):
    pass

class KodaTacticalApp(App):
    def build(self):
        self.title = "Koda Tactical"
        # Cargamo
        return Builder.load_string(KV)

if __name__ == '__main__':
    KodaTacticalApp().run()
