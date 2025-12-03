# Plateforme PaaS - Guide d'Installation et Configuration

## 📋 Prérequis

### Serveur Proxmox
- Proxmox VE 7.0 ou supérieur
- Accès administrateur
- Réseau configuré avec bridge (vmbr0 par défaut)

### Machine de développement
- Python 3.8 ou supérieur
- Terraform 1.0 ou supérieur
- Git

## 🔧 Installation

### 1. Configuration de Proxmox

#### Créer un utilisateur pour Terraform
```bash
# Se connecter au serveur Proxmox via SSH
ssh root@proxmox-server

# Créer l'utilisateur
pveum user add terraform@pve --comment "Utilisateur Terraform"

# Attribuer les permissions
pveum aclmod / -user terraform@pve -role PVEAdmin

# Créer un token API
pveum user token add terraform@pve terraform-token --privsep=0

# IMPORTANT: Copier le token affiché, il ne sera plus visible!
```

#### Préparer un template Ubuntu
```bash
# Télécharger l'image Ubuntu Cloud
wget https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img

# Créer une VM template
qm create 9000 --name ubuntu-22.04-cloudinit --memory 2048 --net0 virtio,bridge=vmbr0
qm importdisk 9000 jammy-server-cloudimg-amd64.img local-lvm
qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9000-disk-0
qm set 9000 --ide2 local-lvm:cloudinit
qm set 9000 --boot c --bootdisk scsi0
qm set 9000 --serial0 socket --vga serial0
qm set 9000 --agent enabled=1
qm template 9000

# Pour les conteneurs LXC, télécharger le template
pveam update
pveam download local ubuntu-22.04-standard_22.04-1_amd64.tar.gz
```

### 2. Configuration de la plateforme

#### Cloner le projet
```bash
git clone <votre-repo>
cd platforme
```

#### Installer les dépendances Python
```bash
cd backend
pip install -r requirements.txt
```

#### Installer Terraform
```bash
# Linux
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Vérifier l'installation
terraform --version
```

#### Configuration des variables d'environnement
```bash
# Copier le fichier exemple
cp .env.example .env

# Éditer avec vos informations
nano .env
```

**Configuration requise dans `.env`:**
```env
# Proxmox - Remplacer avec vos valeurs
PROXMOX_API_URL=https://votre-proxmox:8006/api2/json
PROXMOX_API_TOKEN_ID=terraform@pve!terraform-token
PROXMOX_API_TOKEN_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
PROXMOX_NODE=pve
PROXMOX_STORAGE=local-lvm
PROXMOX_BRIDGE=vmbr0

# Flask - Générer une clé secrète
FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# Réseau - Adapter à votre configuration
NETWORK_POOL_START=192.168.1.100
NETWORK_POOL_END=192.168.1.200
NETWORK_GATEWAY=192.168.1.1
```

### 3. Initialisation

#### Créer les dossiers nécessaires
```bash
mkdir -p data logs terraform/workspaces terraform/states
```

#### Initialiser la base de données
```bash
cd backend
python app.py
# Arrêter avec Ctrl+C après initialisation
```

### 4. Test de connexion

```bash
# Tester la connexion à Proxmox
python << EOF
from services.proxmox_service import ProxmoxService
service = ProxmoxService()
print(service.test_connection())
EOF
```

## 🚀 Lancement

### Mode développement
```bash
cd backend
python app.py
```

### Mode production (avec gunicorn)
```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Avec systemd (recommandé pour production)
```bash
# Créer le service
sudo nano /etc/systemd/system/paas-platform.service
```

```ini
[Unit]
Description=PaaS Platform Service
After=network.target

[Service]
User=votre-utilisateur
WorkingDirectory=/chemin/vers/platforme/backend
Environment="PATH=/chemin/vers/venv/bin"
ExecStart=/chemin/vers/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Activer et démarrer
sudo systemctl daemon-reload
sudo systemctl enable paas-platform
sudo systemctl start paas-platform
sudo systemctl status paas-platform
```

## 🧪 Test de déploiement

### Via l'interface web
1. Ouvrir http://localhost:5000
2. Sélectionner "Machine Virtuelle"
3. Choisir "Django"
4. Entrer: https://github.com/django/django-rest-framework
5. Configurer ressources (2 CPU, 2048 MB, 20 GB)
6. Cliquer "Déployer"

### Via API (curl)
```bash
curl -X POST http://localhost:5000/api/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "type": "vm",
    "framework": "django",
    "github_url": "https://github.com/votreuser/votre-repo.git",
    "cpu": 2,
    "memory": 2048,
    "disk": 20
  }'
```

## 🔍 Dépannage

### Erreur de connexion Proxmox
```bash
# Vérifier les certificats
curl -k https://votre-proxmox:8006/api2/json/version

# Tester le token
curl -k -H "Authorization: PVEAPIToken=terraform@pve!terraform-token=VOTRE-TOKEN" \
  https://votre-proxmox:8006/api2/json/version
```

### Erreur Terraform
```bash
# Réinitialiser Terraform
cd terraform/workspaces/deployment-X
rm -rf .terraform .terraform.lock.hcl
terraform init
```

### Logs de déploiement
```bash
# Logs de l'application
tail -f logs/app.log

# Logs d'un déploiement spécifique
cat logs/deployment-X.log
```

## 📊 Monitoring

### Statut du système
```bash
# Via API
curl http://localhost:5000/api/status

# Ressources Proxmox
curl http://localhost:5000/api/resources
```

### Métriques
- Nombre de déploiements actifs
- Utilisation des ressources Proxmox
- Temps moyen de déploiement

## 🔒 Sécurité

### Recommandations
1. Changer `FLASK_SECRET_KEY` en production
2. Utiliser HTTPS avec certificat SSL
3. Configurer le firewall (UFW)
4. Limiter l'accès à l'API
5. Sauvegarder régulièrement la base de données

### Firewall
```bash
sudo ufw allow 5000/tcp
sudo ufw allow from 192.168.1.0/24 to any port 5000
sudo ufw enable
```

## 📝 Notes

- Les VMs prennent 5-10 minutes à déployer
- Les conteneurs LXC sont plus rapides (2-3 minutes)
- Vérifier l'espace disque disponible sur Proxmox
- Les templates doivent être préparés à l'avance

## 🆘 Support

En cas de problème:
1. Consulter les logs
2. Vérifier la configuration Proxmox
3. Tester la connexion réseau
4. Vérifier les ressources disponibles
