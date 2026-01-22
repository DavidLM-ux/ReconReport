#!/usr/bin/env python3
import sys
import shutil
import subprocess
import nmap3
import json
from datetime import datetime
from simple_term_menu import TerminalMenu
import time
import threading

# Codes couleur ANSI
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

banner = f'''{Colors.CYAN}{Colors.BOLD}
 ______                            ______                                
(_____ \\                          (_____ \\                           _   
 _____) )_____  ____ ___  ____     _____) )_____ ____   ___   ____ _| |_ 
|  __  /| ___ |/ ___) _ \\|  _ \\   |  __  /| ___ |  _ \\ / _ \\ / ___|_   _)
| |  \\ \\| ____( (__| |_| | | | |  | |  \\ \\| ____| |_| | |_| | |     | |_ 
|_|   |_|_____)\\____)___/|_| |_|  |_|   |_|_____)  __/ \\___/|_|      \\__)
                                                |_|                      
{Colors.YELLOW}Recon Report V1.0
{Colors.GREEN}Coded by David LE MEUR{Colors.RESET}
'''

# Variables globales
output_mode = None  # "terminal" ou "file"
output_file = None
nmap = None
result = None

class SimpleProgressBar:
    """Barre de progression simple et robuste style pip"""
    
    def __init__(self, desc, total=100):
        self.desc = desc
        self.total = total
        self.current = 0
        self.bar_length = 40
        
    def update(self, amount=1):
        """Mettre à jour la progression"""
        self.current = min(self.current + amount, self.total)
        self._display()
    
    def _display(self):
        """Afficher la barre"""
        percent = int((self.current / self.total) * 100)
        filled = int((self.current / self.total) * self.bar_length)
        bar = '━' * filled + '░' * (self.bar_length - filled)
        
        # Afficher avec retour chariot pour mettre à jour sur la même ligne
        print(f'\r   {bar} {percent}%', end='', flush=True)
    
    def close(self):
        """Finaliser et passer à la ligne"""
        self.current = self.total
        self._display()
        print()  # Nouvelle ligne

def write_output(text, color=""):
    """Fonction pour écrire soit dans le terminal soit dans un fichier"""
    if output_mode == "terminal":
        print(f"{color}{text}{Colors.RESET if color else ''}")
    else:
        # Écrire dans le fichier sans les codes couleur
        output_file.write(text + "\n")

def menu():
    global output_mode, output_file
    
    print(f"{Colors.MAGENTA}{Colors.BOLD}=== MENU ==={Colors.RESET}")
    options = ["Afficher la sortie dans le terminal", "Exporter les résultats dans un fichier"]
    terminal_menu = TerminalMenu(options)
    menu_entry_index = terminal_menu.show()
    
    if menu_entry_index == 0:
        output_mode = "terminal"
        print(f"{Colors.GREEN} Vous avez choisi d'{options[menu_entry_index]}{Colors.RESET}\n")
    else:
        output_mode = "file"
        print(f"{Colors.GREEN} Vous avez choisi d'{options[menu_entry_index]}{Colors.RESET}\n")
    
    # Vérification des arguments
    try:
        target = sys.argv[1]
        
        # Si mode fichier, créer le fichier de sortie
        if output_mode == "file":
            now = datetime.now()
            filename = f"{target}_{now.strftime('%Y%m%d_%H%M')}.txt"
            output_file = open(filename, 'w', encoding='utf-8')
            print(f"{Colors.CYAN} Résultats exportés vers : {filename}{Colors.RESET}\n")
            # Écrire la bannière dans le fichier
            output_file.write(banner.replace(Colors.CYAN, "").replace(Colors.BOLD, "")
                            .replace(Colors.YELLOW, "").replace(Colors.GREEN, "")
                            .replace(Colors.RESET, "") + "\n")
            output_file.write(f"Target: {target}\n")
            output_file.write(f"Date: {now.strftime('%Y-%m-%d %H:%M')}\n")
            output_file.write("="*60 + "\n\n")
            
    except IndexError:
        print(f"{Colors.RED} Usage : {sys.argv[0]} <target>{Colors.RESET}")
        sys.exit(1)

