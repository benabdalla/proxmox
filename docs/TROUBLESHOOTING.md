# Dépannage - Plateforme PaaS

## Problèmes courants et solutions

### 1. Erreur de connexion à Proxmox

#### Symptôme
```
❌ Erreur de connexion à Proxmox
```

#### Solutions

**A. Vérifier l'URL de l'API**
```bash
# Tester la connexion
curl -k https://votre-proxmox:8006/api2/json/version
```

**B. Vérifier le token API**
```bash
# Format correct
PROXMOX_API_TOKEN_ID=terraform@pve!terraform-token
PROXMOX_API_TOKEN_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**C. Vérifier les permissions**
```bash
# Sur le serveur Proxmox
pveum user list
pveum user token list terraform@pve
```

**D. Problème de certificat SSL**
Dans `proxmox_service.py`, vérifier:
```python
verify_ssl=False  # Pour développement uniquement
```

---

### 2. Terraform init échoue

#### Symptôme
```
Error: Failed to install provider
```

#### Solutions

**A. Réinitialiser Terraform**
```bash
cd terraform/workspaces/deployment-X
rm -rf .terraform .terraform.lock.hcl
terraform init
```

**B. Vérifier la connexion internet**
```bash
ping registry.terraform.io
```

**C. Utiliser un mirror Terraform**
Créer `~/.terraformrc`:
```hcl
provider_installation {
  network_mirror {
    url = "https://terraform-mirror.example.com/"
  }
}
```

---

### 3. Déploiement reste en "pending"

#### Symptôme
Le déploiement ne progresse pas

#### Solutions

**A. Vérifier les logs**
```bash
tail -f logs/app.log
```

**B. Vérifier les processus**
```bash
ps aux | grep python
```

**C. Redémarrer l'application**
```bash
# Linux
./start.sh

# Windows
start.bat
```

---

### 4. VM ne démarre pas

#### Symptôme
```
Timeout en attendant que la VM soit prête
```

#### Solutions

**A. Vérifier le template Proxmox**
```bash
# Sur Proxmox
qm list | grep template
```

**B. Vérifier le cloud-init**
```bash
qm cloudinit dump <vmid> user
```

**C. Augmenter le timeout**
Dans `.env`:
```
VM_START_TIMEOUT=600
```

---

### 5. Erreur "Framework non supporté"

#### Symptôme
```
Framework non supporté: xxx
```

#### Solutions

**A. Vérifier la liste des frameworks**
```bash
curl http://localhost:5000/api/frameworks
```

**B. Utiliser le bon nom**
Frameworks valides:
- django, flask, fastapi
- nodejs, express, react, vue, nextjs
- laravel, symfony
- springboot

---

### 6. Problème de mémoire insuffisante

#### Symptôme
```
Cannot allocate memory
```

#### Solutions

**A. Vérifier les ressources Proxmox**
```bash
curl http://localhost:5000/api/resources
```

**B. Réduire les ressources demandées**
```json
{
  "cpu": 1,
  "memory": 1024,
  "disk": 10
}
```

---

### 7. Port déjà utilisé

#### Symptôme
```
Address already in use: 5000
```

#### Solutions

**A. Trouver le processus**
```bash
# Linux
lsof -i :5000

# Windows
netstat -ano | findstr :5000
```

**B. Tuer le processus**
```bash
# Linux
kill -9 <PID>

# Windows
taskkill /PID <PID> /F
```

**C. Changer le port**
Dans `.env`:
```
FLASK_PORT=5001
```

---

### 8. Erreur Git clone

#### Symptôme
```
fatal: could not read Username
```

#### Solutions

**A. Vérifier l'URL**
```bash
# Format correct
https://github.com/user/repo.git
```

**B. Utiliser un dépôt public**
Les dépôts privés nécessitent une authentification

**C. Configurer SSH (futur)**

---

### 9. Base de données corrompue

#### Symptôme
```
database disk image is malformed
```

#### Solutions

**A. Sauvegarder et recréer**
```bash
# Sauvegarder
cp data/deployments.db data/deployments.db.backup

# Supprimer
rm data/deployments.db

# Redémarrer l'application (recrée la DB)
./start.sh
```

---

### 10. Scripts de déploiement échouent

#### Symptôme
Installation/déploiement échoue

#### Solutions

**A. Vérifier les logs de déploiement**
```bash
curl http://localhost:5000/api/deployments/1/logs
```

**B. Tester le script manuellement**
```bash
# Se connecter à la VM
ssh root@<vm-ip>

# Exécuter le script
bash /tmp/install_framework.sh django
```

**C. Vérifier les dépendances système**
```bash
# Sur la VM
apt-get update
apt-get install -y curl wget git
```

---

## Commandes de diagnostic

### Vérifier l'état du système
```bash
# Statut API
curl http://localhost:5000/health

# Statut Proxmox
curl http://localhost:5000/api/status

# Ressources
curl http://localhost:5000/api/resources
```

### Logs détaillés
```bash
# Logs Flask
tail -f logs/app.log

# Logs d'un déploiement
cat logs/deployment-1.log

# Logs système
journalctl -u paas-platform -f
```

### Tests Proxmox
```bash
# Lister les VMs
curl -k -H "Authorization: PVEAPIToken=USER!TOKEN=SECRET" \
  https://proxmox:8006/api2/json/nodes/pve/qemu

# Statut d'une VM
curl -k -H "Authorization: PVEAPIToken=USER!TOKEN=SECRET" \
  https://proxmox:8006/api2/json/nodes/pve/qemu/100/status/current
```

---

## Réinitialisation complète

Si tout échoue, réinitialisation complète:

```bash
# Arrêter l'application
pkill -f "python app.py"

# Nettoyer les données
rm -rf data/*.db
rm -rf logs/*.log
rm -rf terraform/workspaces/*
rm -rf terraform/states/*

# Supprimer l'environnement virtuel
rm -rf backend/venv

# Réinstaller
./start.sh
```

---

## Support et aide

### Logs utiles
Toujours inclure ces informations lors d'une demande d'aide:
1. Version Python: `python --version`
2. Version Terraform: `terraform --version`
3. Logs: `logs/app.log`
4. Configuration (sans secrets): `.env`
5. État du déploiement: API `/deployments/{id}`

### Informations Proxmox
```bash
# Version Proxmox
pveversion -v

# État des nœuds
pvesh get /nodes

# Ressources disponibles
pvesh get /nodes/pve/status
```
