import socket
import struct
from threading import Thread
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import mainthread
from kivy.properties import StringProperty

# Configuración de ventana para PC
Window.clearcolor = (0.02, 0.02, 0.03, 1)
Window.size = (360, 640)

# ==========================================
# LÓGICA DE RED (Protocolo A2S de Valve)
# ==========================================
def get_server_info(ip, port):
    """Consulta básica a un servidor Source usando Sockets puros."""
    QUERY = b'\xFF\xFF\xFF\xFFTSource Engine Query\x00'
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.5)
        sock.sendto(QUERY, (ip, int(port)))
        data, _ = sock.recvfrom(4096)
        sock.close()

        # Parseo simple del paquete A2S_INFO
        content = data[6:]
        name, end = content.split(b'\x00', 1)
        map_name, end = end.split(b'\x00', 1)
        folder, end = end.split(b'\x00', 1)
        game, end = end.split(b'\x00', 1)
        
        # Jugadores y Max Jugadores están en los siguientes bytes
        players = end[2]
        max_players = end[3]
        
        return {
            "name": name.decode('utf-8', 'ignore'),
            "players": f"{players}/{max_players}",
            "map": map_name.decode('utf-8', 'ignore'),
            "ip": f"{ip}:{port}"
        }
    except Exception as e:
        print(f"Error en {ip}:{port} -> {e}")
        return None

# ==========================================
# DISEÑO VISUAL (KV Language)
# ==========================================
KV = """
#:set color_back [0.02, 0.02, 0.03, 1]
#:set color_neon [0.0, 1.0, 0.25, 1]
#:set color_neon_dim [0.0, 1.0, 0.25, 0.2]

<TacticalButton@Button>:
    background_normal: ''
    background_down: ''
    background_color: [0, 0, 0, 0]
    color: color_neon
    bold: True
    size_hint_y: None
    height: '55dp'
    canvas.before:
        Color:
            rgba: color_neon if self.state == 'normal' else [1, 1, 1, 0.2]
        Line:
            width: 1.2
            rectangle: (self.x, self.y, self.width, self.height)

<ServerCard>:
    orientation: 'horizontal'
    size_hint_y: None
    height: '80dp'
    padding: '10dp'
    spacing: '10dp'
    canvas.before:
        Color:
            rgba: [0.05, 0.05, 0.1, 1]
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: color_neon_dim
        Line:
            width: 1
            rectangle: (self.x, self.y, self.width, self.height)

    BoxLayout:
        orientation: 'vertical'
        size_hint_x: 0.7
        Label:
            text: root.server_name
            bold: True
            halign: 'left'
            text_size: self.size
        Label:
            text: root.server_ip
            font_size: '11sp'
            color: [0.5, 0.5, 0.5, 1]
            halign: 'left'
            text_size: self.size

    BoxLayout:
        orientation: 'vertical'
        size_hint_x: 0.3
        Label:
            text: root.player_count
            color: color_neon
            font_size: '18sp'
            bold: True
        Label:
            text: "PLAYERS"
            font_size: '9sp'
            color: [0.4, 0.4, 0.4, 1]

ScreenManager:
    MenuScreen:
    ServerListScreen:

<MenuScreen>:
    name: 'menu'
    BoxLayout:
        orientation: 'vertical'
        padding: ['20dp', '60dp', '20dp', '40dp']
        spacing: '20dp'

        Label:
            text: "KODA\\nTACTICAL"
            font_size: '42sp'
            bold: True
            color: color_neon
            halign: 'center'
        
        Label:
            text: "SYSTEM STATUS: SECURE"
            font_size: '12sp'
            color: [0.4, 0.4, 0.4, 1]

        Widget:

        TacticalButton:
            text: "SCAN SERVERS"
            on_release: app.root.current = 'servers'

<ServerListScreen>:
    name: 'servers'
    BoxLayout:
        orientation: 'vertical'
        
        BoxLayout:
            size_hint_y: None
            height: '60dp'
            padding: '10dp'
            Button:
                text: "< VOLVER"
                background_color: [0,0,0,0]
                color: color_neon
                on_release: app.root.current = 'menu'
            Label:
                text: "LIVE FEED"
                bold: True
                color: color_neon

        ScrollView:
            BoxLayout:
                id: server_container
                orientation: 'vertical'
                padding: '15dp'
                spacing: '12dp'
                size_hint_y: None
                height: self.minimum_height
"""

# ==========================================
# CLASES Y WIDGETS
# ==========================================
class ServerCard(App.get_running_app().root.__class__ if App.get_running_app() else Screen):
    # Esto es un truco para que el KV reconozca las propiedades
    pass

from kivy.uix.boxlayout import BoxLayout
class ServerCard(BoxLayout):
    server_name = StringProperty('')
    server_ip = StringProperty('')
    player_count = StringProperty('')

class MenuScreen(Screen):
    pass

class ServerListScreen(Screen):
    def on_enter(self):
        # Limpiamos la lista y empezamos a escanear
        self.ids.server_container.clear_widgets()
        Thread(target=self.scan_servers_thread, daemon=True).start()

    def scan_servers_thread(self):
        # --- LISTA DE TUS SERVIDORES (IP, PORT) ---
        # Cámbialos por los servidores reales que quieras monitorear
        targets = [
            ("45.235.98.50", 27015), 
            ("45.235.98.50", 27016),
            ("181.119.141.22", 27015)
        ]

        for ip, port in targets:
            data = get_server_info(ip, port)
            if data:
                self.add_card_to_ui(data)

    @mainthread
    def add_card_to_ui(self, data):
        card = ServerCard(
            server_name=data['name'],
            server_ip=data['ip'],
            player_count=data['players']
        )
        self.ids.server_container.add_widget(card)

class KodaTacticalApp(App):
    def build(self):
        return Builder.load_string(KV)

if __name__ == '__main__':
    KodaTacticalApp().run()
