import socket
import json
import os
import time
import struct
import requests
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

# --- LÓGICA DE RED Y GEO-IP ---
def get_server_data(address, get_players=False):
    try:
        ip, port = address.split(":")
        addr = (ip, int(port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1.2)

        # 1. Info Básica y Ping
        QUERY_INFO = b'\xFF\xFF\xFF\xFFTSource Engine Query\x00'
        start_time = time.perf_counter()
        sock.sendto(QUERY_INFO, addr)
        data, _ = sock.recvfrom(4096)
        ping = int((time.perf_counter() - start_time) * 1000)
        
        parts = data[6:].split(b'\x00')
        cur_p = parts[4][0]
        max_p = parts[4][1]
        
        info = {
            "name": parts[0].decode('utf-8', 'ignore')[:25],
            "map": parts[1].decode('utf-8', 'ignore'),
            "players": f"{cur_p}/{max_p}",
            "cur_players": cur_p,
            "max_players": max_p,
            "ping": f"{ping}ms",
            "ip": address
        }

        # 2. Geo-IP (Cacheamos para no saturar la API)
        try:
            geo_req = requests.get(f"http://ip-api.com/json/{ip}?fields=countryCode", timeout=0.5).json()
            info["country"] = geo_req.get("countryCode", "??")
        except:
            info["country"] = "UN"

        player_list = []
        if get_players:
            # Protocolo A2S_PLAYER (Simplificado para brevedad)
            sock.sendto(b'\xFF\xFF\xFF\xFF\x55\xFF\xFF\xFF\xFF', addr)
            resp, _ = sock.recvfrom(4096)
            sock.sendto(b'\xFF\xFF\xFF\xFF\x55' + resp[5:], addr)
            resp, _ = sock.recvfrom(4096)
            ptr = 6
            for _ in range(resp[5]):
                ptr += 1
                end = resp.find(b'\x00', ptr)
                name = resp[ptr:end].decode('utf-8', 'ignore')
                if name: player_list.append(name)
                ptr = end + 10
        
        sock.close()
        return info, player_list
    except:
        return None, []

# --- UI TACTICAL V6 ---
KV = """
<ServerCard>:
    orientation: "horizontal"
    size_hint_y: None
    height: "100dp"
    padding: "12dp"
    radius: [15, ]
    md_bg_color: app.card_color
    on_release: app.show_server_options(root.server_ip, root.player_count)
    
    MDBoxLayout:
        orientation: "vertical"
        MDBoxLayout:
            adaptive_height: True
            spacing: "8dp"
            MDLabel:
                text: f"[{root.country}]"
                font_style: "Caption"
                theme_text_color: "Custom"
                text_color: app.neon_orange
                size_hint_x: None
                width: "30dp"
            MDLabel:
                text: root.server_name
                font_style: "Subtitle1"
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
            text_color: app.neon_orange if "32/32" not in root.player_count else [1,0,0,1]
        MDLabel:
            text: root.ping_val
            font_style: "Caption"
            halign: "right"
            theme_text_color: "Custom"
            text_color: 0, 1, 0, 1
        MDIconButton:
            icon: "star" if root.is_fav else "star-outline"
            icon_size: "18dp"
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
            text: "LAUNCH HUB"
            size_hint_x: 1
            height: "60dp"
            md_bg_color: app.neon_orange
            on_release: root.manager.current = 'servers'

<ServerListScreen>:
    name: 'servers'
    md_bg_color: app.bg_dark
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Global Operations"
            md_bg_color: app.bg_dark
            left_action_items: [["arrow-left", lambda x: app.go_back()]]
            right_action_items: [["refresh", lambda x: app.refresh_list()]]
        
        MDScrollView:
            MDBoxLayout:
                id: container
                orientation: 'vertical'
                adaptive_height: True
                padding: "20dp"
                spacing: "12dp"
"""

class ServerCard(MDCard):
    server_name = StringProperty()
    server_map = StringProperty()
    player_count = StringProperty()
    server_ip = StringProperty()
    ping_val = StringProperty()
    country = StringProperty("??")
    is_fav = BooleanProperty(False)

class MenuScreen(Screen): pass
class ServerListScreen(Screen): pass

class KoudaApp(MDApp):
    watching_ip = None # IP que estamos vigilando para alerta

    def build(self):
        Window.clearcolor = get_color_from_hex("#0F0F0F")
        self.storage_file = os.path.join(self.user_data_dir, "servers.json")
        self.favs_file = os.path.join(self.user_data_dir, "favs.json")
        self.theme_cls.theme_style = "Dark"
        self.bg_dark = get_color_from_hex("#0F0F0F")
        self.card_color = get_color_from_hex("#1A1A1A")
        self.neon_orange = get_color_from_hex("#FF6B00")
        self.text_dim = get_color_from_hex("#707070")
        return Builder.load_string(KV)

    def on_start(self):
        Clock.schedule_once(lambda dt: self.refresh_list(), 0.1)
        # Hilo de vigilancia de slots (Background Monitor)
        Clock.schedule_interval(self.check_watchlist, 15)

    def refresh_list(self):
        container = self.root.get_screen('servers').ids.container
        container.clear_widgets()
        servers = self.load_data(self.storage_file, ["45.235.98.50:27015"])
        favs = self.load_data(self.favs_file, [])
        for addr in (favs + [s for s in servers if s not in favs]):
            Thread(target=self.fetch_and_add, args=(addr, addr in favs), daemon=True).start()

    def fetch_and_add(self, addr, is_fav):
        info, _ = get_server_data(addr)
        if info: self.add_ui(info, is_fav)

    @mainthread
    def add_ui(self, info, is_fav):
        self.root.get_screen('servers').ids.container.add_widget(
            ServerCard(server_name=info['name'], server_map=info['map'], 
                       player_count=info['players'], server_ip=info['ip'], 
                       ping_val=info['ping'], country=info['country'], is_fav=is_fav)
        )

    def show_server_options(self, ip, p_count):
        # Si el server está lleno, ofrecemos activar alerta
        buttons = [MDFlatButton(text="VER JUGADORES", on_release=lambda x: self.open_players(ip))]
        cur, maxi = p_count.split("/")
        if cur == maxi:
            buttons.append(MDRaisedButton(text="ALERTAR ESPACIO", md_bg_color=[1,0,0,1], 
                                          on_release=lambda x: self.set_watch(ip)))
        
        self.dialog = MDDialog(title="Opciones de Misión", buttons=buttons)
        self.dialog.open()

    def set_watch(self, ip):
        self.watching_ip = ip
        self.dialog.dismiss()
        # Aquí podrías usar una notificación nativa si usas plyer
        print(f"Vigilando {ip}...") 

    def check_watchlist(self, dt):
        if self.watching_ip:
            info, _ = get_server_data(self.watching_ip)
            if info and info['cur_players'] < info['max_players']:
                self.trigger_alert(info['name'])
                self.watching_ip = None

    @mainthread
    def trigger_alert(self, name):
        MDDialog(title="¡SLOT LIBRE!", text=f"Hay espacio en {name}. ¡Entra ahora!").open()

    def open_players(self, ip):
        self.dialog.dismiss()
        self.dialog = MDDialog(title="Escaneando...", type="custom", content_cls=MDList())
        self.dialog.open()
        Thread(target=self.bg_load_players, args=(ip,), daemon=True).start()

    def bg_load_players(self, ip):
        _, players = get_server_data(ip, True)
        self.show_final_players(players)

    @mainthread
    def show_final_players(self, players):
        self.dialog.dismiss()
        list_v = MDList()
        for p in players: list_v.add_widget(OneLineListItem(text=p))
        self.dialog = MDDialog(title="Operativos", type="custom", 
                               content_cls=ScrollView(size_hint_y=None, height="250dp", content=list_v))
        self.dialog.open()

    def load_data(self, path, default):
        if os.path.exists(path):
            with open(path, "r") as f: return json.load(f)
        return default

    def save_data(self, path, data):
        with open(path, "w") as f: json.dump(data, f)

    def toggle_favorite(self, ip):
        favs = self.load_data(self.favs_file, [])
        if ip in favs: favs.remove(ip)
        else: favs.append(ip)
        self.save_data(self.favs_file, favs)
        self.refresh_list()

    def go_back(self): self.root.current = 'menu'

if __name__ == '__main__':
    KoudaApp().run()
