# Recon Report V1.0

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)

![Python](https://img.shields.io/badge/python-3.6+-green.svg)

![License](https://img.shields.io/badge/license-GPL-orange.svg)

**Recon Report** est un outil de reconnaissance réseau qui combine plusieurs outils de scan (nmap, sslscan, whatweb, amassn nikto) dans une interface unifiée avec des barres de progression élégantes et des options d'export.

## Fonctionnalités

- **Scan de ports** avec détection de services et versions
- **Scan SSL/TLS** automatique sur les ports 443 et 8443
- **Analyse web** avec WhatWeb
- **Énumération de sous-domaines** avec Amass
- **Barres de progression** style pip (sobre et fluide)
- **Export vers fichier** avec horodatage
- **Interface colorée** pour une meilleure lisibilité

## Installation

### 1. Cloner ou télécharger le projet

```bash
# Placer le script dans un répertoire de votre choix
cd /chemin/vers/votre/dossier
```

### 2. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

Ou manuellement :

```bash
pip install python-nmap nmap3 simple-term-menu
```

### 3. Installer les outils système requis

#### Debian/Ubuntu/Kali Linux

```bash
sudo apt update
sudo apt install nmap sslscan whatweb
```

#### Installation d'Amass (optionnel)

```bash
# Méthode 1 : Via APT (si disponible)
sudo apt install amass

# Méthode 2 : Via Snap
sudo snap install amass

# Méthode 3 : Depuis les sources
# Voir : https://github.com/owasp-amass/amass
```

#### macOS

```bash
brew install nmap
brew install sslscan
# whatweb et amass disponibles via d'autres méthodes
```

### 4. Rendre le script exécutable

```bash
chmod +x recon_report_fixed.py
```

## Utilisation

### Syntaxe de base

```bash
./recon_report_fixed.py <cible>
```

ou

```bash
python3 recon_report_fixed.py <cible>
```

### Exemples

#### Scan d'un domaine

```bash
./recon_report_fixed.py example.com
```

#### Scan d'une adresse IP

```bash
./recon_report_fixed.py 192.168.1.1
```

#### Scan d'un réseau

```bash
./recon_report_fixed.py 192.168.1.0/24
```

### Options du menu

Lors de l'exécution, un menu interactif vous propose deux options :

1. **Afficher la sortie dans le terminal**
  
  - Tous les résultats s'affichent directement dans la console
  - Idéal pour les scans rapides ou les tests
2. **Exporter les résultats dans un fichier**
  
  - Crée un fichier `<cible>_YYYYMMDD_HHMM.txt`
  - Les barres de progression restent visibles dans la console
  - Les résultats détaillés sont sauvegardés dans le fichier

## Exemple de sortie

```
 ______                            ______                                
(_____ \                          (_____ \                           _   
 _____) )_____  ____ ___  ____     _____) )_____ ____   ___   ____ _| |_ 
|  __  /| ___ |/ ___) _ \|  _ \   |  __  /| ___ |  _ \ / _ \ / ___|_   _)
| |  \ \| ____( (__| |_| | | | |  | |  \ \| ____| |_| | |_| | |     | |_ 
|_|   |_|_____)\____)___/|_| |_|  |_|   |_|_____)  __/ \___/|_|      \__)
                                                |_|                      
Recon Report V1.0
Coded by David LE MEUR

=== MENU ===
> Afficher la sortie dans le terminal
  Exporter les résultats dans un fichier

✓ Vous avez choisi d'Afficher la sortie dans le terminal

🔍 Démarrage du scan de example.com...

[*] Scan Nmap de example.com...
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

[*] Analyse de 2 ports...
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2/2

============================================================
====== IP: 93.184.216.34 ======
============================================================

###*** SCAN DE PORTS ***###

------ PORT 80 ------
STATUT : open
SERVICE : http
TYPE : Apache httpd
VERSION : 2.4.41

------ PORT 443 ------
STATUT : open
SERVICE : https
TYPE : Apache httpd
VERSION : 2.4.41

[*] Scan SSL 93.184.216.34:443...
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

[Résultats SSL détaillés...]

[*] Scan WhatWeb...
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%

[Résultats WhatWeb...]

============================================================
✓ Scan terminé avec succès!
============================================================
```

## Structure du projet

```
recon-report/
├── recon_report_fixed.py    # Script principal
├── requirements.txt          # Dépendances Python
└── README.md                 # Ce fichier
```

## Configuration

### Personnalisation des couleurs

Vous pouvez modifier les couleurs dans la classe `Colors` :

```python
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
```

### Modification des outils de scan

Pour ajouter ou retirer des outils, modifiez les fonctions correspondantes :

- `scan_port()` - Scan nmap de base
- `scan_ssl()` - Scan SSL/TLS
- `scan_whatweb()` - Analyse web
- `scan_amass_domain()` - Énumération DNS

## Dépannage

### Erreur : "command not found"

- Vérifiez que l'outil est installé : `which nmap sslscan whatweb amass`
- Installez les outils manquants (voir section Installation)

### Erreur : "ModuleNotFoundError"

```bash
pip install -r requirements.txt
```

### Erreur : "Permission denied"

```bash
chmod +x recon_report_fixed.py
```

### Les barres de progression ne s'affichent pas correctement

- Assurez-vous d'utiliser un terminal compatible (bash, zsh, etc.)
- Évitez les redirections de sortie lors de l'utilisation en mode terminal

## Notes importantes

### Permissions

Certains scans peuvent nécessiter des privilèges root :

```bash
sudo ./recon_report_fixed.py <cible>
```

### Légalité

**AVERTISSEMENT** : N'utilisez cet outil que sur des systèmes dont vous êtes propriétaire ou pour lesquels vous avez une autorisation écrite explicite. L'utilisation non autorisée peut être illégale dans votre juridiction.

### Performance

- Les scans peuvent prendre du temps selon la cible
- La progression est simulée pour les outils sans support natif
- Les barres de progression sont fluides mais approximatives

## Améliorations futures

- [ ] Support de multiples cibles
- [ ] Options en ligne de commande (--output, --no-ssl, etc.)
- [ ] Export en JSON/XML
- [ ] Rapport HTML avec graphiques
- [ ] Scan parallèle pour accélérer
- [ ] Configuration via fichier

## Licence

Ce projet est sous licence GPL. Voir le fichier LICENSE pour plus de détails.

## Auteur

**DavidLM-ux**

- GitHub: [@DavidLM-ux](https://github.com/DavidLM-ux)

## Support

Pour toute question ou problème :

- Ouvrir une [issue](https://github.com/DavidLM-ux/ReconReport/issues)
- Contact : [lemeur.david@proton.me](mailto:lemeur.david@proton.me)

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

- Signaler des bugs
- Proposer des améliorations
- Ajouter de nouvelles fonctionnalités

## Ressources

- [Nmap Documentation](https://nmap.org/book/man.html)
- [SSLScan](https://github.com/rbsec/sslscan)
- [WhatWeb](https://github.com/urbanadventurer/WhatWeb)
- [Amass](https://github.com/owasp-amass/amass)

---

**Version:** 1.0  
**Date:** Janvier 2026