def if_installed(program):
    return shutil.which(program) is not None

def run_command_with_progress(command, desc):
    """
    Exécute une commande subprocess avec une barre de progression fluide
    
    Args:
        command: Liste de commande à exécuter
        desc: Description du scan
    
    Returns:
        tuple: (stdout, stderr, returncode)
    """
    # Afficher le message de début
    print(f"{Colors.CYAN}[*]{Colors.RESET} {desc}...")
    
    # Créer la barre de progression
    pbar = SimpleProgressBar(desc, total=100)
    
    # Variable pour stocker le résultat
    result_container = {'stdout': '', 'stderr': '', 'returncode': None, 'done': False}
    
    def run_command():
        """Exécuter la commande dans un thread"""
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            result_container['stdout'] = result.stdout
            result_container['stderr'] = result.stderr
            result_container['returncode'] = result.returncode
        except Exception as e:
            result_container['stderr'] = str(e)
            result_container['returncode'] = 1
        finally:
            result_container['done'] = True
    
    # Démarrer la commande dans un thread
    thread = threading.Thread(target=run_command)
    thread.start()
    
    # Animer la barre pendant que la commande s'exécute
    current = 0
    while not result_container['done']:
        if current < 95:
            increment = 2
            pbar.update(increment)
            current += increment
        time.sleep(0.1)
    
    # Compléter à 100%
    remaining = 100 - current
    pbar.update(remaining)
    pbar.close()
    
    # Attendre la fin du thread
    thread.join()
    
    return result_container['stdout'], result_container['stderr'], result_container['returncode']

def scan_ssl(ip, port_number):
    """Scan SSL sur le port spécifié"""
    write_output(f"\n###*** SCAN SSL (Port {port_number}) ***###", Colors.MAGENTA + Colors.BOLD)
    write_output(f"Exécution de sslscan sur {ip}:{port_number}", Colors.YELLOW)
    
    if if_installed("sslscan"):
        try:
            stdout, stderr, returncode = run_command_with_progress(
                ["sslscan", f"{ip}:{port_number}"],
                f"Scan SSL {ip}:{port_number}"
            )
            
            # Affichage/écriture des résultats
            if output_mode == "terminal":
                print(stdout)
            else:
                output_file.write(stdout)
                
        except Exception as e:
            write_output(f"Erreur lors de l'exécution de sslscan: {e}", Colors.RED)
    else:
        write_output("sslscan n'est pas installé", Colors.RED)

def scan_port():
    """Scan des ports avec barre de progression"""
    ssl_ports_found = []
    
    # Compter le nombre total de ports à analyser
    total_ports = 0
    for ip, data in result.items():
        if ip not in ["runtime", "stats", "task_results"] and isinstance(data, dict):
            total_ports += len(data.get("ports", []))
    
    # Afficher le message de début et créer la barre
    if total_ports > 0:
        print(f"{Colors.CYAN}[*]{Colors.RESET} Analyse de {total_ports} ports...")
        #pbar = SimpleProgressBar(f"Analyse des ports", total=total_ports)
    
    port_count = 0
    for ip, data in result.items():
        if ip in ["runtime", "stats", "task_results"]:
            continue
        
        write_output(f"\n{'='*60}", Colors.CYAN)
        write_output(f"====== IP: {ip} ======", Colors.CYAN + Colors.BOLD)
        write_output(f"{'='*60}", Colors.CYAN)
        write_output(f"\n###*** SCAN DE PORTS ***###", Colors.MAGENTA + Colors.BOLD)
        
        if isinstance(data, dict):
            ports = data.get("ports", [])
            
            for port in ports:
                port_nb = port.get('portid')
                state = port.get('state')
                service_name = port.get('service', {}).get('name', 'Unknown')
                service_product = port.get('service', {}).get('product', 'Unknown')
                service_version = port.get('service', {}).get('version', 'Unknown')
                
                write_output(f"\n------ PORT {port_nb} ------", Colors.YELLOW + Colors.BOLD)
                
                # Couleur selon l'état du port
                state_color = Colors.GREEN if state == "open" else Colors.RED
                write_output(f"STATUT : {state}", state_color)
                write_output(f"SERVICE : {service_name}", Colors.WHITE)
                write_output(f"TYPE : {service_product}", Colors.WHITE)
                write_output(f"VERSION : {service_version}", Colors.WHITE)
                
                # Détecter les ports SSL
                if port_nb in ["443", "8443"] and state == "open":
                    ssl_ports_found.append((ip, port_nb))
                
                # Mettre à jour la barre de progression
                if total_ports > 0:
                    port_count += 1
                    pbar.update(1)
    
    # Fermer la barre de progression
    if total_ports > 0:
        pbar.close()
    
    # Exécuter scan_ssl uniquement si des ports SSL sont trouvés
    if ssl_ports_found:
        for ip, port_nb in ssl_ports_found:
            scan_ssl(ip, port_nb)
    else:
        write_output(f"\nAucun port SSL (443/8443) ouvert détecté", Colors.YELLOW)
        write_output(f"Pas d'exécution de sslscan", Colors.YELLOW)

