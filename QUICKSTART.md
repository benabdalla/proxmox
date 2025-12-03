# 🚀 Démarrage Rapide - Plateforme PaaS

## ⚡ Installation en 5 minutes

### 1️⃣ Prérequis
- ✅ Proxmox VE 7.0+
- ✅ Python 3.8+
- ✅ Terraform 1.0+

### 2️⃣ Configuration Proxmox

```bash
# Sur votre serveur Proxmox
pveum user add terraform@pve
pveum aclmod / -user terraform@pve -role PVEAdmin
pveum user token add terraform@pve terraform-token --privsep=0
# ⚠️ COPIEZ LE TOKEN AFFICHÉ !
```

### 3️⃣ Configuration de la plateforme

```bash
# Cloner le projet
git clone <votre-repo>
cd platforme

# Configurer l'environnement
cp .env.example .env
nano .env  # Éditer avec vos informations Proxmox
```

**Configuration minimale `.env` :**
```env
PROXMOX_API_URL=https://votre-proxmox:8006/api2/json
PROXMOX_API_TOKEN_ID=terraform@pve!terraform-token
PROXMOX_API_TOKEN_SECRET=votre-token-secret
PROXMOX_NODE=pve
```

### 4️⃣ Démarrage

**Linux / macOS :**
```bash
chmod +x start.sh
./start.sh
```

**Windows :**
```cmd
start.bat
```

### 5️⃣ Accès à l'interface

Ouvrez votre navigateur : **http://localhost:5000** 🎉

---

## 🎯 Premier déploiement

### Via l'interface web

1. Ouvrir http://localhost:5000
2. Sélectionner **Machine Virtuelle**
3. Choisir **Django**
4. URL GitHub : `https://github.com/django/django`
5. Ressources : **2 CPU**, **2048 MB**, **20 GB**
6. Cliquer sur **Déployer** 🚀

### Via l'API (curl)

```bash
curl -X POST http://localhost:5000/api/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "type": "vm",
    "framework": "django",
    "github_url": "https://github.com/your/repo.git",
    "cpu": 2,
    "memory": 2048,
    "disk": 20
  }'
```

---

## 📊 Vérifications

### Statut du système
```bash
curl http://localhost:5000/health
curl http://localhost:5000/api/status
```

### Liste des déploiements
```bash
curl http://localhost:5000/api/deployments
```

### Ressources Proxmox
```bash
curl http://localhost:5000/api/resources
```

---

## 🆘 Problèmes ?

### Erreur de connexion Proxmox
```bash
# Tester la connexion
curl -k https://votre-proxmox:8006/api2/json/version
```

### Port déjà utilisé
```bash
# Changer le port dans .env
FLASK_PORT=5001
```

### Voir les logs
```bash
tail -f logs/app.log
```

---

## 📚 Documentation complète

- [README.md](README.md) - Vue d'ensemble
- [INSTALLATION.md](docs/INSTALLATION.md) - Installation détaillée
- [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) - Guide de déploiement
- [API.md](docs/API.md) - Documentation API
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Architecture
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Dépannage

---

## 🎓 Frameworks supportés

| Langage | Frameworks |
|---------|-----------|
| **Python** | Django, Flask, FastAPI |
| **JavaScript** | Node.js, Express, React, Vue.js, Next.js |
| **PHP** | Laravel, Symfony |
| **Java** | Spring Boot |

---

## 💡 Exemples rapides

### Déployer une app Django
```bash
curl -X POST http://localhost:5000/api/deploy \
  -H "Content-Type: application/json" \
  -d '{"type":"vm","framework":"django","github_url":"https://github.com/django/django.git","cpu":2,"memory":2048,"disk":20}'
```

### Déployer une app React
```bash
curl -X POST http://localhost:5000/api/deploy \
  -H "Content-Type: application/json" \
  -d '{"type":"lxc","framework":"react","github_url":"https://github.com/facebook/create-react-app.git","cpu":1,"memory":1024,"disk":10}'
```

### Déployer une app Laravel
```bash
curl -X POST http://localhost:5000/api/deploy \
  -H "Content-Type: application/json" \
  -d '{"type":"vm","framework":"laravel","github_url":"https://github.com/laravel/laravel.git","cpu":2,"memory":3072,"disk":30}'
```

---

## 🔒 Sécurité

- ✅ Token API Proxmox
- ✅ Validation des URLs GitHub
- ✅ Limites de ressources
- ✅ Isolation des VMs
- ✅ Firewall UFW

---

## 📈 Monitoring

### Via l'interface web
- Dashboard avec statistiques
- Liste des déploiements en temps réel
- Visualisation des ressources Proxmox

### Via l'API
```bash
# Statut global
curl http://localhost:5000/api/status | jq

# Ressources
curl http://localhost:5000/api/resources | jq
```

---

## 🤝 Support

En cas de problème :
1. Consulter [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. Vérifier les logs : `logs/app.log`
3. Tester la connexion Proxmox
4. Ouvrir une issue sur GitHub

---

## 🎉 C'est parti !

Votre plateforme PaaS est maintenant prête à déployer des applications automatiquement ! 🚀

**Astuce :** Commencez avec un conteneur LXC pour des déploiements plus rapides (2-3 min vs 5-10 min pour une VM).
