# 🔧 GUIDE DE CONFIGURATION PROXMOX - ÉTAPE PAR ÉTAPE

## ⚠️ PROBLÈME ACTUEL

```
❌ Impossible de récupérer les ressources Proxmox
❌ Vérifiez votre connexion à Proxmox
```

**Cause:** Le fichier `.env` contient des valeurs par défaut qui ne correspondent pas à votre serveur Proxmox.

---

## 🎯 SOLUTION EN 4 ÉTAPES

### **Étape 1 : Obtenir l'Adresse IP de Proxmox**

#### Option A : Via l'interface web Proxmox
Si vous pouvez accéder à Proxmox via un navigateur, notez l'URL :
```
Exemple : https://192.168.1.50:8006
          https://10.0.0.100:8006
```

#### Option B : Via la console du serveur
Sur le serveur Proxmox directement :
```bash
# Afficher l'adresse IP
ip addr show | grep inet
# ou
hostname -I
```

---

### **Étape 2 : Créer un Token API sur Proxmox**

1. **Connectez-vous à l'interface web Proxmox**
   - Ouvrez https://VOTRE-IP-PROXMOX:8006
   - Connectez-vous avec vos identifiants root

2. **Créer un utilisateur pour Terraform**
   ```
   Datacenter → Permissions → Users → Add
   
   Username: terraform@pve
   Realm: Proxmox VE authentication server
   Password: (choisissez un mot de passe)
   ```

3. **Donner les permissions à l'utilisateur**
   ```
   Datacenter → Permissions → Add → User Permission
   
   Path: /
   User: terraform@pve
   Role: Administrator (ou PVEAdmin)
   ```

4. **Créer un Token API**
   ```
   Datacenter → Permissions → API Tokens → Add
   
   User: terraform@pve
   Token ID: terraform-token
   Privilege Separation: NON COCHÉ ❌
   
   → Cliquez sur "Add"
   → COPIEZ le Secret affiché (vous ne le reverrez plus!)
   ```

   Vous obtiendrez quelque chose comme :
   ```
   Token ID: terraform@pve!terraform-token
   Secret: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ```

---

### **Étape 3 : Lister les Templates Existants (si vous en avez)**

#### Via SSH sur Proxmox :
```bash
ssh root@VOTRE-IP-PROXMOX
qm list
```

Cherchez les VMs marquées comme template (avec un * ou "template" dans le nom).
Notez l'ID (ex: 100, 9000, etc.)

#### Via l'interface web :
```
Server View → VM → Chercher les icônes de template
Noter le VMID (ex: 100, 9000)
```

---

### **Étape 4 : Configurer le fichier .env**

Maintenant, éditez le fichier `.env` avec VOS vraies valeurs :

```powershell
# Ouvrir .env dans l'éditeur
notepad "c:\mootezdiskD\Formation Test\platforme\.env"
```

**REMPLACEZ les lignes suivantes :**

```properties
# AVANT (valeurs par défaut)
PROXMOX_API_URL=https://proxmox-server.local:8006/api2/json
PROXMOX_API_TOKEN_ID=terraform@pve!terraform-token
PROXMOX_API_TOKEN_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
PROXMOX_NODE=pve
TEMPLATE_NAME=ubuntu-22.04-template

# APRÈS (vos vraies valeurs)
PROXMOX_API_URL=https://192.168.1.50:8006/api2/json  # ← Votre IP Proxmox
PROXMOX_API_TOKEN_ID=terraform@pve!terraform-token   # ← Votre Token ID
PROXMOX_API_TOKEN_SECRET=abc12345-6789-...           # ← Votre Secret
PROXMOX_NODE=pve                                     # ← Nom de votre nœud
TEMPLATE_NAME=9000                                   # ← ID de votre template (ou créer)
```

---

## 📝 EXEMPLE CONCRET

Voici un exemple avec des valeurs réalistes :

```properties
# Configuration Proxmox
PROXMOX_API_URL=https://192.168.1.50:8006/api2/json
PROXMOX_API_TOKEN_ID=terraform@pve!terraform-token
PROXMOX_API_TOKEN_SECRET=a1b2c3d4-e5f6-7890-abcd-ef1234567890
PROXMOX_NODE=pve
PROXMOX_STORAGE=local-lvm
PROXMOX_ISO_STORAGE=local
PROXMOX_BRIDGE=vmbr0

# Templates Proxmox
TEMPLATE_NAME=9000  # ← Si vous avez créé le template avec ID 9000
# ou
# TEMPLATE_NAME=100  # ← Si vous utilisez un template existant avec ID 100

# Le reste peut rester inchangé
FLASK_SECRET_KEY=change-this-to-a-random-secret-key
FLASK_ENV=production
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

---

## ✅ VÉRIFICATION DE LA CONFIGURATION

Après avoir configuré `.env`, testez la connexion :

```powershell
# Test 1 : Ping du serveur Proxmox
ping VOTRE-IP-PROXMOX

