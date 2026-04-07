import socket
import json
import os
from threading import Thread
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.clock import mainthread
from kivy.utils import get_color_from_hex
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivy.properties import StringProperty, ColorProperty

# --- LÓGICA DE PERSISTENCIA ---
STORAGE_FILE = "servers.json"

def load_saved_servers():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as f:
            return json.load(f)
    return ["45.235.98.50:27015", "181.119.141.22:27015"] # Defaults

def save_servers(servers_list):
    with open(STORAGE_FILE, "w") as f:
        json.dump(servers_list, f)

# --- LÓGICA DE RED (Source Engine) ---
def get_server_info(address):
    try:
        ip, port = address.split(":")
        QUERY = b'\xFF\xFF\xFF\xFFTSource Engine Query\x00'
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1.5)
        sock.sendto(QUERY, (ip, int(port)))
        data, _ = sock.recvfrom(4096)
        sock.close()
        content = data[6:]
        parts = content.split(b'\x00')
        return {
            "name": parts[0].decode('utf-8', 'ignore')[:25],
            "map": parts[1].decode('utf-8', 'ignore'),
            "players": f"{parts[4][0]}/{parts[4][1]}",
            "ip": address
        }
    except:
        return None

# --- DISEÑO KV ---
KV = """
<GameCard>:
    orientation: "vertical"
    size_hint: None, None
    size: "140dp", "180dp"
    radius: [20, ]
    padding: "15dp"
    md_bg_color: root.bg_color
    elevation: 3

    MDIcon:
        icon: root.icon_name
        font_size: "50sp"
        halign: "center"
        theme_text_color: "Custom"
        text_color: 1, 1, 1, 1
        pos_hint: {"center_x": .5}
    MDLabel:
        text: root.game_name
        halign: "center"
        bold: True
        theme_text_color: "Custom"
        text_color: 1, 1, 1, 1

<ServerCard>:
    orientation: "horizontal"
    size_hint_y: None
    height: "100dp"
    padding: "15dp"
    radius: [20, ]
    md_bg_color: app.card_color
    elevation: 2

    MDBoxLayout:
        orientation: "vertical"
        MDLabel:
            text: root.server_name
            bold: True
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
        MDLabel:
            text: f"MAPA: {root.server_map}"
            font_style: "Caption"
            theme_text_color: "Custom"
            text_color: app.text_dim
        MDLabel:
            text: root.server_ip
            font_style: "Caption"
            theme_text_color: "Custom"
            text_color: app.neon_orange

    MDBoxLayout:
        orientation: "vertical"
        adaptive_width: True
        spacing: "5dp"
        MDLabel:
            text: root.player_count
            halign: "right"
            bold: True
            theme_text_color: "Custom"
            text_color: app.neon_orange
        MDIconButton:
            icon: "delete"
            theme_text_color: "Custom"
            text_color: 1, 0, 0, 1
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
            text: "BIENVENIDO\\nA KOUDA"
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
    MDFloatLayout:
        MDBoxLayout:
            orientation: 'vertical'
            MDTopAppBar:
                title: "Server Hub"
                elevation: 0
                md_bg_color: app.bg_dark
                left_action_items: [["arrow-left", lambda x: app.go_back()]]
            MDScrollView:
                MDBoxLayout:
                    orientation: 'vertical'
                    adaptive_height: True
                    padding: "20dp"
                    spacing: "20dp"
                    
                    # Carrusel de juegos (se mantiene igual)
                    MDScrollView:
                        size_hint_y: None
                        height: "200dp"
                        MDBoxLayout:
                            orientation: "horizontal"
                            adaptive_width: True
                            spacing: "15dp"
                            GameCard:
                                game_name: "CS 1.6"
                                icon_name: "target-variant"
                                bg_color: 0.2, 0.25, 0.15, 1
                            GameCard:
                                game_name: "CS:GO"
                                icon_name: "pistol"
                                bg_color: 0.1, 0.15, 0.25, 1

                    MDBoxLayout:
                        id: container
                        orientation: 'vertical'
                        adaptive_height: True
                        spacing: "12dp"

        MDFloatingActionButton:
            icon: "plus"
            md_bg_color: app.neon_orange
            pos_hint: {"center_x": .85, "center_y": .1}
            on_release: app.show_add_dialog()
"""

class GameCard(MDCard):
    game_name = StringProperty()
    icon_name = StringProperty()
    bg_color = ColorProperty()

class ServerCard(MDCard):
    server_name = StringProperty()
    server_map = StringProperty()
    player_count = StringProperty()
    server_ip = StringProperty()

class KoudaApp(MDApp):
    dialog = None

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.bg_dark = get_color_from_hex("#121212")
        self.card_color = get_color_from_hex("#1E1E1E")
        self.neon_orange = get_color_from_hex("#FF6B00")
        self.text_dim = get_color_from_hex("#8E8E93")
        return Builder.load_string(KV)

    def on_start(self):
        self.refresh_list()

    def refresh_list(self):
        container = self.root.get_screen('servers').ids.container
        container.clear_widgets()
        servers = load_saved_servers()
        for addr in servers:
            Thread(target=self.fetch_and_add, args=(addr,), daemon=True).start()

    def fetch_and_add(self, addr):
        info = get_server_info(addr)
        if info:
            self.add_ui(info)

    @mainthread
    def add_ui(self, info):
        container = self.root.get_screen('servers').ids.container
        card = ServerCard(
            server_name=info['name'],
            server_map=info['map'],
            player_count=info['players'],
            server_ip=info['ip']
        )
        container.add_widget(card)

    def show_add_dialog(self):
        if not self.dialog:
            self.content = MDTextField(hint_text="Ej: 127.0.0.1:27015")
            self.dialog = MDDialog(
                title="Añadir Servidor",
                type="custom",
                content_cls=self.content,
                buttons=[
                    MDFlatButton(text="CANCELAR", on_release=lambda x: self.dialog.dismiss()),
                    MDRaisedButton(text="AÑADIR", on_release=self.add_server_from_dialog),
                ],
            )
        self.dialog.open()

    def add_server_from_dialog(self, *args):
        new_ip = self.content.text
        if ":" in new_ip:
            servers = load_saved_servers()
            if new_ip not in servers:
                servers.append(new_ip)
                save_servers(servers)
                self.refresh_list()
            self.dialog.dismiss()
            self.content.text = ""

    def remove_server(self, ip):
        servers = load_saved_servers()
        if ip in servers:
            servers.remove(ip)
            save_servers(servers)
            self.refresh_list()

    def go_back(self):
        self.root.current = 'menu'

if __name__ == '__main__':
    KoudaApp().run()
