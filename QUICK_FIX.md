# 🚨 Guide de Résolution Rapide des Erreurs

## ⚠️ Problèmes Détectés

### Erreur 1: Template Proxmox Manquant ❌
```
Template 'ubuntu-22.04-template' not found
```

### Erreur 2: Problème de Connectivité Terraform ❌
```
Network connectivity issue reaching Terraform registry
```

---

## 🔧 Solution 1: Créer le Template Proxmox

### Option A: Créer un Template Ubuntu 22.04 (Recommandé)

#### Étape 1: Se connecter à Proxmox via SSH
```bash
ssh root@votre-proxmox-server
```

#### Étape 2: Télécharger l'image cloud Ubuntu 22.04
```bash
cd /var/lib/vz/template/iso
wget https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img
```

#### Étape 3: Créer une VM template
```bash
# Créer une VM (ID 9000 par exemple)
qm create 9000 --name ubuntu-22.04-template --memory 2048 --cores 2 --net0 virtio,bridge=vmbr0

# Importer le disque
qm importdisk 9000 /var/lib/vz/template/iso/jammy-server-cloudimg-amd64.img local-lvm

# Attacher le disque
qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9000-disk-0

# Ajouter Cloud-Init
qm set 9000 --ide2 local-lvm:cloudinit

# Configurer le boot
qm set 9000 --boot c --bootdisk scsi0

# Ajouter un serial console
qm set 9000 --serial0 socket --vga serial0

# Activer l'agent QEMU
qm set 9000 --agent enabled=1

# Convertir en template
qm template 9000
```

#### Étape 4: Mettre à jour votre fichier `.env`
```bash
# Dans .env, ajouter:
TEMPLATE_NAME=ubuntu-22.04-template
# OU utiliser l'ID:
TEMPLATE_NAME=9000
```

---

### Option B: Utiliser un Template Existant

#### Étape 1: Lister les templates disponibles sur Proxmox
```bash
# Via SSH sur Proxmox
qm list | grep template
```

#### Étape 2: Noter le nom ou l'ID du template

#### Étape 3: Mettre à jour votre `.env`
```bash
# Exemple si vous avez un template avec ID 100
TEMPLATE_NAME=100

# OU avec un nom
TEMPLATE_NAME=mon-template-ubuntu
```

---

### Option C: Créer un Template LXC (Pour conteneurs uniquement)

```bash
# Se connecter à Proxmox
ssh root@votre-proxmox-server

# Télécharger le template Ubuntu 22.04 LXC
pveam update
pveam download local ubuntu-22.04-standard_22.04-1_amd64.tar.zst

# Le template sera disponible dans:
# local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst
```

Puis dans `.env`:
```bash
LXC_TEMPLATE=local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst
```

---

## 🌐 Solution 2: Résoudre le Problème Terraform

### Option A: Configuration Proxy/Réseau

#### Si vous êtes derrière un proxy
```bash
# Dans votre terminal (avant de lancer l'app)
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
export NO_PROXY=localhost,127.0.0.1

# Puis lancer l'application
./start.sh
```

#### Tester la connectivité
```bash
# Tester l'accès au registry Terraform
curl -I https://registry.terraform.io

# Tester l'accès à GitHub (pour les providers)
curl -I https://github.com
```

---

### Option B: Mirror Terraform Local (Solution Avancée)

#### Étape 1: Créer un fichier de configuration Terraform
```bash
# Linux/Mac
mkdir -p ~/.terraform.d
nano ~/.terraform.d/terraform.rc

# Windows
# Créer: %APPDATA%\terraform.rc
```

#### Étape 2: Ajouter la configuration du mirror
```hcl
provider_installation {
  network_mirror {
    url = "https://releases.hashicorp.com/terraform/"
    include = ["registry.terraform.io/*/*"]
  }
  direct {
    exclude = ["registry.terraform.io/*/*"]
  }
}
```

---

### Option C: Téléchargement Manuel du Provider

