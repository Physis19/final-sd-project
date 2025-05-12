import socket
import json
import time
import random
import threading
from datetime import datetime
import colorama
from colorama import Fore, Back, Style

# Inicializa o colorama para funcionar em todos os sistemas
colorama.init(autoreset=True)

class BerkeleyClient:
    def __init__(self, host='localhost', port=5000, client_id=None):
        self.host = host
        self.port = port
        self.client_id = client_id or f"Cliente-{random.randint(1000, 9999)}"
        self.clock_offset = random.randint(-10, 10)  # Deslocamento aleatório do relógio (-10 a 10 segundos)
        self.socket = None
        self.connected = False
        self.running = True
    
    def get_current_time(self):
        """Retorna o tempo atual do cliente com o deslocamento"""
        return time.time() + self.clock_offset
    
    def connect(self):
        """Conecta ao servidor coordenador"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            self.print_header()
            print(f"{Fore.GREEN}Conectado ao coordenador em {self.host}:{self.port}")
            print(f"{Fore.YELLOW}Relógio inicial: {Fore.CYAN}{self.format_time(self.get_current_time())}"
                  f"{Fore.YELLOW} (offset: {Fore.RED}{self.clock_offset:+.2f}s{Fore.YELLOW})")
            print(f"{Fore.WHITE}{'=' * 60}")
            return True
        except Exception as e:
            print(f"{Fore.RED}Erro ao conectar ao coordenador: {e}")
            return False
    
    def print_header(self):
        """Exibe um cabeçalho formatado"""
        print(f"\n{Fore.WHITE}{Back.BLUE}{Style.BRIGHT} ALGORITMO DE BERKELEY - {self.client_id} {Style.RESET_ALL}")
        print(f"{Fore.WHITE}{'=' * 60}")
    
    def start(self):
        """Inicia o cliente e aguarda solicitações do coordenador"""
        if not self.connect():
            return
        
        try:
            while self.running:
                try:
                    data = self.socket.recv(1024)
                    if not data:
                        # Servidor desconectado
                        print(f"{Fore.RED}Conexão com o coordenador perdida")
                        break
                    
                    self.handle_message(data)
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"{Fore.RED}Erro ao receber mensagem: {e}")
                    break
        finally:
            if self.socket:
                self.socket.close()
            print(f"{Fore.YELLOW}{self.client_id} desconectado")
    
    def handle_message(self, data):
        """Processa mensagens recebidas do coordenador"""
        message = json.loads(data.decode('utf-8'))
        message_type = message.get("type")
        
        if message_type == "time_request":
            # Coordenador solicitou o tempo atual
            current_time = self.get_current_time()
            print(f"\n{Fore.WHITE}{Back.CYAN} SOLICITAÇÃO DE TEMPO RECEBIDA {Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Tempo atual: {Fore.CYAN}{self.format_time(current_time)}")
            
            response = json.dumps({
                "type": "time_response",
                "time": current_time,
                "client_id": self.client_id
            })
            self.socket.send(response.encode('utf-8'))
            print(f"{Fore.GREEN}Tempo enviado ao coordenador")
            
        elif message_type == "time_adjustment":
            # Coordenador enviou um ajuste de tempo
            adjustment = message.get("adjustment")
            old_time = self.get_current_time()
            
            print(f"\n{Fore.WHITE}{Back.GREEN} AJUSTE DE RELÓGIO RECEBIDO {Style.RESET_ALL}")
            print(f"{Fore.WHITE}{'-' * 60}")
            print(f"{Fore.YELLOW}Tempo antes do ajuste: {Fore.CYAN}{self.format_time(old_time)}")
            print(f"{Fore.GREEN}Ajuste recebido: {Fore.WHITE}{adjustment:+.2f}s")
            
            # Aplica o ajuste
            self.clock_offset += adjustment
            new_time = self.get_current_time()
            
            print(f"{Fore.YELLOW}Tempo após ajuste: {Fore.CYAN}{self.format_time(new_time)}")
            print(f"{Fore.WHITE}Novo offset do relógio: {Fore.RED}{self.clock_offset:+.2f}s")
            print(f"{Fore.WHITE}{'-' * 60}")
    
    def stop(self):
        """Para o cliente"""
        self.running = False
        if self.socket:
            self.socket.close()
    
    @staticmethod
    def format_time(timestamp):
        """Formata um timestamp em uma string legível"""
        return datetime.fromtimestamp(timestamp).strftime('%H:%M:%S.%f')[:-3]

if __name__ == "__main__":
    # Você pode passar um ID de cliente como argumento, ou será gerado um aleatório
    import sys
    client_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    client = BerkeleyClient(client_id=client_id)
    try:
        client.start()
    except KeyboardInterrupt:
        print(f"{Fore.RED}Cliente encerrado pelo usuário")
        client.stop()