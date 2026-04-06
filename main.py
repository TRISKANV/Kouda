import socket
from threading import Thread
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import mainthread
from kivy.utils import get_color_from_hex
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty

# --- LÓGICA DE RED (Tu código original optimizado) ---
def get_server_info(ip, port):
    QUERY = b'\xFF\xFF\xFF\xFFTSource Engine Query\x00'
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1.5)
        sock.sendto(QUERY, (ip, int(port)))
        data, _ = sock.recvfrom(4096)
        sock.close()
        content = data[6:]
        parts = content.split(b'\x00')
        return {
            "name": parts[0].decode('utf-8', 'ignore')[:25],
            "map": parts[1].decode('utf-8', 'ignore') if len(parts) > 1 else "unknown",
            "players": f"{parts[4][0]}/{parts[4][1]}" if len(parts) > 4 else "??",
            "ip": f"{ip}:{port}"
        }
    except:
        return None

# --- INTERFAZ KV (Estética de la imagen aplicada a KivyMD) ---
KV = """
<ServerCard>:
    orientation: "horizontal"
    size_hint_y: None
    height: "80dp"
    padding: "15dp"
    radius: [15, ]
    md_bg_color: app.card_color
    elevation: 2
    ripple_behavior: True

    MDBoxLayout:
        orientation: "vertical"
        adaptive_height: True
        pos_hint: {"center_y": .5}
        
        MDLabel:
            text: root.server_name
            font_style: "Subtitle1"
            bold: True
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
        MDLabel:
            text: root.server_map
            font_style: "Caption"
            theme_text_color: "Custom"
            text_color: app.text_dim

    MDBoxLayout:
        orientation: "vertical"
        adaptive_width: True
        pos_hint: {"center_y": .5}
        
        MDLabel:
            text: root.player_count
            halign: "right"
            bold: True
            theme_text_color: "Custom"
            text_color: app.neon_orange
        MDLabel:
            text: "35ms" # Ping simulado como en la imagen
            font_style: "Caption"
            halign: "right"
            theme_text_color: "Custom"
            text_color: app.text_dim

MDScreenManager:
    MenuScreen:
    ServerListScreen:

<MenuScreen>:
    name: 'menu'
    md_bg_color: app.bg_dark
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: '40dp'
        spacing: '30dp'
        
        MDLabel:
            text: "KOUDA\\nTACTICAL"
            font_style: "H3"
            halign: "center"
            bold: True
            theme_text_color: "Custom"
            text_color: app.neon_orange

        MDRaisedButton:
            text: "SCAN SERVERS"
            size_hint_x: 1
            height: "60dp"
            md_bg_color: app.neon_orange
            text_color: 0, 0, 0, 1
            on_release: root.manager.current = 'servers'

<ServerListScreen>:
    name: 'servers'
    md_bg_color: app.bg_dark
    
    MDBoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: "Server Hub"
            elevation: 0
            md_bg_color: app.bg_dark
            left_action_items: [["arrow-left", lambda x: app.go_back()]]

        MDScrollView:
            MDBoxLayout:
                id: container
                orientation: 'vertical'
                adaptive_height: True
                padding: "20dp"
                spacing: "10dp"
"""

class ServerCard(MDCard):
    server_name = StringProperty()
    server_map = StringProperty()
    player_count = StringProperty()

class MenuScreen(Screen): pass

class ServerListScreen(Screen):
    def on_enter(self):
        self.ids.container.clear_widgets()
        Thread(target=self.run_scan, daemon=True).start()

    def run_scan(self):
        # IPs de tu código original
        test_ips = [("45.235.98.50", 27015), ("181.119.141.22", 27015)]
        for ip, port in test_ips:
            info = get_server_info(ip, port)
            if info:
                self.add_ui(info)

    @mainthread
    def add_ui(self, info):
        card = ServerCard(
            server_name=info['name'],
            server_map=info['map'],
            player_count=info['players']
        )
        self.ids.container.add_widget(card)

class KoudaApp(MDApp):
    def build(self):
        # Colores exactos de la estética pedida
        self.theme_cls.theme_style = "Dark"
        self.bg_dark = get_color_from_hex("#121212")
        self.card_color = get_color_from_hex("#1E1E1E")
        self.neon_orange = get_color_from_hex("#FF6B00")
        self.text_dim = get_color_from_hex("#8E8E93")
        
        return Builder.load_string(KV)

    def go_back(self):
        self.root.current = 'menu'

if __name__ == '__main__':
    KoudaApp().run()
