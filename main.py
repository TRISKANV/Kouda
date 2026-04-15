import socket
import json
import os
from threading import Thread
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.clock import mainthread, Clock
from kivy.utils import get_color_from_hex
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivy.properties import StringProperty, ColorProperty

# --- LÓGICA DE RED (UDP SOURCE QUERY) ---
def get_server_info(address):
    try:
        if ":" not in address: return None
        ip, port = address.split(":")
        QUERY = b'\xFF\xFF\xFF\xFFTSource Engine Query\x00'
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
        sock.sendto(QUERY, (ip, int(port)))
        data, _ = sock.recvfrom(4096)
        sock.close()
        parts = data[6:].split(b'\x00')
        return {
            "name": parts[0].decode('utf-8', 'ignore')[:25],
            "map": parts[1].decode('utf-8', 'ignore'),
            "players": f"{parts[4][0]}/{parts[4][1]}",
            "ip": address
        }
    except:
        return None

# --- DISEÑO INTEGRADO (TU ESTÉTICA TACTICAL) ---
KV = """
<GameCard>:
    orientation: "vertical"
    size_hint: None, None
    size: "140dp", "180dp"
    radius: [20, ]
    md_bg_color: root.bg_color
    elevation: 4
    FitImage:
        source: root.image_path
        radius: [20, 20, 0, 0]
        size_hint_y: 0.75
        allow_stretch: True
    MDLabel:
        text: root.game_name
        halign: "center"
        bold: True
        theme_text_color: "Custom"
        text_color: 1, 1, 1, 1
        size_hint_y: 0.25

<ServerCard>:
    orientation: "horizontal"
    size_hint_y: None
    height: "90dp"
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
            font_style: "H6"
            bold: True
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
        MDLabel:
            text: f"{root.server_map} • {root.server_ip}"
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
            text: "35ms"
            font_style: "Caption"
            halign: "right"
            theme_text_color: "Custom"
            text_color: app.text_dim
        MDIconButton:
            icon: "trash-can-outline"
            icon_size: "18dp"
            theme_icon_color: "Custom"
            icon_color: app.text_dim
            on_release: app.remove_server(root.server_ip)

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
        
        # Carrusel de juegos (Agregado para que no falle el código Python)
        MDBoxLayout:
            size_hint_y: None
            height: "220dp"
            padding: ["20dp", 0]
            MDScrollView:
                bar_width: 0
                MDBoxLayout:
                    id: game_carousel
                    orientation: "horizontal"
                    adaptive_width: True
                    spacing: "15dp"

        MDScrollView:
            MDBoxLayout:
                id: container
                orientation: 'vertical'
                adaptive_height: True
                padding: "20dp"
                spacing: "12dp"
    
    MDFloatingActionButton:
        icon: "plus"
        md_bg_color: app.neon_orange
        pos_hint: {"center_x": .88, "center_y": .08}
        on_release: app.show_add_dialog()
"""

class GameCard(MDCard):
    game_name = StringProperty()
    image_path = StringProperty()
    bg_color = ColorProperty()

class ServerCard(MDCard):
    server_name = StringProperty()
    server_map = StringProperty()
    player_count = StringProperty()
    server_ip = StringProperty()

class MenuScreen(Screen): pass
class ServerListScreen(Screen): pass

class KoudaApp(MDApp):
    dialog = None
    
    def build(self):
        self.storage_file = os.path.join(self.user_data_dir, "servers.json")
        self.assets_path = os.path.join(self.directory, "assets")
        self.theme_cls.theme_style = "Dark"
        
        # Colores Tactical
        self.bg_dark = get_color_from_hex("#0F0F0F")
        self.card_color = get_color_from_hex("#1A1A1A")
        self.neon_orange = get_color_from_hex("#FF6B00")
        self.text_dim = get_color_from_hex("#707070")
        
        return Builder.load_string(KV)

    def on_start(self):
        # El delay de 0.5s previene el freeze en el logo
        Clock.schedule_once(self.run_initial_logic, 0.5)

    def run_initial_logic(self, dt):
        self.setup_game_cards()
        self.refresh_list()

    def setup_game_cards(self):
        try:
            carousel = self.root.get_screen('servers').ids.game_carousel
            games = [
                ("CS 1.6", "cs16.png", "#2D3E2F"),
                ("CS:GO", "csgo.png", "#1B2838"),
                ("HALF-LIFE", "hl.png", "#4B2D1F"),
                ("TF2", "tf2.png", "#392A23")
            ]
            for name, img, color in games:
                path = os.path.join(self.assets_path, img)
                if not os.path.exists(path): path = ""
                carousel.add_widget(GameCard(game_name=name, image_path=path, bg_color=get_color_from_hex(color)))
        except:
            pass

    def refresh_list(self):
        container = self.root.get_screen('servers').ids.container
        container.clear_widgets()
        for addr in self.load_servers():
            Thread(target=self.fetch_and_add, args=(addr,), daemon=True).start()

    def fetch_and_add(self, addr):
        info = get_server_info(addr)
        if info:
            self.add_ui(info)

    @mainthread
    def add_ui(self, info):
        self.root.get_screen('servers').ids.container.add_widget(
            ServerCard(
                server_name=info['name'], 
                server_map=info['map'], 
                player_count=info['players'], 
                server_ip=info['ip']
            )
        )

    def load_servers(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return ["45.235.98.50:27015"]

    def save_servers(self, data):
        try:
            with open(self.storage_file, "w") as f:
                json.dump(data, f)
        except:
            pass

    def show_add_dialog(self):
        self.field = MDTextField(hint_text="IP:Puerto", mode="round")
        self.dialog = MDDialog(
            title="Nuevo Servidor",
            type="custom",
            content_cls=self.field,
            buttons=[
                MDFlatButton(text="CANCELAR", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="AGREGAR", md_bg_color=self.neon_orange, on_release=self.add_server_from_dialog),
            ],
        )
        self.dialog.open()

    def add_server_from_dialog(self, *args):
        val = self.field.text.strip()
        if ":" in val:
            s = self.load_servers()
            if val not in s:
                s.append(val)
                self.save_servers(s)
                self.refresh_list()
            self.dialog.dismiss()

    def remove_server(self, ip):
        s = self.load_servers()
        if ip in s:
            s.remove(ip)
            self.save_servers(s)
            self.refresh_list()

    def go_back(self):
        self.root.current = 'menu'

if __name__ == '__main__':
    KoudaApp().run()