def scan_whatweb():
    """Scan WhatWeb avec barre de progression"""
    if if_installed("whatweb"):
        write_output(f"\n###*** SCAN WHATWEB ***###", Colors.MAGENTA + Colors.BOLD)
        
        try:
            stdout, stderr, returncode = run_command_with_progress(
                ["whatweb", "--no-color {sys.argv[1]}"],
                "Scan WhatWeb"
            )
            
            if output_mode == "terminal":
                print(stdout)
            else:
                output_file.write(stdout)
                
        except Exception as e:
            write_output(f"Erreur lors de l'exécution de whatweb: {e}", Colors.RED)
    else:
        write_output(f"\nPas d'exécution de whatweb (non installé)", Colors.YELLOW)

def scan_amass_domain():
    """Scan Amass avec barre de progression"""
    if if_installed("amass"):
        write_output(f"\n###*** SCAN AMASS ***###", Colors.MAGENTA + Colors.BOLD)
        
        try:
            cmd = ["amass", "enum", "-max-depth", "2", "-timeout", "1", "-d", sys.argv[1]]
            stdout, stderr, returncode = run_command_with_progress(
                cmd,
                "Scan Amass"
            )
            
            if output_mode == "terminal":
                print(stdout)
            else:
                output_file.write(stdout)
                
        except Exception as e:
            write_output(f"Erreur lors de l'exécution de amass: {e}", Colors.RED)
    else:
        write_output(f"\nPas d'exécution de amass (non installé)", Colors.YELLOW)

if __name__ == "__main__":
    print(banner)
    menu()
    
    # Initialisation de nmap
    nmap = nmap3.Nmap()
    
    write_output(f"\n Démarrage du scan de {sys.argv[1]}...\n", Colors.CYAN + Colors.BOLD)
    
    try:
        # Scan nmap avec progression fluide
        print(f"{Colors.CYAN}[*]{Colors.RESET} Scan Nmap de {sys.argv[1]}...")
        pbar = SimpleProgressBar("Scan Nmap", total=100)
        
        # Lancer nmap dans un thread
        nmap_done = False
        def run_nmap():
            global result, nmap_done
            result = nmap.nmap_version_detection(sys.argv[1])
            nmap_done = True
        
        thread = threading.Thread(target=run_nmap)
        thread.start()
        
        # Animer pendant le scan
        current = 0
        while not nmap_done:
            if current < 95:
                pbar.update(2)
                current += 2
            time.sleep(0.1)
        
        pbar.update(100 - current)
        pbar.close()
        thread.join()
        
        # Exécution des scans
        scan_port()
        scan_whatweb()
        scan_amass_domain()
        
        write_output(f"\n{'='*60}", Colors.GREEN)
        write_output(f" Scan terminé avec succès!", Colors.GREEN + Colors.BOLD)
        write_output(f"{'='*60}", Colors.GREEN)
        
    except Exception as e:
        write_output(f"\n Erreur lors du scan: {e}", Colors.RED + Colors.BOLD)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Fermer le fichier si ouvert
        if output_file:
            output_file.close()
            print(f"\n{Colors.GREEN} Résultats sauvegardés dans le fichier{Colors.RESET}")