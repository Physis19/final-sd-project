import socket
import threading
import time
import random
import json
from datetime import datetime, timedelta
import colorama
from colorama import Fore, Back, Style

# Inicializa o colorama para funcionar em todos os sistemas
colorama.init(autoreset=True)

class BerkeleyCoordinator:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.clients = []  # Lista para armazenar conexões de clientes
        self.clock_offset = random.randint(-10, 10)  # Deslocamento aleatório do relógio (-10 a 10 segundos)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.lock = threading.Lock()
        
    def get_current_time(self):
        """Retorna o tempo atual do coordenador com o deslocamento"""
        return time.time() + self.clock_offset
    
    def start(self):
        """Inicia o servidor e aguarda conexões"""
        self.server_socket.listen(5)
        self.print_header()
        print(f"{Fore.GREEN}Coordenador iniciado em {self.host}:{self.port}")
        print(f"{Fore.YELLOW}Relógio inicial do coordenador: {Fore.CYAN}{self.format_time(self.get_current_time())}{Fore.YELLOW} (offset: {Fore.RED}{self.clock_offset:+.2f}s{Fore.YELLOW})")
        print(f"{Fore.WHITE}{'=' * 60}")
        
        # Thread para aceitar conexões
        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.daemon = True
        accept_thread.start()
        
        # Aguarda um tempo para alguns clientes se conectarem
        time.sleep(5)
        
        # Loop principal
        try:
            while True:
                if self.clients:
                    self.synchronize_clocks()
                    time.sleep(20)  # Sincroniza a cada 20 segundos
                else:
                    print(f"{Fore.YELLOW}Aguardando clientes...")
                    time.sleep(5)
        except KeyboardInterrupt:
            print(f"{Fore.RED}Coordenador encerrado")
            self.server_socket.close()
    
    def print_header(self):
        """Exibe um cabeçalho formatado"""
        print(f"\n{Fore.WHITE}{Back.BLUE}{Style.BRIGHT} ALGORITMO DE BERKELEY - COORDENADOR {Style.RESET_ALL}")
        print(f"{Fore.WHITE}{'=' * 60}")
    
    def accept_connections(self):
        """Aceita conexões de clientes"""
        while True:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"{Fore.GREEN}Cliente conectado de {address[0]}:{address[1]}")
                
                # Adiciona cliente à lista
                with self.lock:
                    self.clients.append(client_socket)
                
                # Inicia thread para lidar com este cliente
                client_thread = threading.Thread(target=self.handle_client,
                                               args=(client_socket, address))
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                print(f"{Fore.RED}Erro ao aceitar conexão: {e}")
                break
    
    def handle_client(self, client_socket, address):
        """Manipula comunicação com um cliente específico"""
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    # Cliente desconectado
                    break
                
                message = json.loads(data.decode('utf-8'))
                if message.get("type") == "time_response":
                    # Processamento feito em synchronize_clocks
                    pass
        except Exception as e:
            print(f"{Fore.RED}Erro ao comunicar com cliente {address}: {e}")
        finally:
            # Remove cliente da lista
            with self.lock:
                if client_socket in self.clients:
                    self.clients.remove(client_socket)
            client_socket.close()
            print(f"{Fore.YELLOW}Cliente {address} desconectado")
    
    def synchronize_clocks(self):
        """Executa o algoritmo de Berkeley para sincronização"""
        print(f"\n{Fore.WHITE}{Back.GREEN}{Style.BRIGHT} INÍCIO DO PROCESSO DE SINCRONIZAÇÃO {Style.RESET_ALL}")
        print(f"{Fore.WHITE}{'-' * 60}")
        
        coordinator_time = self.get_current_time()
        print(f"{Fore.CYAN}► Tempo do coordenador: {self.format_time(coordinator_time)}")
        
        # Coletando tempos dos clientes
        client_times = []
        client_responses = []
        
        def request_time(client_socket):
            try:
                request = json.dumps({"type": "time_request"})
                client_socket.send(request.encode('utf-8'))
                
                # Aguarda resposta
                data = client_socket.recv(1024)
                response = json.loads(data.decode('utf-8'))
                
                if response.get("type") == "time_response":
                    client_time = response.get("time")
                    client_id = response.get("client_id", "Desconhecido")
                    client_responses.append((client_socket, client_time, client_id))
                    print(f"{Fore.CYAN}► Recebido tempo de {client_id}: {self.format_time(client_time)}")
            except Exception as e:
                print(f"{Fore.RED}Erro ao solicitar tempo de cliente: {e}")
        
        # Solicita tempo de todos os clientes em paralelo
        threads = []
        with self.lock:
            clients_copy = self.clients.copy()
        
        print(f"{Fore.YELLOW}Solicitando tempos de {len(clients_copy)} clientes...")
        
        for client_socket in clients_copy:
            thread = threading.Thread(target=request_time, args=(client_socket,))
            thread.start()
            threads.append(thread)
        
        # Aguarda todas as respostas
        for thread in threads:
            thread.join(timeout=5)  # Timeout de 5 segundos para cada cliente
        
        # Calcula a média dos tempos (incluindo o coordenador)
        all_times = [coordinator_time] + [response[1] for response in client_responses]
        if all_times:
            average_time = sum(all_times) / len(all_times)
            
            # Ajusta o relógio do coordenador
            adjustment = average_time - coordinator_time
            self.clock_offset += adjustment
            new_time = self.get_current_time()
            
            print(f"{Fore.WHITE}{'-' * 60}")
            print(f"{Fore.GREEN}► Tempo médio calculado: {self.format_time(average_time)}")
            print(f"{Fore.YELLOW}► Ajuste do coordenador: {Fore.WHITE}{adjustment:+.2f}s")
            print(f"{Fore.GREEN}► Novo tempo do coordenador: {self.format_time(new_time)}")
            print(f"{Fore.WHITE}{'-' * 60}")
            
            # Exibe uma tabela com os ajustes
            print(f"{Fore.WHITE}{Style.BRIGHT}{'ID':15} | {'Tempo Anterior':15} | {'Ajuste':10} | {'Novo Tempo':15}")
            print(f"{Fore.WHITE}{'-' * 60}")
            
            # Linha do coordenador na tabela
            print(f"{Fore.GREEN}{'Coordenador':15} | {self.format_time(coordinator_time):15} | "
                  f"{adjustment:+.2f}s{'':5} | {self.format_time(new_time):15}")
            
            # Envia ajustes para todos os clientes
            for client_socket, client_time, client_id in client_responses:
                client_adjustment = average_time - client_time
                try:
                    adjustment_message = json.dumps({
                        "type": "time_adjustment",
                        "adjustment": client_adjustment
                    })
                    client_socket.send(adjustment_message.encode('utf-8'))
                    
                    # Adiciona cliente à tabela
                    new_client_time = client_time + client_adjustment
                    print(f"{Fore.CYAN}{client_id:15} | {self.format_time(client_time):15} | "
                          f"{client_adjustment:+.2f}s{'':5} | {self.format_time(new_client_time):15}")
                    
                except Exception as e:
                    print(f"{Fore.RED}Erro ao enviar ajuste para {client_id}: {e}")
            
            print(f"{Fore.WHITE}{'-' * 60}")
            print(f"{Fore.WHITE}{Back.GREEN}{Style.BRIGHT} FIM DO PROCESSO DE SINCRONIZAÇÃO {Style.RESET_ALL}")
            print()
        else:
            print(f"{Fore.RED}Nenhum cliente disponível para sincronização")
    
    @staticmethod
    def format_time(timestamp):
        """Formata um timestamp em uma string legível"""
        return datetime.fromtimestamp(timestamp).strftime('%H:%M:%S.%f')[:-3]

if __name__ == "__main__":
    coordinator = BerkeleyCoordinator()
    coordinator.start()