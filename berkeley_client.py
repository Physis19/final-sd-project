import socket
import json
import time
import random
from datetime import datetime
import sys

class BerkeleyClient:
    def __init__(self, host='localhost', port=5000, client_id=None):
        self.host = host
        self.port = port
        self.client_id = client_id or f"Cliente-{random.randint(1000, 9999)}"
        self.clock_offset = random.randint(-10, 10)
        self.socket = None
        self.connected = False
        self.running = True
    
    def get_current_time(self):
        return time.time() + self.clock_offset
    
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            self.print_header()
            print(f"[{self.client_id}] Relógio inicial: {self.format_time(self.get_current_time())}")
            print(f"[{self.client_id}] Offset inicial: {self.clock_offset:+.2f}s (deslocamento aleatório)")
            print("=" * 80)
            return True
        except Exception as e:
            print(f"[ERRO] Erro ao conectar ao coordenador: {e}")
            return False
    
    def print_header(self):
        print("\n" + "=" * 80)
        print(f"| ALGORITMO DE BERKELEY - CLIENTE: {self.client_id} |".center(80))
        print("=" * 80)
    
    def start(self):
        if not self.connect():
            return
        
        try:
            while self.running:
                try:
                    data = self.socket.recv(1024)
                    if not data:
                        print(f"[{self.client_id}] Conexão com o coordenador perdida")
                        break
                    
                    self.handle_message(data)
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"[{self.client_id}] Erro ao receber mensagem: {e}")
                    break
        finally:
            if self.socket:
                self.socket.close()
            print(f"[{self.client_id}] Desconectado")
    
    def handle_message(self, data):
        message = json.loads(data.decode('utf-8'))
        message_type = message.get("type")
        
        if message_type == "time_request":
            current_time = self.get_current_time()
            print("\n" + "=" * 80)
            print(f"| {self.client_id} - SOLICITAÇÃO DE TEMPO RECEBIDA |".center(80))
            print("=" * 80)
            
            print(f"[{self.client_id}] Recebida solicitação de tempo do coordenador")
            print(f"[{self.client_id}] Tempo atual: {self.format_time(current_time)}")
            print(f"[{self.client_id}] Offset atual: {self.clock_offset:+.2f}s")
            
            response = json.dumps({
                "type": "time_response",
                "time": current_time,
                "client_id": self.client_id
            })
            self.socket.send(response.encode('utf-8'))
            print(f"[{self.client_id}] Enviando resposta ao coordenador: {self.format_time(current_time)}")
            
        elif message_type == "time_adjustment":
            adjustment = message.get("adjustment")
            old_time = self.get_current_time()
            
            print("\n" + "=" * 80)
            print(f"| {self.client_id} - AJUSTE DE RELÓGIO RECEBIDO |".center(80))
            print("=" * 80)
            
            print("\nPROCESSO DE AJUSTE DO RELÓGIO:")
            print("-" * 80)
            print(f"[{self.client_id}] Tempo antes do ajuste: {self.format_time(old_time)}")
            print(f"[{self.client_id}] Offset antes do ajuste: {self.clock_offset:+.2f}s")
            print(f"[{self.client_id}] Ajuste recebido do coordenador: {adjustment:+.2f}s")
            
            self.clock_offset += adjustment
            new_time = self.get_current_time()
            
            print(f"[{self.client_id}] Novo offset do relógio: {self.clock_offset:+.2f}s")
            print(f"[{self.client_id}] Tempo após ajuste: {self.format_time(new_time)}")
            
            print("\nRESUMO DO AJUSTE:")
            print("-" * 80)
            print(f"Tempo antes: {self.format_time(old_time)}")
            print(f"Ajuste aplicado: {adjustment:+.2f} segundos")
            print(f"Tempo após: {self.format_time(new_time)}")
            print("=" * 80)
    
    def stop(self):
        self.running = False
        if self.socket:
            self.socket.close()
    
    @staticmethod
    def format_time(timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%H:%M:%S.%f')[:-3]

if __name__ == "__main__":
    client_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    client = BerkeleyClient(client_id=client_id)
    try:
        client.start()
    except KeyboardInterrupt:
        print("Cliente encerrado pelo usuário")
        client.stop()