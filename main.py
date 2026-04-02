import socket
import json
import os
from threading import Thread
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import mainthread
from kivy.properties import StringProperty

# --- LÓGICA DE RED SEGURA ---
def get_server_info(ip, port):
    QUERY = b'\xFF\xFF\xFF\xFFTSource Engine Query\x00'
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1.5) # Tiempo corto para no trabar
        sock.sendto(QUERY, (ip, int(port)))
        data, _ = sock.recvfrom(4096)
        sock.close()
        # Parseo ultra-básico para evitar errores de split
        content = data[6:]
        parts = content.split(b'\x00')
        return {
            "name": parts[0].decode('utf-8', 'ignore')[:20],
            "players": f"{parts[4][0]}/{parts[4][1]}" if len(parts) > 4 else "??",
            "ip": f"{ip}:{port}"
        }
    except:
        return None

# --- INTERFAZ ---
KV = """
#:set neon [0, 1, 0.3, 1]

<ServerCard@BoxLayout>:
    server_name: ''
    server_ip: ''
    player_count: ''
    size_hint_y: None
    height: '80dp'
    padding: '10dp'
    canvas.before:
        Color:
            rgba: [0.1, 0.1, 0.15, 1]
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        Label:
            text: root.server_name
            bold: True
            halign: 'left'
            text_size: self.size
        Label:
            text: root.server_ip
            font_size: '10sp'
            color: [0.5, 0.5, 0.5, 1]

    Label:
        text: root.player_count
        color: neon
        bold: True
        size_hint_x: 0.3

ScreenManager:
    MenuScreen:
    ServerListScreen:

<MenuScreen>:
    name: 'menu'
    BoxLayout:
        orientation: 'vertical'
        padding: '40dp'
        spacing: '20dp'
        Label:
            text: "KODA\\nTACTICAL"
            font_size: '40sp'
            color: neon
            bold: True
            halign: 'center'
        Button:
            text: "SCAN"
            size_hint_y: None
            height: '60dp'
            on_release: app.root.current = 'servers'

<ServerListScreen>:
    name: 'servers'
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: "< BACK"
            size_hint_y: None
            height: '50dp'
            on_release: app.root.current = 'menu'
        ScrollView:
            BoxLayout:
                id: container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: '5dp'
"""

class MenuScreen(Screen): pass
class ServerListScreen(Screen):
    def on_enter(self):
        self.ids.container.clear_widgets()
        Thread(target=self.run_scan, daemon=True).start()

    def run_scan(self):
        # IPs de prueba fijas para asegurar que al menos cargue algo
        test_ips = [("45.235.98.50", 27015), ("181.119.141.22", 27015)]
        for ip, port in test_ips:
            info = get_server_info(ip, port)
            if info: self.add_ui(info)

    @mainthread
    def add_ui(self, info):
        from kivy.factory import Factory
        card = Factory.ServerCard()
        card.server_name = info['name']
        card.server_ip = info['ip']
        card.player_count = info['players']
        self.ids.container.add_widget(card)

class KodaTacticalApp(App):
    def build(self):
        # CARGA SEGURA DEL KV
        try:
            return Builder.load_string(KV)
        except Exception as e:
            print(f"KV Error: {e}")
            return Screen()

if __name__ == '__main__':
    KodaTacticalApp().run()
