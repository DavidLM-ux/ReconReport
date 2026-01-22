#!/usr/bin/env python3
import sys
import shutil
import subprocess
import nmap3
import json
from datetime import datetime
from simple_term_menu import TerminalMenu

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
(_____ \                          (_____ \                           _   
 _____) )_____  ____ ___  ____     _____) )_____ ____   ___   ____ _| |_ 
|  __  /| ___ |/ ___) _ \|  _ \   |  __  /| ___ |  _ \ / _ \ / ___|_   _)
| |  \ \| ____( (__| |_| | | | |  | |  \ \| ____| |_| | |_| | |     | |_ 
|_|   |_|_____)\____)___/|_| |_|  |_|   |_|_____)  __/ \___/|_|      \__)
                                                |_|                      
{Colors.YELLOW}Recon Report V1.0
{Colors.GREEN}Coded by David LE MEUR{Colors.RESET}
'''

# Variables globales
output_mode = None  # "terminal" ou "file"
output_file = None
nmap = None
result = None

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

def scan_ssl(ip, port_number):
    """Scan SSL sur le port spécifié"""
    write_output(f"\n###*** SCAN SSL (Port {port_number}) ***###", Colors.MAGENTA + Colors.BOLD)
    write_output(f"Exécution de sslscan sur {ip}:{port_number}", Colors.YELLOW)
    
    if if_installed("sslscan"):
        try:
            if output_mode == "terminal":
                subprocess.run(["sslscan", f"{ip}:{port_number}"])
            else:
                result = subprocess.run(["sslscan", f"{ip}:{port_number}"], 
                                      capture_output=True, text=True)
                output_file.write(result.stdout)
        except Exception as e:
            write_output(f"Erreur lors de l'exécution de sslscan: {e}", Colors.RED)
    else:
        write_output("sslscan n'est pas installé", Colors.RED)

def scan_port():
    """Scan des ports et détection des ports SSL"""
    ssl_ports_found = []
    
    for ip, data in result.items():
        if ip in ["runtime", "stats", "task_results"]:
            continue
        
        write_output(f"\n{'='*60}", Colors.CYAN)
        write_output(f"====== IP: {ip} ======", Colors.CYAN + Colors.BOLD)
        write_output(f"{'='*60}", Colors.CYAN)
        write_output(f"\n###*** SCAN DE PORTS ***###", Colors.MAGENTA + Colors.BOLD)
        
        if isinstance(data, dict):
            for port in data.get("ports", []):
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
    
    # Exécuter scan_ssl uniquement si des ports SSL sont trouvés
    if ssl_ports_found:
        for ip, port_nb in ssl_ports_found:
            scan_ssl(ip, port_nb)
    else:
        write_output(f"\nAucun port SSL (443/8443) ouvert détecté", Colors.YELLOW)
        write_output(f"Pas d'exécution de sslscan", Colors.YELLOW)

def scan_whatweb():
    """Scan WhatWeb"""
    if if_installed("whatweb"):
        write_output(f"\n###*** SCAN WHATWEB ***###", Colors.MAGENTA + Colors.BOLD)
        try:
            if output_mode == "terminal":
                subprocess.run(["whatweb", sys.argv[1]])
            else:
                result = subprocess.run(["whatweb", sys.argv[1]], 
                                      capture_output=True, text=True)
                output_file.write(result.stdout)
        except Exception as e:
            write_output(f"Erreur lors de l'exécution de whatweb: {e}", Colors.RED)
    else:
        write_output(f"\nPas d'exécution de whatweb (non installé)", Colors.YELLOW)

def scan_amass_domain():
    """Scan Amass pour la découverte de sous-domaines"""
    if if_installed("amass"):
        write_output(f"\n###*** SCAN AMASS ***###", Colors.MAGENTA + Colors.BOLD)
        try:
            cmd = ["amass", "enum", "-max-depth", "2", "-timeout", "1", "-d", sys.argv[1]]
            if output_mode == "terminal":
                subprocess.run(cmd)
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)
                output_file.write(result.stdout)
        except Exception as e:
            write_output(f"Erreur lors de l'exécution de amass: {e}", Colors.RED)
    else:
        write_output(f"\nPas d'exécution de amass (non installé)", Colors.YELLOW)

if __name__ == "__main__":
    print(banner)
    menu()
    
    # Initialisation de nmap
    nmap = nmap3.Nmap()
    
    write_output(f"\n Démarrage du scan de {sys.argv[1]}...", Colors.CYAN + Colors.BOLD)
    
    try:
        result = nmap.nmap_version_detection(sys.argv[1])
        
        # Exécution des scans
        scan_port()
        scan_whatweb()
        scan_amass_domain()
        
        write_output(f"\n{'='*60}", Colors.GREEN)
        write_output(f" Scan terminé avec succès!", Colors.GREEN + Colors.BOLD)
        write_output(f"{'='*60}", Colors.GREEN)
        
    except Exception as e:
        write_output(f"\n Erreur lors du scan: {e}", Colors.RED + Colors.BOLD)
        sys.exit(1)
    finally:
        # Fermer le fichier si ouvert
        if output_file:
            output_file.close()
            print(f"\n{Colors.GREEN} Résultats sauvegardés dans le fichier{Colors.RESET}")