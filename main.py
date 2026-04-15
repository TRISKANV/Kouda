import socket
import json
import os
import time
import struct
from threading import Thread
from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.clock import mainthread, Clock
from kivy.utils import get_color_from_hex
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import OneLineListItem, MDList
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, ColorProperty, BooleanProperty

# --- LÓGICA DE RED AVANZADA ---
def get_server_data(address, get_players=False):
    try:
        ip, port = address.split(":")
        addr = (ip, int(port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1.5)

        # 1. Info Básica y Ping Real
        QUERY_INFO = b'\xFF\xFF\xFF\xFFTSource Engine Query\x00'
        start_time = time.perf_counter()
        sock.sendto(QUERY_INFO, addr)
        data, _ = sock.recvfrom(4096)
        ping = int((time.perf_counter() - start_time) * 1000)
        
        parts = data[6:].split(b'\x00')
        info = {
            "name": parts[0].decode('utf-8', 'ignore')[:25],
            "map": parts[1].decode('utf-8', 'ignore'),
            "players": f"{parts[4][0]}/{parts[4][1]}",
            "ping": f"{ping}ms",
            "ip": address
        }

        # 2. Lista de Jugadores (A2S_PLAYER)
        player_list = []
        if get_players:
            sock.sendto(b'\xFF\xFF\xFF\xFF\x55\xFF\xFF\xFF\xFF', addr)
            resp, _ = sock.recvfrom(4096)
            challenge = resp[5:]
            sock.sendto(b'\xFF\xFF\xFF\xFF\x55' + challenge, addr)
            resp, _ = sock.recvfrom(4096)
            
            ptr = 6
            num_p = resp[5]
            for _ in range(num_p):
                ptr += 1
                name_end = resp.find(b'\x00', ptr)
                p_name = resp[ptr:name_end].decode('utf-8', 'ignore')
                score = struct.unpack('<l', resp[name_end+1:name_end+5])[0]
                if p_name: player_list.append(f"{p_name}  —  {score} pts")
                ptr = name_end + 10
        
        sock.close()
        return info, player_list
    except:
        return None, []

# --- DISEÑO TACTICAL V5 (KV) ---
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
    height: "100dp"
    padding: "15dp"
    radius: [15, ]
    md_bg_color: app.card_color
    elevation: 2
    on_release: app.show_player_list(root.server_ip)
    
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
        spacing: "2dp"
        MDLabel:
            text: root.player_count
            halign: "right"
            bold: True
            theme_text_color: "Custom"
            text_color: app.neon_orange
        MDLabel:
            text: root.ping_val
            font_style: "Caption"
            halign: "right"
            theme_text_color: "Custom"
            text_color: 0, 1, 0, 1
        MDIconButton:
            icon: "star" if root.is_fav else "star-outline"
            icon_size: "18dp"
            theme_icon_color: "Custom"
            icon_color: (1, 0.8, 0, 1) if root.is_fav else app.text_dim
            on_release: app.toggle_favorite(root.server_ip)

MDScreenManager:
    MenuScreen:
    ServerListScreen:

<MenuScreen>:
    name: 'menu'
    md_bg_color: app.bg_dark
    MDBoxLayout:
        orientation: 'vertical'
        padding: '40dp'
        MDLabel:
            text: "KOUDA\\nTACTICAL"
            font_style: "H3"
            halign: "center"
            bold: True
            theme_text_color: "Custom"
            text_color: app.neon_orange
        MDRaisedButton:
            text: "SCAN HUB"
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
            title: "Live Operations"
            md_bg_color: app.bg_dark
            elevation: 0
            left_action_items: [["arrow-left", lambda x: app.go_back()]]
            right_action_items: [["refresh", lambda x: app.refresh_list()]]
        
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
    ping_val = StringProperty()
    is_fav = BooleanProperty(False)

class MenuScreen(Screen): pass
class ServerListScreen(Screen): pass

class KoudaApp(MDApp):
    def build(self):
        Window.clearcolor = get_color_from_hex("#0F0F0F")
        self.storage_file = os.path.join(self.user_data_dir, "servers.json")
        self.favs_file = os.path.join(self.user_data_dir, "favs.json")
        self.assets_path = os.path.join(self.directory, "assets")
        self.theme_cls.theme_style = "Dark"
        
        self.bg_dark = get_color_from_hex("#0F0F0F")
        self.card_color = get_color_from_hex("#1A1A1A")
        self.neon_orange = get_color_from_hex("#FF6B00")
        self.text_dim = get_color_from_hex("#707070")
        
        return Builder.load_string(KV)

    def on_start(self):
        Clock.schedule_once(lambda dt: self.refresh_list(), 0.1)

    def refresh_list(self):
        container = self.root.get_screen('servers').ids.container
        container.clear_widgets()
        self.setup_game_cards()
        
        servers = self.load_data(self.storage_file, ["45.235.98.50:27015"])
        favs = self.load_data(self.favs_file, [])
        
        # Primero cargar favoritos
        for addr in favs:
            Thread(target=self.fetch_and_add, args=(addr, True), daemon=True).start()
        # Luego el resto
        for addr in servers:
            if addr not in favs:
                Thread(target=self.fetch_and_add, args=(addr, False), daemon=True).start()

    def fetch_and_add(self, addr, is_fav):
        info, _ = get_server_data(addr)
        if info:
            self.add_ui(info, is_fav)

    @mainthread
    def add_ui(self, info, is_fav):
        self.root.get_screen('servers').ids.container.add_widget(
            ServerCard(server_name=info['name'], server_map=info['map'], 
                       player_count=info['players'], server_ip=info['ip'], 
                       ping_val=info['ping'], is_fav=is_fav)
        )

    def show_player_list(self, ip):
        self.dialog = MDDialog(title="Consultando escuadra...", type="custom", content_cls=MDList())
        self.dialog.open()
        Thread(target=self.bg_load_players, args=(ip,), daemon=True).start()

    def bg_load_players(self, ip):
        _, players = get_server_data(ip, True)
        self.show_final_player_dialog(players)

    @mainthread
    def show_final_player_dialog(self, players):
        self.dialog.dismiss()
        content = ScrollView(size_hint_y=None, height="300dp")
        list_v = MDList()
        if not players:
            list_v.add_widget(OneLineListItem(text="Servidor vacío o sin respuesta"))
        else:
            for p in players: list_v.add_widget(OneLineListItem(text=p))
        content.add_widget(list_v)
        self.dialog = MDDialog(title="Operativos Online", type="custom", content_cls=content,
                               buttons=[MDFlatButton(text="CERRAR", on_release=lambda x: self.dialog.dismiss())])
        self.dialog.open()

    def toggle_favorite(self, ip):
        favs = self.load_data(self.favs_file, [])
        if ip in favs: favs.remove(ip)
        else: favs.append(ip)
        self.save_data(self.favs_file, favs)
        self.refresh_list()

    def load_data(self, path, default):
        if os.path.exists(path):
            with open(path, "r") as f: return json.load(f)
        return default

    def save_data(self, path, data):
        with open(path, "w") as f: json.dump(data, f)

    def setup_game_cards(self):
        try:
            carousel = self.root.get_screen('servers').ids.game_carousel
            carousel.clear_widgets()
            games = [("CS 1.6", "cs16.png", "#2D3E2F"), ("CS:GO", "csgo.png", "#1B2838"), 
                     ("HALF-LIFE", "hl.png", "#4B2D1F"), ("TF2", "tf2.png", "#392A23")]
            for name, img, color in games:
                path = os.path.join(self.assets_path, img)
                carousel.add_widget(GameCard(game_name=name, image_path=path if os.path.exists(path) else "", 
                                             bg_color=get_color_from_hex(color)))
        except: pass

    def show_add_dialog(self):
        self.field = MDTextField(hint_text="IP:Puerto", mode="round")
        self.dialog = MDDialog(title="Nuevo Objetivo", type="custom", content_cls=self.field,
            buttons=[MDFlatButton(text="CANCEL", on_release=lambda x: self.dialog.dismiss()),
                     MDRaisedButton(text="AÑADIR", md_bg_color=self.neon_orange, on_release=self.add_server_from_dialog)])
        self.dialog.open()

    def add_server_from_dialog(self, *args):
        val = self.field.text.strip()
        if ":" in val:
            s = self.load_data(self.storage_file, [])
            if val not in s:
                s.append(val); self.save_data(self.storage_file, s); self.refresh_list()
            self.dialog.dismiss()

    def go_back(self): self.root.current = 'menu'

if __name__ == '__main__':
    KoudaApp().run()
