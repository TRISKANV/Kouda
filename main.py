import socket
import json
import os
import time
import struct
import requests
from threading import Thread

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.clock import mainthread, Clock
from kivy.utils import get_color_from_hex
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, ColorProperty, BooleanProperty

from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import OneLineIconListItem, IconLeftWidget, MDList
from kivymd.uix.snackbar import Snackbar

# --- LÓGICA DE RED DUAL (GOLDSRC + SOURCE) ---
def get_server_data(address, get_players=False):
    try:
        ip, port = address.split(":")
        addr = (ip, int(port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1.5)

        QUERY_INFO = b'\xFF\xFF\xFF\xFFTSource Engine Query\x00'
        start_time = time.perf_counter()
        sock.sendto(QUERY_INFO, addr)
        data, _ = sock.recvfrom(4096)
        ping = int((time.perf_counter() - start_time) * 1000)
        
        info = {
            "name": "Servidor Desconocido", "map": "-", "players": "?/?",
            "cur_players": 0, "max_players": 0, "ping": f"{ping}ms", "ip": address, "country": "??"
        }

        try:
            header = data[4]
            if header == 0x6D:  # 'm' -> Servidor GoldSrc (CS 1.6, HL)
                parts = data[5:].split(b'\x00')
                if len(parts) >= 3:
                    info["name"] = parts[1].decode('utf-8', 'ignore')[:25]
                    info["map"] = parts[2].decode('utf-8', 'ignore')
                    idx = 5 + len(parts[0]) + 1 + len(parts[1]) + 1 + len(parts[2]) + 1 + len(parts[3]) + 1 + len(parts[4]) + 1
                    if idx + 1 < len(data):
                        info["cur_players"] = data[idx]
                        info["max_players"] = data[idx+1]
                        info["players"] = f"{data[idx]}/{data[idx+1]}"
            
            elif header == 0x49:  # 'I' -> Servidor Source (CS:GO, TF2)
                parts = data[6:].split(b'\x00')
                if len(parts) >= 2:
                    info["name"] = parts[0].decode('utf-8', 'ignore')[:25]
                    info["map"] = parts[1].decode('utf-8', 'ignore')
                    idx = 6 + len(parts[0]) + 1 + len(parts[1]) + 1 + len(parts[2]) + 1 + len(parts[3]) + 1 + 2
                    if idx + 1 < len(data):
                        info["cur_players"] = data[idx]
                        info["max_players"] = data[idx+1]
                        info["players"] = f"{data[idx]}/{data[idx+1]}"
        except Exception:
            pass 

        try:
            geo_res = requests.get(f"http://ip-api.com/json/{ip}?fields=countryCode", timeout=1.0).json()
            info["country"] = geo_res.get("countryCode", "??")
        except:
            pass

        player_list = []
        if get_players:
            try:
                sock.sendto(b'\xFF\xFF\xFF\xFF\x55\xFF\xFF\xFF\xFF', addr)
                resp, _ = sock.recvfrom(4096)
                if resp.startswith(b'\xFF\xFF\xFF\xFF\x41'): 
                    sock.sendto(b'\xFF\xFF\xFF\xFF\x55' + resp[5:9], addr)
                    resp, _ = sock.recvfrom(4096)
                
                if resp.startswith(b'\xFF\xFF\xFF\xFF\x44'):
                    ptr = 5
                    num_players = resp[ptr]
                    ptr += 1
                    for _ in range(num_players):
                        if ptr >= len(resp): break
                        ptr += 1 
                        end = resp.find(b'\x00', ptr)
                        if end == -1 or end + 8 > len(resp): break
                        
                        p_name = resp[ptr:end].decode('utf-8', 'ignore')
                        score = struct.unpack('<l', resp[end+1:end+5])[0]
                        if p_name: player_list.append((p_name, score))
                        ptr = end + 9
            except Exception:
                pass 
        
        sock.close()
        return info, player_list
    except Exception:
        return None, []

# --- UI KOUDA TACTICAL ---
KV = """
<GameCard>:
    orientation: "vertical"
    size_hint: None, None
    size: "130dp", "170dp"
    radius: [15, ]
    md_bg_color: root.bg_color
    elevation: 2
    
    FitImage:
        source: root.image_path
        size_hint_y: 0.75
        radius: [15, 15, 0, 0]
        
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
                width: "35dp"
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
            text_color: app.neon_orange if "32/32" not in root.player_count else [1, 0, 0, 1]
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
            text: "LAUNCH HUB"
            size_hint_x: 1
            height: "60dp"
            md_bg_color: app.neon_orange
            text_color: 0, 0, 0, 1
            on_release: root.manager.current = 'servers'

<ServerListScreen>:
    name: 'servers'
    md_bg_color: app.bg_dark
    on_enter: app.setup_game_cards()
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: "Global Operations"
            md_bg_color: app.bg_dark
            elevation: 0
            left_action_items: [["arrow-left", lambda x: app.go_back()]]
            right_action_items: [["refresh", lambda x: app.refresh_list()]]
        
        MDBoxLayout:
            size_hint_y: None
            height: "200dp"
            padding: ["20dp", "10dp"]
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
    country = StringProperty("??")
    is_fav = BooleanProperty(False)

class MenuScreen(Screen): pass
class ServerListScreen(Screen): pass

class KoudaApp(MDApp):
    watching_ip = None
    dialog = None

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
        Clock.schedule_once(lambda dt: self.refresh_list(), 0.5)
        Clock.schedule_interval(self.check_watchlist, 20)

    def refresh_list(self):
        container = self.root.get_screen('servers').ids.container
        container.clear_widgets()
        
        servers = self.load_data(self.storage_file, ["45.235.98.50:27015"])
        favs = self.load_data(self.favs_file, [])
        
        combined = (favs + [s for s in servers if s not in favs])
        for addr in combined:
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

    def setup_game_cards(self):
        carousel = self.root.get_screen('servers').ids.game_carousel
        if len(carousel.children) > 0: return 
        games = [("CS 1.6", "cs16.png", "#2D3E2F"), ("CS:GO", "csgo.png", "#1B2838"), 
                 ("HL", "hl.png", "#4B2D1F"), ("TF2", "tf2.png", "#392A23")]
        for name, img, color in games:
            path = os.path.join(self.assets_path, img)
            carousel.add_widget(GameCard(game_name=name, image_path=path if os.path.exists(path) else "", 
                                         bg_color=get_color_from_hex(color)))

    def show_server_options(self, ip, p_count):
        cur, maxi = map(int, p_count.split('/') if '/' in p_count else (0,0))
        btns = [MDFlatButton(text="ESCANEAR JUGADORES", on_release=lambda x: self.prepare_scan(ip))]
        
        if cur >= maxi and maxi > 0:
            btns.append(MDRaisedButton(text="VIGILAR", md_bg_color=[1, 0, 0, 1],
                                          on_release=lambda x: self.set_watch(ip)))
        
        self.dialog = MDDialog(title="Opciones", buttons=btns)
        self.dialog.open()

    def prepare_scan(self, ip):
        if self.dialog: 
            self.dialog.dismiss()
            self.dialog = None
        
        Snackbar(
            text="Interceptando comunicaciones...", 
            bg_color=self.neon_orange,
            snackbar_x="10dp",
            snackbar_y="10dp"
        ).open()
        
        Thread(target=self.bg_load_players, args=(ip,), daemon=True).start()

    def bg_load_players(self, ip):
        _, players = get_server_data(ip, True)
        self.show_final_players(players)

    @mainthread
    def show_final_players(self, players):
        list_v = MDList()
        if not players:
            list_v.add_widget(OneLineIconListItem(text="Servidor vacío o bloqueado"))
        else:
            for name, score in players:
                item = OneLineIconListItem(text=f"{name}  [b]{score} pts[/b]", theme_text_color="Custom", text_color=[1,1,1,1])
                item.add_widget(IconLeftWidget(icon="account-outline", theme_icon_color="Custom", icon_color=self.neon_orange))
                list_v.add_widget(item)
        
        self.dialog = MDDialog(
            title="OPERATIVOS ONLINE",
            type="custom",
            content_cls=ScrollView(size_hint_y=None, height="300dp", content=list_v),
            buttons=[MDFlatButton(text="CERRAR", on_release=lambda x: self.dialog.dismiss())]
        )
        self.dialog.open()

    def set_watch(self, ip):
        self.watching_ip = ip
        if self.dialog: self.dialog.dismiss()
        Clock.schedule_once(lambda dt: MDDialog(title="Vigilancia Activa", text=f"Alerta cuando haya espacio.").open(), 0.4)

    def check_watchlist(self, dt):
        if self.watching_ip:
            info, _ = get_server_data(self.watching_ip)
            if info and info['cur_players'] < info['max_players']:
                self.trigger_alert(info['name'])
                self.watching_ip = None

    @mainthread
    def trigger_alert(self, name):
        MDDialog(title="¡SLOT LIBRE!", text=f"El servidor {name} tiene espacio.").open()

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

    def show_add_dialog(self):
        self.field = MDTextField(hint_text="IP:Puerto", mode="round")
        self.dialog = MDDialog(title="Añadir Servidor", type="custom", content_cls=self.field,
            buttons=[MDFlatButton(text="CANCELAR", on_release=lambda x: self.dialog.dismiss()),
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
