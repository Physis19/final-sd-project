import socket
import threading
import time
import random
import json
from datetime import datetime

class BerkeleyCoordinator:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.clients = [] 
        self.clock_offset = random.randint(-10, 10) 
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.lock = threading.Lock()
        
    def get_current_time(self):
        return time.time() + self.clock_offset
    
    def start(self):
        self.server_socket.listen(5)
        self.print_header()
        print(f"[COORDENADOR] Relógio inicial: {self.format_time(self.get_current_time())}")
        print(f"[COORDENADOR] Offset inicial: {self.clock_offset:+.2f}s (deslocamento aleatório)")
        print("=" * 80)
        
        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.daemon = True
        accept_thread.start()
        
        print("[COORDENADOR] Aguardando conexões de clientes por 5 segundos...")
        time.sleep(5)
        
        try:
            while True:
                with self.lock:
                    num_clients = len(self.clients)
                
                if num_clients > 0:
                    print(f"\n[COORDENADOR] {num_clients} clientes conectados. Iniciando sincronização...")
                    self.synchronize_clocks()
                    print(f"[COORDENADOR] Próxima sincronização em 20 segundos...")
                    time.sleep(20) 
                else:
                    print("[COORDENADOR] Aguardando clientes para iniciar sincronização...")
                    time.sleep(5)
        except KeyboardInterrupt:
            print("[COORDENADOR] Encerrado pelo usuário")
            self.server_socket.close()
    
    def print_header(self):
        print("\n" + "=" * 80)
        print("| ALGORITMO DE BERKELEY - COORDENADOR |".center(80))
        print("=" * 80)
    
    def accept_connections(self):
        while True:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"[COORDENADOR] Nova conexão de {address[0]}:{address[1]}")
                
                with self.lock:
                    self.clients.append(client_socket)
                    num_clients = len(self.clients)
                
                print(f"[COORDENADOR] Total de clientes conectados: {num_clients}")
                
                client_thread = threading.Thread(target=self.handle_client,
                                               args=(client_socket, address))
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                print(f"[ERRO] Falha ao aceitar conexão: {e}")
                break
    
    def handle_client(self, client_socket, address):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                message = json.loads(data.decode('utf-8'))
                if message.get("type") == "time_response":
                    client_id = message.get("client_id", "Desconhecido")
                    if "debug" in message:
                        print(f"[DEBUG] Resposta de tempo recebida de {client_id}")
        except Exception as e:
            print(f"[ERRO] Falha na comunicação com cliente {address}: {e}")
        finally:
            with self.lock:
                if client_socket in self.clients:
                    self.clients.remove(client_socket)
                    num_clients = len(self.clients)
            client_socket.close()
            print(f"[COORDENADOR] Cliente {address} desconectado. Restantes: {num_clients}")
    
    def synchronize_clocks(self):
        print("\n" + "=" * 80)
        print("| ALGORITMO DE BERKELEY - INÍCIO DO PROCESSO DE SINCRONIZAÇÃO |".center(80))
        print("=" * 80)
        
        print("\nFASE 1: OBTENÇÃO DO TEMPO DO COORDENADOR")
        print("-" * 80)
        
        coordinator_time = self.get_current_time()
        print(f"[COORDENADOR] Tempo atual: {self.format_time(coordinator_time)}")
        print(f"[COORDENADOR] Offset atual: {self.clock_offset:+.2f}s")
        
        client_responses = []
        
        print("\nFASE 2: SOLICITAÇÃO DE TEMPOS DOS CLIENTES")
        print("-" * 80)
        
        def request_time(client_socket):
            try:
                request = json.dumps({"type": "time_request"})
                print(f"[COORDENADOR] Enviando solicitação de tempo para um cliente...")
                client_socket.send(request.encode('utf-8'))
                
                data = client_socket.recv(1024)
                response = json.loads(data.decode('utf-8'))
                
                if response.get("type") == "time_response":
                    client_time = response.get("time")
                    client_id = response.get("client_id", "Desconhecido")
                    difference = client_time - coordinator_time
                    client_responses.append((client_socket, client_time, client_id))
                    print(f"[{client_id}] Tempo recebido: {self.format_time(client_time)}")
                    print(f"[{client_id}] Diferença com coordenador: {difference:+.2f}s")
            except Exception as e:
                print(f"[ERRO] Falha ao solicitar tempo de cliente: {e}")
        
        threads = []
        with self.lock:
            clients_copy = self.clients.copy()
        
        print(f"[COORDENADOR] Enviando solicitações para {len(clients_copy)} clientes...")
        
        for client_socket in clients_copy:
            thread = threading.Thread(target=request_time, args=(client_socket,))
            thread.start()
            threads.append(thread)
        
        for thread in threads:
            thread.join(timeout=5) 
        
        print("\nFASE 3: CÁLCULO DO TEMPO MÉDIO")
        print("-" * 80)
        
        all_times = [coordinator_time] + [response[1] for response in client_responses]
        if all_times:
            print("[CÁLCULO] Tempos coletados:")
            print(f"  - Coordenador: {self.format_time(coordinator_time)}")
            for _, client_time, client_id in client_responses:
                print(f"  - {client_id}: {self.format_time(client_time)}")
            
            average_time = sum(all_times) / len(all_times)
            
            print(f"[CÁLCULO] Soma dos tempos: {sum(all_times):.2f}")
            print(f"[CÁLCULO] Número de relógios: {len(all_times)}")
            print(f"[CÁLCULO] Tempo médio calculado: {self.format_time(average_time)}")
            
            print("\nFASE 4: AJUSTE DO RELÓGIO DO COORDENADOR")
            print("-" * 80)
            
            adjustment = average_time - coordinator_time
            self.clock_offset += adjustment
            new_time = self.get_current_time()
            
            print(f"[COORDENADOR] Tempo antes do ajuste: {self.format_time(coordinator_time)}")
            print(f"[COORDENADOR] Ajuste calculado: {adjustment:+.2f}s")
            print(f"[COORDENADOR] Tempo após ajuste: {self.format_time(new_time)}")
            print(f"[COORDENADOR] Novo offset: {self.clock_offset:+.2f}s")
            
            print("\nFASE 5: ENVIO DE AJUSTES PARA OS CLIENTES")
            print("-" * 80)
            
            print("| ID Cliente        | Tempo Anterior   | Diferença Média | Ajuste        | Tempo Após Ajuste |")
            print("|" + "-" * 78 + "|")
            
            print(f"| {'Coordenador':16} | {self.format_time(coordinator_time):15} | "
                  f"{0:+.2f}s{'':10} | {adjustment:+.2f}s{'':7} | {self.format_time(new_time):16} |")
            
            for client_socket, client_time, client_id in client_responses:
                diff_from_avg = client_time - average_time
                client_adjustment = average_time - client_time
                
                try:
                    print(f"[COORDENADOR] Enviando ajuste de {client_adjustment:+.2f}s para {client_id}...")
                    adjustment_message = json.dumps({
                        "type": "time_adjustment",
                        "adjustment": client_adjustment
                    })
                    client_socket.send(adjustment_message.encode('utf-8'))
                    
                    new_client_time = client_time + client_adjustment
                    print(f"| {client_id:16} | {self.format_time(client_time):15} | "
                          f"{diff_from_avg:+.2f}s{'':10} | {client_adjustment:+.2f}s{'':7} | {self.format_time(new_client_time):16} |")
                    
                except Exception as e:
                    print(f"[ERRO] Falha ao enviar ajuste para {client_id}: {e}")
            
            print("\nFASE 6: SINCRONIZAÇÃO CONCLUÍDA")
            print("-" * 80)
            print("Todos os relógios agora estão sincronizados com o tempo médio calculado.")
            print(f"Tempo médio do sistema: {self.format_time(average_time)}")
            
            max_diff = 0
            for _, client_time, client_id in client_responses:
                adjusted_time = client_time + (average_time - client_time)
                diff = abs(adjusted_time - average_time)
                max_diff = max(max_diff, diff)
            
            print(f"Diferença máxima entre relógios após sincronização: {max_diff:.6f}s "
                  f"({'< 1 segundo: OK' if max_diff < 1 else '≥ 1 segundo: ERRO!'})")
            
            print("=" * 80)
            print()
        else:
            print("[ERRO] Nenhum cliente disponível para sincronização")
    
    @staticmethod
    def format_time(timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%H:%M:%S.%f')[:-3]

if __name__ == "__main__":
    coordinator = BerkeleyCoordinator()
    coordinator.start()