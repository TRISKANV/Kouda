import socket
import struct
import json
import os
from threading import Thread
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import mainthread
from kivy.properties import StringProperty, ListProperty

# Configuración visual para PC (Simulación de móvil)
Window.clearcolor = (0.02, 0.02, 0.03, 1)
Window.size = (360, 640)

# ==========================================
# MOTOR DE RED (A2S PROTOCOL)
# ==========================================
def get_server_info(ip, port):
    QUERY = b'\xFF\xFF\xFF\xFFTSource Engine Query\x00'
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
        sock.sendto(QUERY, (ip, int(port)))
        data, _ = sock.recvfrom(4096)
        sock.close()
        content = data[6:]
        name, end = content.split(b'\x00', 1)
        map_name, end = end.split(b'\x00', 1)
        folder, end = end.split(b'\x00', 1)
        game, end = end.split(b'\x00', 1)
        return {
            "name": name.decode('utf-8', 'ignore'),
            "players": f"{end[2]}/{end[3]}",
            "ip": f"{ip}:{port}"
        }
    except:
        return None

# ==========================================
# INTERFAZ TÁCTICA (KV LANGUAGE)
# ==========================================
KV = """
#:set color_neon [0.0, 1.0, 0.25, 1]
#:set color_back [0.02, 0.02, 0.03, 1]

<TacticalButton@Button>:
    background_normal: ''
    background_color: [0,0,0,0]
    color: color_neon
    bold: True
    size_hint_y: None
    height: '55dp'
    canvas.before:
        Color:
            rgba: color_neon if self.state == 'normal' else [1,1,1,0.2]
        Line:
            width: 1.1
            rectangle: (self.x, self.y, self.width, self.height)

<ServerCard>:
    orientation: 'horizontal'
    size_hint_y: None
    height: '85dp'
    padding: '12dp'
    canvas.before:
        Color:
            rgba: [0.05, 0.05, 0.1, 1]
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: [0, 1, 0.25, 0.15]
        Line:
            width: 1
            rectangle: (self.x, self.y, self.width, self.height)

    BoxLayout:
        orientation: 'vertical'
        Label:
            text: root.server_name
            bold: True
            font_size: '15sp'
            halign: 'left'
            text_size: self.size
        Label:
            text: root.server_ip
            font_size: '11sp'
            color: [0.5, 0.5, 0.5, 1]
            halign: 'left'
            text_size: self.size

    Label:
        text: root.player_count
        size_hint_x: 0.3
        color: color_neon
        font_size: '20sp'
        bold: True

ScreenManager:
    MenuScreen:
    ServerListScreen:
    AddServerScreen:

<MenuScreen>:
    name: 'menu'
    BoxLayout:
        orientation: 'vertical'
        padding: '30dp'
        spacing: '15dp'
        Label:
            text: "KODA\\nTACTICAL"
            font_size: '45sp'
            bold: True
            color: color_neon
            halign: 'center'
        Widget:
        TacticalButton:
            text: "SCAN NETWORK"
            on_release: app.root.current = 'servers'
        TacticalButton:
            text: "ADD NODE (IP)"
            on_release: app.root.current = 'add_server'

<ServerListScreen>:
    name: 'servers'
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: None
            height: '60dp'
            padding: '10dp'
            Button:
                text: "< BACK"
                color: color_neon
                background_color: [0,0,0,0]
                on_release: app.root.current = 'menu'
        ScrollView:
            BoxLayout:
                id: container
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: '15dp'
                spacing: '10dp'

<AddServerScreen>:
    name: 'add_server'
    BoxLayout:
        orientation: 'vertical'
        padding: '25dp'
        spacing: '15dp'
        Label:
            text: "NODE CONFIGURATION"
            color: color_neon
            size_hint_y: None
            height: '50dp'
        TextInput:
            id: ip_in
            hint_text: "SERVER IP"
            multiline: False
            size_hint_y: None
            height: '50dp'
            background_color: [0.1, 0.1, 0.1, 1]
            foreground_color: [1, 1, 1, 1]
        TextInput:
            id: port_in
            hint_text: "PORT (27015)"
            multiline: False
            size_hint_y: None
            height: '50dp'
            background_color: [0.1, 0.1, 0.1, 1]
            foreground_color: [1, 1, 1, 1]
        TacticalButton:
            text: "SAVE TO DATABASE"
            on_release: 
                app.add_server(ip_in.text, port_in.text)
                app.root.current = 'menu'
        TacticalButton:
            text: "CANCEL"
            on_release: app.root.current = 'menu'
        Widget:
"""

# ==========================================
# LÓGICA DE APLICACIÓN
# ==========================================
class ServerCard(BoxLayout):
    server_name = StringProperty('')
    server_ip = StringProperty('')
    player_count = StringProperty('')

class MenuScreen(Screen): pass
class ServerListScreen(Screen):
    def on_enter(self):
        self.ids.container.clear_widgets()
        Thread(target=self.fetch_data, daemon=True).start()

    def fetch_data(self):
        servers = App.get_running_app().load_data()
        for s in servers:
            data = get_server_info(s['ip'], s['port'])
            if data: self.update_ui(data)

    @mainthread
    def update_ui(self, data):
        self.ids.container.add_widget(ServerCard(
            server_name=data['name'],
            server_ip=data['ip'],
            player_count=data['players']
        ))

class AddServerScreen(Screen): pass

class KodaTacticalApp(App):
    def build(self):
        return Builder.load_string(KV)

    def get_db_path(self):
        return os.path.join(self.user_data_dir, 'nodes.json')

    def load_data(self):
        if os.path.exists(self.get_db_path()):
            with open(self.get_db_path(), 'r') as f: return json.load(f)
        return []

    def add_server(self, ip, port):
        data = self.load_data()
        data.append({"ip": ip, "port": port})
        with open(self.get_db_path(), 'w') as f: json.dump(data, f)

if __name__ == '__main__':
    KodaTacticalApp().run()
