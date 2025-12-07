# 🚨 Solutions Rapides aux Erreurs de Déploiement

## Erreurs Rencontrées

Vous avez rencontré ces deux erreurs :

### ❌ Erreur 1 : Template Proxmox Manquant
```
Template 'ubuntu-22.04-template' not found
```

### ❌ Erreur 2 : Problème de Connectivité Terraform
```
Network connectivity issue reaching Terraform registry
```

---

## 🎯 Solutions Disponibles

### Option 1 : Script Automatique (Recommandé) ✨

#### Windows
```powershell
.\check-proxmox-templates.ps1
```

#### Linux/Mac
```bash
chmod +x check-proxmox-templates.sh
./check-proxmox-templates.sh
```

Ces scripts vont :
- ✅ Vérifier votre configuration `.env`
- ✅ Vous guider pour créer le template
- ✅ Tester la connectivité réseau
- ✅ Générer un script pour créer le template automatiquement

---

### Option 2 : Création Manuelle Rapide (5 minutes)

#### Sur votre serveur Proxmox (via SSH) :

```bash
# Se connecter à Proxmox
ssh root@votre-proxmox-server

# Télécharger l'image Ubuntu 22.04
cd /var/lib/vz/template/iso
wget https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img

# Créer le template (ID 9000)
qm create 9000 --name ubuntu-22.04-template --memory 2048 --cores 2 --net0 virtio,bridge=vmbr0
qm importdisk 9000 jammy-server-cloudimg-amd64.img local-lvm
qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9000-disk-0
qm set 9000 --ide2 local-lvm:cloudinit --boot c --bootdisk scsi0
qm set 9000 --serial0 socket --vga serial0
qm template 9000

# Vérifier
qm list | grep template
```

#### Sur votre machine de développement :

```bash
# Éditer .env
echo "TEMPLATE_NAME=9000" >> .env

# OU si vous préférez utiliser le nom
echo "TEMPLATE_NAME=ubuntu-22.04-template" >> .env

# Redémarrer l'application
./start.sh  # Linux/Mac
start.bat   # Windows
```

---

### Option 3 : Utiliser un Template Existant

Si vous avez déjà un template Ubuntu sur Proxmox :

```bash
# 1. Lister les templates disponibles (sur Proxmox)
ssh root@proxmox "qm list"

# 2. Noter l'ID ou le nom du template

# 3. Mettre à jour .env
echo "TEMPLATE_NAME=<votre-id-ou-nom>" >> .env
```

---

## 🌐 Résoudre le Problème Terraform

### Solution 1 : Vérifier la Connectivité

```bash
# Tester l'accès aux serveurs Terraform
ping registry.terraform.io
ping releases.hashicorp.com
ping github.com
```

### Solution 2 : Configurer un Proxy (si nécessaire)

#### Windows PowerShell
```powershell
$env:HTTP_PROXY="http://proxy.example.com:8080"
$env:HTTPS_PROXY="http://proxy.example.com:8080"
.\start.bat
```

#### Linux/Mac Bash
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
./start.sh
```

### Solution 3 : Nettoyer et Réessayer

```bash
# Nettoyer les workspaces Terraform
rm -rf terraform/workspaces/*
rm -rf terraform/states/*

# Nettoyer le cache Terraform (optionnel)
rm -rf ~/.terraform.d/plugin-cache

# Redémarrer
./start.sh
```

---

## 📋 Checklist de Vérification

Avant de redémarrer l'application :

- [ ] **Template Proxmox créé** (VM ID ou nom noté)
- [ ] **Variable TEMPLATE_NAME configurée** dans `.env`
- [ ] **Connectivité Internet vérifiée** (registry.terraform.io accessible)
- [ ] **Fichier .env configuré** avec les bonnes informations Proxmox
- [ ] **Workspaces Terraform nettoyés** (si redémarrage)

---

## 🚀 Test Rapide

Après avoir configuré :

```bash
# 1. Vérifier la configuration
cat .env | grep TEMPLATE

# 2. Démarrer l'application
./start.sh  # ou start.bat

# 3. Tester un déploiement simple
curl -X POST http://localhost:5000/api/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "type": "vm",
    "framework": "flask",
    "github_url": "https://github.com/pallets/flask.git",
    "cpu": 1,
    "memory": 1024,
    "disk": 10
  }'

# 4. Vérifier les logs
tail -f logs/app.log
```

---

## 📚 Documentation Complète

- **QUICK_FIX.md** : Guide détaillé avec toutes les solutions
- **docs/INSTALLATION.md** : Guide d'installation complet
- **docs/TROUBLESHOOTING.md** : Guide de dépannage exhaustif
- **README.md** : Vue d'ensemble du projet

---

## 💡 Besoin d'Aide ?

1. **Vérifier les logs** : `tail -f logs/app.log`
2. **Exécuter le script de vérification** : `./check-proxmox-templates.sh`
3. **Consulter QUICK_FIX.md** pour plus de détails

---

**Dernière mise à jour :** 7 Décembre 2025
