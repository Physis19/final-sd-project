import subprocess
import time
import platform
import os
import signal

def print_header():
    print("\n*** SISTEMA DE SINCRONIZAÇÃO DE RELÓGIOS - ALGORITMO DE BERKELEY ***")
    print("=" * 80)
    print("Este script iniciará o coordenador e 4 processos clientes para demonstrar")
    print("o algoritmo de Berkeley para sincronização de relógios em sistemas distribuídos.")
    print("=" * 80)

def run_berkeley_system():
    processes = []
    
    python_cmd = 'python' if platform.system() == 'Windows' else 'python3'
    
    print_header()
    
    try:
        # Verificando se os arquivos existem
        required_files = ['berkeley_coordinator.py', 'berkeley_client.py']
        for file in required_files:
            if not os.path.exists(file):
                print(f"ERRO: O arquivo {file} não foi encontrado!")
                return
        
        print("Iniciando o coordenador...")
        coordinator = subprocess.Popen([python_cmd, 'berkeley_coordinator.py'])
        processes.append(coordinator)
        
        time.sleep(2)  # Dar tempo para o coordenador inicializar
        
        print("Iniciando os clientes...")
        for i in range(1, 5):
            print(f"Iniciando Cliente-{i}...")
            client = subprocess.Popen([python_cmd, 'berkeley_client.py', f'Cliente-{i}'])
            processes.append(client)
            time.sleep(0.5)  # Pequeno intervalo entre inicializações
        
        print("\n*** TODOS OS PROCESSOS ESTÃO EM EXECUÇÃO ***")
        print("Para encerrar todos os processos, pressione Ctrl+C.")
        print("=" * 80)
        
        # Loop principal - mantém o script rodando até Ctrl+C
        while True:
            time.sleep(1)
            
            # Verificar se algum processo terminou inesperadamente
            for process in processes[:]:
                if process.poll() is not None:  # Processo terminou
                    print(f"Um processo terminou inesperadamente com código {process.returncode}")
                    processes.remove(process)
            
            if not processes:
                print("Todos os processos terminaram. Encerrando.")
                break
            
    except KeyboardInterrupt:
        print("\n*** ENCERRANDO TODOS OS PROCESSOS ***")
        
        for process in processes:
            try:
                if platform.system() == 'Windows':
                    process.kill()
                else:
                    # Em sistemas Unix, SIGTERM é mais gracioso que kill
                    process.send_signal(signal.SIGTERM)
                    
                    # Dar um tempo para o processo terminar graciosamente
                    time.sleep(0.2)
                    
                    # Se ainda estiver rodando, use SIGKILL
                    if process.poll() is None:
                        process.kill()
                        
            except Exception as e:
                print(f"Erro ao encerrar processo: {e}")
        
        print("Todos os processos foram encerrados.")

if __name__ == "__main__":
    run_berkeley_system()