# Test 2 : Accès HTTPS
curl -k https://VOTRE-IP-PROXMOX:8006

# Test 3 : Test de l'API (remplacez avec vos vraies valeurs)
$token = "terraform@pve!terraform-token"
$secret = "votre-secret-ici"
$url = "https://192.168.1.50:8006/api2/json/version"

$headers = @{
    "Authorization" = "PVEAPIToken=${token}=${secret}"
}

Invoke-RestMethod -Uri $url -Headers $headers -SkipCertificateCheck
```

Si le Test 3 fonctionne, vous devriez voir la version de Proxmox s'afficher !

---

## 🚀 SI VOUS N'AVEZ PAS DE TEMPLATE

Si vous n'avez aucun template sur Proxmox, créez-en un :

### **Option 1 : Création Rapide via Script**

```powershell
# Générer un script pour créer le template
.\check-proxmox-templates.ps1
```

### **Option 2 : Création Manuelle**

**Sur le serveur Proxmox (via SSH) :**

```bash
ssh root@VOTRE-IP-PROXMOX

# Télécharger Ubuntu 22.04 Cloud Image
cd /var/lib/vz/template/iso
wget https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img

# Créer le template VM avec ID 9000
qm create 9000 \
  --name ubuntu-22.04-template \
  --memory 2048 \
  --cores 2 \
  --net0 virtio,bridge=vmbr0

# Importer le disque
qm importdisk 9000 jammy-server-cloudimg-amd64.img local-lvm

# Configurer la VM
qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9000-disk-0
qm set 9000 --ide2 local-lvm:cloudinit
qm set 9000 --boot c --bootdisk scsi0
qm set 9000 --serial0 socket --vga serial0
qm set 9000 --agent enabled=1

# Convertir en template
qm template 9000

# Vérifier
qm list | grep template
```

**Ensuite, dans votre `.env` :**
```properties
TEMPLATE_NAME=9000
```

---

## 📋 CHECKLIST FINALE

Avant de redémarrer l'application, vérifiez :

- [ ] **Fichier .env créé** (✅ déjà fait)
- [ ] **PROXMOX_API_URL** configuré avec votre vraie IP
- [ ] **PROXMOX_API_TOKEN_ID** configuré (créé sur Proxmox)
- [ ] **PROXMOX_API_TOKEN_SECRET** configuré (copié depuis Proxmox)
- [ ] **PROXMOX_NODE** vérifié (généralement "pve")
- [ ] **TEMPLATE_NAME** configuré avec un ID valide ou créé
- [ ] **Test de connexion** réussi (curl ou Invoke-RestMethod)

---

## 🔄 REDÉMARRAGE DE L'APPLICATION

Une fois tout configuré :

```powershell
# 1. Arrêter l'application actuelle (Ctrl+C)

# 2. Nettoyer les anciens workspaces
Remove-Item -Recurse -Force terraform\workspaces\* -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force terraform\states\* -ErrorAction SilentlyContinue

# 3. Redémarrer
.\start.bat
```

---

## 🆘 AIDE RAPIDE

### Problème : "Je ne connais pas l'IP de mon Proxmox"
**Solution :** 
- Regardez dans votre navigateur si vous y accédez déjà
- Connectez-vous au serveur et tapez `hostname -I`
- Vérifiez votre routeur/DHCP pour voir les machines connectées

### Problème : "Je n'arrive pas à créer le token API"
**Solution :**
- Assurez-vous d'être connecté en tant que `root@pam`
- Décochez "Privilege Separation" lors de la création du token
- Vérifiez que l'utilisateur terraform@pve a les bonnes permissions

### Problème : "Je n'ai pas SSH sur Proxmox"
**Solution :**
- Utilisez la console web de Proxmox (bouton "Shell" dans l'interface)
- Ou créez le template via l'interface web (plus long mais possible)

---

## 📞 COMMANDES DE DIAGNOSTIC

```powershell
# Afficher la config Proxmox actuelle
Get-Content .env | Select-String "PROXMOX"

# Tester la résolution DNS
nslookup proxmox-server.local  # Si vous utilisez un nom

# Tester le port 8006
Test-NetConnection -ComputerName VOTRE-IP -Port 8006

# Vérifier le contenu de .env
Get-Content .env
```

---

## ✨ RÉSUMÉ VISUEL

```
┌─────────────────────────────────────────┐
│ 1. Trouver IP Proxmox                   │
│    → https://192.168.1.50:8006          │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 2. Créer Token API                      │
│    → terraform@pve!terraform-token      │
│    → abc123-456-789-...                 │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 3. Configurer .env                      │
│    → Remplacer valeurs par défaut       │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 4. Créer ou Identifier Template         │
│    → TEMPLATE_NAME=9000                 │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│ 5. Redémarrer Application               │
│    → .\start.bat                        │
└─────────────────────────────────────────┘
```

---

**Temps estimé : 10-15 minutes**  
**Difficulté : ⭐⭐ Moyen**

**Dernière mise à jour : 7 Décembre 2025**
