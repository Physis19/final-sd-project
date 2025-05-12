import subprocess
import time
import os
import signal
import sys
import platform
import colorama
from colorama import Fore, Back, Style

# Inicializa o colorama para funcionar em todos os sistemas
colorama.init(autoreset=True)

def print_header():
    """Exibe um cabeçalho formatado"""
    print(f"\n{Fore.WHITE}{Back.MAGENTA}{Style.BRIGHT} SISTEMA DE SINCRONIZAÇÃO DE RELÓGIOS - ALGORITMO DE BERKELEY {Style.RESET_ALL}")
    print(f"{Fore.WHITE}{'=' * 80}")
    print(f"{Fore.CYAN}Este script iniciará o coordenador e 4 processos clientes para demonstrar")
    print(f"{Fore.CYAN}o algoritmo de Berkeley para sincronização de relógios em sistemas distribuídos.")
    print(f"{Fore.WHITE}{'=' * 80}")

def run_berkeley_system():
    processes = []
    
    # Determina o comando python baseado no sistema operacional
    python_cmd = 'python' if platform.system() == 'Windows' else 'python3'
    
    print_header()
    
    try:
        # Verifica se os módulos necessários estão instalados
        try:
            import colorama
        except ImportError:
            print(f"{Fore.YELLOW}Instalando módulo colorama...")
            subprocess.check_call([python_cmd, '-m', 'pip', 'install', 'colorama'])
            print(f"{Fore.GREEN}Módulo colorama instalado com sucesso!")
        
        # Inicia o coordenador
        print(f"{Fore.GREEN}Iniciando o coordenador...")
        coordinator = subprocess.Popen([python_cmd, 'berkeley_coordinator.py'])
        processes.append(coordinator)
        
        # Aguarda o coordenador iniciar
        time.sleep(2)
        
        # Inicia 4 clientes
        print(f"{Fore.CYAN}Iniciando os clientes...")
        for i in range(1, 5):
            print(f"{Fore.WHITE}Iniciando Cliente-{i}...")
            client = subprocess.Popen([python_cmd, 'berkeley_client.py', f'Cliente-{i}'])
            processes.append(client)
            time.sleep(0.5)  # Pequeno intervalo entre a inicialização dos clientes
        
        print(f"\n{Fore.WHITE}{Back.GREEN}{Style.BRIGHT} TODOS OS PROCESSOS ESTÃO EM EXECUÇÃO {Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Para encerrar todos os processos, pressione {Fore.RED}Ctrl+C{Fore.YELLOW}.")
        print(f"{Fore.WHITE}{'=' * 80}")
        
        # Mantém o script em execução
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.WHITE}{Back.RED}{Style.BRIGHT} ENCERRANDO TODOS OS PROCESSOS {Style.RESET_ALL}")
        
        # Encerra todos os processos de forma apropriada para cada sistema operacional
        for process in processes:
            try:
                if platform.system() == 'Windows':
                    process.kill()
                else:
                    # No Linux e macOS
                    process.terminate()  # Tenta primeiro um encerramento mais suave
                    time.sleep(0.2)
                    if process.poll() is None:  # Se ainda estiver rodando
                        process.kill()  # Usa kill para forçar o encerramento
            except Exception as e:
                print(f"{Fore.RED}Erro ao encerrar processo: {e}")
        
        print(f"{Fore.GREEN}Todos os processos foram encerrados.")

if __name__ == "__main__":
    run_berkeley_system()