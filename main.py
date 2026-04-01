from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import StringProperty, ListProperty
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
from valve.source.a2s import ServerQuerier
import threading

# Configuración de Estética Koda
ACCENT = [1, 0.55, 0, 1]  # #ff8c00
BG_COLOR = [0.05, 0.05, 0.06, 1]  # #0d0e10
PANEL_COLOR = [0.08, 0.09, 0.11, 1]  # #16171d

class ServerCard(BoxLayout):
    status = StringProperty('offline')
    server_name = StringProperty('BUSCANDO...')
    map_name = StringProperty('---')
    players = StringProperty('0/0')
    ip_port = StringProperty('')
    icon_src = StringProperty('assets/cs16.png')

class KodaApp(App):
    servers_data = ListProperty([])
    current_filter = StringProperty('cs16')

    def build(self):
        self.store = JsonStore('koda_storage.json')
        self.load_servers()
        return self.root

    def load_servers(self):
        if self.store.exists('servers'):
            self.servers_data = self.store.get('servers')['data']

    def set_filter(self, game):
        self.current_filter = game
        self.refresh_all()

    def add_server(self, ip_port):
        if not ip_port: return
        self.servers_data.append({'ip': ip_port, 'game': self.current_filter})
        self.store.put('servers', data=self.servers_data)
        self.refresh_all()

    def refresh_all(self):
        # Aquí es donde ocurre la magia UDP nativa
        for server in self.servers_data:
            if server['game'] == self.current_filter:
                threading.Thread(target=self.query_udp, args=(server['ip'],)).start()

    def query_udp(self, ip_port):
        try:
            ip, port = ip_port.split(':')
            with ServerQuerier((ip, int(port)), timeout=2.0) as sv:
                info = sv.info()
                # Actualizar UI desde el hilo principal
                Clock.schedule_once(lambda dt: self.update_card(ip_port, info))
        except:
            Clock.schedule_once(lambda dt: self.update_card_offline(ip_port))

    def update_card(self, ip, info):
        # Lógica para actualizar los datos en la pantalla
        pass 

if __name__ == '__main__':
    KodaApp().run()
