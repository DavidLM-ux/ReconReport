#!/bin/bash

##################################################################################
# reconReport                                                                    #
# Utilisation: Script d'automatisation de l'étape de reconnaissance d'un pentest #
# Usage: ./reconReport <target> OU ./reconReport -i (Mode interactif)            #
# Auteur: David LM <lemeurdav@gmail.com>                                         #
# Version: V0.2                                                                  #
# Licence: GPL                                                                   #
##################################################################################

# Activation du mode strict
set -euo pipefail

# Couleurs pour l'affichage
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

function banner() {
    clear
    cat <<\EOF
(_____ \\                           (_____ \\                              _   
 _____) )  _____  ____ ___   ____    _____) )  _____ ____   ___     ____ _| |_ 
|  __  /  | ___ |/ ___) _ \\|  _ \\ |  __  /  | ___ |  _ \\/  _ \\ / ___|_   _)
| |  \\ \ | ____( (__| |_| || | | | | |  \\ \ | ____| |_| || |_| || |    || |_
|_|   \\_\|_____)\\____)___/|_| |_| |_|   \\_\|_____)  __/ \\___/ |_|     \\__)
                                                    |_|

EOF
}

function usage() {
    cat <<EOF

Recon Report V0.2

Usage : $0 [option] <target> OU $0 -i (Mode interactif)

Options :
  -h, --help             Afficher cette page d'aide
  -f, --file             Exporter la sortie dans un fichier au format Hote_date_heure.txt
  -t, --terminal         Afficher la sortie dans le terminal
  -i, --interactif       Exécution du script en mode interactif

Exemples:
  $0 -f 8.8.8.8
  $0 -t example.com
  $0 -i

EOF
    exit 0
}

function log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

function log_error() {
    echo -e "${RED}[ERREUR]${NC} $1" >&2
}

function log_warning() {
    echo -e "${YELLOW}[ATTENTION]${NC} $1"
}

function check_dependance() {
    local missing_deps=()
    local missing_snap_deps=()
    
    # Vérification silencieuse des dépendances
    command -v sslscan &>/dev/null || missing_deps+=("sslscan")
    command -v whatweb &>/dev/null || missing_deps+=("whatweb")
    command -v nikto &>/dev/null || missing_deps+=("nikto")
    command -v nmap &>/dev/null || missing_deps+=("nmap")
    command -v amass &>/dev/null || missing_snap_deps+=("amass")
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_warning "Dépendances APT manquantes : ${missing_deps[*]}"
        read -p "Voulez-vous les installer maintenant ? (o/N) : " install_choice
        if [[ "$install_choice" =~ ^[oO]$ ]]; then
            log_info "Installation des dépendances..."
            sudo apt update && sudo apt install -y "${missing_deps[@]}"
        else
            log_error "Installation annulée. Le script nécessite ces dépendances."
            exit 1
        fi
    else
        log_info "Toutes les dépendances APT sont installées"
    fi
    
    if [ ${#missing_snap_deps[@]} -gt 0 ]; then
        log_warning "Dépendances SNAP manquantes : ${missing_snap_deps[*]}"
        read -p "Voulez-vous les installer maintenant ? (o/N) : " install_choice
        if [[ "$install_choice" =~ ^[oO]$ ]]; then
            log_info "Installation des dépendances snap..."
            sudo snap install amass
        else
            log_error "Installation annulée. Le script nécessite amass."
            exit 1
        fi
    else
        log_info "Toutes les dépendances SNAP sont installées"
    fi
}

function validate_target() {
    local target="$1"
    
    # Validation basique de l'hôte (IP ou nom de domaine)
    if [[ ! "$target" =~ ^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$ ]] && \
       [[ ! "$target" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        log_error "Cible invalide : $target"
        return 1
    fi
    return 0
}

function scanreport() {
    local target="$1"
    local no_color="${2:-}"
    
    # Validation de la cible
    if ! validate_target "$target"; then
        return 1
    fi
    
    log_info "Démarrage du scan de : $target"
    
    # Scan du port 443
    log_info "Vérification du port SSL (443)..."
    local nmap_result
    nmap_result=$(nmap -p 443 -T3 "$target" 2>/dev/null | grep "443/tcp" | awk '{print $2}')
    
    # Options pour désactiver les couleurs si nécessaire
    local sslscan_opts=""
    local whatweb_opts=""
    
    if [ -n "$no_color" ]; then
        sslscan_opts="--no-colour"
        whatweb_opts="--color=never"
    fi
    
    # SSLSCAN (si port 443 ouvert)
    if [ "$nmap_result" == "open" ]; then
        echo -e "\n### SSLSCAN ###\n"
        sslscan $sslscan_opts "$target" 2>/dev/null || log_warning "Échec de sslscan"
    else
        log_info "Service SSL absent sur cette cible (port 443 fermé/filtré)"
    fi
    
    # WHATWEB
    echo -e "\n### WHATWEB ###\n"
    whatweb $whatweb_opts "$target" 2>/dev/null || log_warning "Échec de whatweb"
    
    # AMASS
    echo -e "\n### AMASS ###\n"
    amass enum -d "$target" -max-depth 2 -timeout 1 2>/dev/null || log_warning "Échec de amass"
    
    # NIKTO
    echo -e "\n### NIKTO ###\n"
    nikto -h "$target" 2>/dev/null || log_warning "Échec de nikto"
    
    log_info "Scan terminé pour : $target"
}

function interactif() {
    local target
    local option
    
    echo ""
    read -p "Entrez l'hôte cible : " target
    
    # Validation de la cible
    if ! validate_target "$target"; then
        log_error "Cible invalide"
        exit 1
    fi
    
    echo -e "\nOptions disponibles :"
    echo "1 - Afficher le résultat dans le terminal"
    echo "2 - Exporter le résultat dans un fichier"
    echo ""
    read -p "Votre choix : " option
    
    case "$option" in
        1)
            scanreport "$target"
            ;;
        2)
            local output_file="${target}_$(date +%d%m%y-%H%M).txt"
            log_info "Export vers : $output_file"
            scanreport "$target" "no_color" | tee "$output_file"
            log_info "Résultats sauvegardés dans : $output_file"
            ;;
        *)
            log_error "Option non reconnue : $option"
            exit 1
            ;;
    esac
}

# Programme principal
main() {
    # Vérification des dépendances
    check_dependance
    
    # Si aucun argument, afficher l'aide
    if [ $# -eq 0 ]; then
        usage
    fi
    
    # Parse des options
    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help)
                usage
                ;;
            -f|--file)
                if [ -z "${2:-}" ]; then
                    log_error "Option -f requiert une cible"
                    usage
                fi
                banner
                local output_file="${2}_$(date +%d%m%y-%H%M).txt"
                log_info "Export vers : $output_file"
                scanreport "$2" "no_color" | tee "$output_file"
                log_info "Résultats sauvegardés dans : $output_file"
                exit 0
                ;;
            -t|--terminal)
                if [ -z "${2:-}" ]; then
                    log_error "Option -t requiert une cible"
                    usage
                fi
                banner
                scanreport "$2"
                exit 0
                ;;
            -i|--interactif)
                banner
                interactif
                exit 0
                ;;
            *)
                log_error "Option inconnue : $1"
                usage
                ;;
        esac
        shift
    done
}

# Point d'entrée
main "$@"