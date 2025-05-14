import subprocess
import time
import platform

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
        print("Iniciando o coordenador...")
        coordinator = subprocess.Popen([python_cmd, 'berkeley_coordinator.py'])
        processes.append(coordinator)
        
        time.sleep(2)
        
        print("Iniciando os clientes...")
        for i in range(1, 5):
            print(f"Iniciando Cliente-{i}...")
            client = subprocess.Popen([python_cmd, 'berkeley_client.py', f'Cliente-{i}'])
            processes.append(client)
            time.sleep(0.5)  
        
        print("\n*** TODOS OS PROCESSOS ESTÃO EM EXECUÇÃO ***")
        print("Para encerrar todos os processos, pressione Ctrl+C.")
        print("=" * 80)
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n*** ENCERRANDO TODOS OS PROCESSOS ***")
        
        for process in processes:
            try:
                if platform.system() == 'Windows':
                    process.kill()
                else:
                    process.terminate() 
                    time.sleep(0.2)
                    if process.poll() is None:
                        process.kill() 
            except Exception as e:
                print(f"Erro ao encerrar processo: {e}")
        
        print("Todos os processos foram encerrados.")

if __name__ == "__main__":
    run_berkeley_system()