#### Étape 1: Télécharger le provider Proxmox manuellement
```bash
# Créer le dossier des plugins
mkdir -p ~/.terraform.d/plugins/registry.terraform.io/telmate/proxmox/2.9.14/linux_amd64

# Télécharger le provider
cd ~/.terraform.d/plugins/registry.terraform.io/telmate/proxmox/2.9.14/linux_amd64
wget https://github.com/Telmate/terraform-provider-proxmox/releases/download/v2.9.14/terraform-provider-proxmox_2.9.14_linux_amd64.zip
unzip terraform-provider-proxmox_2.9.14_linux_amd64.zip
chmod +x terraform-provider-proxmox_v2.9.14
```

---

### Option D: Utiliser Terraform en Mode Offline

#### Étape 1: Pré-télécharger les providers
```bash
# Sur une machine avec internet
terraform init
terraform providers mirror ./providers

# Copier le dossier ./providers vers votre serveur
```

#### Étape 2: Configurer Terraform pour utiliser le mirror local
```hcl
provider_installation {
  filesystem_mirror {
    path    = "/path/to/providers"
    include = ["registry.terraform.io/*/*"]
  }
}
```

---

## 🔍 Vérification Rapide

### 1. Vérifier la configuration Proxmox
```bash
# Vérifier que le fichier .env existe
cat .env | grep TEMPLATE_NAME

# Si absent, l'ajouter
echo "TEMPLATE_NAME=ubuntu-22.04-template" >> .env
# OU
echo "TEMPLATE_NAME=9000" >> .env
```

### 2. Vérifier la connectivité réseau
```bash
# Tester registry.terraform.io
ping registry.terraform.io

# Tester releases.hashicorp.com
ping releases.hashicorp.com

# Tester GitHub
ping github.com
```

### 3. Nettoyer et redémarrer
```bash
# Nettoyer les anciens workspaces Terraform
rm -rf terraform/workspaces/*
rm -rf terraform/states/*

# Redémarrer l'application
./start.sh
```

---

## 📋 Checklist Complète

- [ ] **Template Proxmox créé** (VM ID 9000 ou autre)
- [ ] **Variable TEMPLATE_NAME** configurée dans `.env`
- [ ] **Connectivité Internet** vérifiée
- [ ] **Proxy configuré** (si nécessaire)
- [ ] **Provider Terraform** accessible
- [ ] **Permissions Proxmox** correctes
- [ ] **Application redémarrée**

---

## 🚀 Commandes de Test Rapide

```bash
# Test 1: Vérifier les templates Proxmox
ssh root@proxmox "qm list"

# Test 2: Vérifier la configuration
cat .env | grep -E "TEMPLATE|PROXMOX"

# Test 3: Tester Terraform manuellement
cd terraform/workspaces/deployment-18
terraform init -upgrade

# Test 4: Redémarrer et tester un déploiement
./start.sh

# Test 5: Vérifier les logs
tail -f logs/app.log
```

---

## 💡 Solution la Plus Rapide (3 minutes)

### Si vous avez déjà un template sur Proxmox:

```bash
# 1. Lister les templates
ssh root@proxmox "qm list | grep template"

# 2. Noter l'ID (par exemple: 9000)

# 3. Ajouter dans .env
echo "TEMPLATE_NAME=9000" >> .env

# 4. Redémarrer
./start.sh
```

### Si vous n'avez PAS de template:

```bash
# 1. Créer rapidement un template (sur Proxmox via SSH)
wget https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img -O /tmp/ubuntu.img
qm create 9000 --name ubuntu-22.04-template --memory 2048 --cores 2 --net0 virtio,bridge=vmbr0
qm importdisk 9000 /tmp/ubuntu.img local-lvm
qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9000-disk-0
qm set 9000 --ide2 local-lvm:cloudinit --boot c --bootdisk scsi0
qm template 9000

# 2. Configurer .env
echo "TEMPLATE_NAME=9000" >> .env

# 3. Redémarrer
./start.sh
```

---

## 📞 Besoin d'Aide?

Consultez:
- `docs/INSTALLATION.md` - Guide d'installation complet
- `docs/TROUBLESHOOTING.md` - Guide de dépannage détaillé
- `logs/app.log` - Logs de l'application

---

**Dernière mise à jour:** 7 Décembre 2025
