#!/bin/bash

# Script d'installation pour Recon Report V1.0
# Usage: ./install.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Installation de Recon Report V1.0                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Fonction pour afficher des messages
print_status() {
    echo -e "${CYAN}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Vérifier si Python 3 est installé
print_status "Vérification de Python 3..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION trouvé"
else
    print_error "Python 3 n'est pas installé"
    echo "Installez Python 3 avec : sudo apt install python3 python3-pip"
    exit 1
fi

# Vérifier si pip est installé
print_status "Vérification de pip..."
if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
    print_success "pip trouvé"
else
    print_error "pip n'est pas installé"
    echo "Installez pip avec : sudo apt install python3-pip"
    exit 1
fi

# Installer les dépendances Python
print_status "Installation des dépendances Python..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --user
    print_success "Dépendances Python installées"
else
    print_warning "requirements.txt non trouvé, installation manuelle..."
    pip3 install python-nmap nmap3 simple-term-menu --user
fi

# Détection du système d'exploitation
print_status "Détection du système d'exploitation..."
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    print_success "Système détecté : $OS"
else
    print_warning "Impossible de détecter le système d'exploitation"
    OS="Unknown"
fi

# Installation des outils système
print_status "Vérification des outils système requis..."

# Fonction pour vérifier si un outil est installé
check_tool() {
    if command -v $1 &> /dev/null; then
        print_success "$1 est déjà installé"
        return 0
    else
        print_warning "$1 n'est pas installé"
        return 1
    fi
}

# Liste des outils à vérifier
TOOLS_MISSING=()

if ! check_tool nmap; then
    TOOLS_MISSING+=("nmap")
fi

if ! check_tool sslscan; then
    TOOLS_MISSING+=("sslscan")
fi

if ! check_tool whatweb; then
    TOOLS_MISSING+=("whatweb")
fi

if ! check_tool amass; then
    TOOLS_MISSING+=("amass")
fi

# Si des outils manquent, proposer de les installer
if [ ${#TOOLS_MISSING[@]} -gt 0 ]; then
    echo ""
    print_warning "Les outils suivants ne sont pas installés :"
    for tool in "${TOOLS_MISSING[@]}"; do
        echo "  - $tool"
    done
    echo ""
    
    # Vérifier si on est sous Debian/Ubuntu
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]] || [[ "$OS" == *"Kali"* ]]; then
        read -p "Voulez-vous installer ces outils maintenant ? (nécessite sudo) [y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Installation des outils..."
            
            # Mettre à jour les paquets
            sudo apt update
            
            # Installer les outils un par un
            for tool in "${TOOLS_MISSING[@]}"; do
                if [ "$tool" == "amass" ]; then
                    print_status "Installation de amass via snap..."
                    if command -v snap &> /dev/null; then
                        sudo snap install amass
                    else
                        print_warning "snap n'est pas installé, amass doit être installé manuellement"
                        echo "Voir: https://github.com/owasp-amass/amass"
                    fi
                else
                    print_status "Installation de $tool..."
                    sudo apt install -y $tool
                fi
            done
            
            print_success "Outils système installés"
        else
            print_warning "Installation des outils annulée"
            print_warning "Le script fonctionnera en mode dégradé (certains scans seront ignorés)"
        fi
    else
        print_warning "Installation automatique non disponible pour votre système"
        echo "Veuillez installer manuellement :"
        echo "  - nmap"
        echo "  - sslscan" 
        echo "  - whatweb"
        echo "  - amass (optionnel)"
    fi
fi

# Rendre le script principal exécutable
print_status "Configuration des permissions..."
if [ -f "recon_report_fixed.py" ]; then
    chmod +x recon_report_fixed.py
    print_success "Script rendu exécutable"
else
    print_error "recon_report_fixed.py non trouvé"
    exit 1
fi

# Résumé de l'installation
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║               Installation terminée !                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
print_success "Recon Report est prêt à être utilisé !"
echo ""
echo "Usage :"
echo "  ./recon_report_fixed.py <cible>"
echo ""
echo "Exemples :"
echo "  ./recon_report_fixed.py example.com"
echo "  ./recon_report_fixed.py 192.168.1.1"
echo "  ./recon_report_fixed.py 192.168.1.0/24"
echo ""
print_warning "Rappel : N'utilisez cet outil que sur des systèmes autorisés !"
echo ""
