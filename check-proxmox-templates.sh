#!/bin/bash

# Script pour vérifier et configurer les templates Proxmox
# Usage: ./check-proxmox-templates.sh

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}=====================================${NC}"
echo -e "${CYAN}  Vérification Configuration Proxmox${NC}"
echo -e "${CYAN}=====================================${NC}"
echo ""

# Fonction pour lire le fichier .env
get_env_value() {
    local key=$1
    if [ -f ".env" ]; then
        grep "^${key}=" .env | cut -d'=' -f2-
    fi
}

# Vérifier si .env existe
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Fichier .env non trouvé!${NC}"
    echo -e "${YELLOW}Création depuis .env.example...${NC}"
    
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ Fichier .env créé. Veuillez le configurer.${NC}"
    else
        echo -e "${RED}❌ .env.example non trouvé!${NC}"
        exit 1
    fi
fi

# Lire les configurations
PROXMOX_URL=$(get_env_value "PROXMOX_API_URL")
PROXMOX_NODE=$(get_env_value "PROXMOX_NODE")
TEMPLATE_NAME=$(get_env_value "TEMPLATE_NAME")
LXC_TEMPLATE=$(get_env_value "LXC_TEMPLATE")

echo -e "${CYAN}📋 Configuration actuelle:${NC}"
echo -e "   Proxmox URL: ${PROXMOX_URL}"
echo -e "   Proxmox Node: ${PROXMOX_NODE}"
echo -e "   VM Template: ${TEMPLATE_NAME}"
echo -e "   LXC Template: ${LXC_TEMPLATE}"
echo ""

# Vérifier si les variables critiques sont configurées
MISSING_VARS=()

if [ -z "$PROXMOX_URL" ] || [[ "$PROXMOX_URL" == *"proxmox-server.local"* ]]; then
    MISSING_VARS+=("PROXMOX_API_URL")
fi

if [ -z "$TEMPLATE_NAME" ] || [ "$TEMPLATE_NAME" == "ubuntu-22.04-template" ]; then
    echo -e "${YELLOW}⚠️  TEMPLATE_NAME utilise la valeur par défaut${NC}"
    echo -e "${YELLOW}   Assurez-vous qu'un template nommé 'ubuntu-22.04-template' existe sur Proxmox${NC}"
    echo ""
fi

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo -e "${RED}❌ Variables manquantes dans .env:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo -e "${RED}   - $var${NC}"
    done
    echo ""
    echo -e "${YELLOW}📝 Veuillez éditer le fichier .env et configurer ces variables${NC}"
    echo ""
fi

# Générer les commandes pour créer un template sur Proxmox
echo -e "${CYAN}=====================================${NC}"
echo -e "${CYAN}  Commandes pour créer le template${NC}"
echo -e "${CYAN}=====================================${NC}"
echo ""
echo -e "${YELLOW}Si vous n'avez pas encore de template, connectez-vous à Proxmox via SSH et exécutez:${NC}"
echo ""

cat << 'EOF'
# 1. Télécharger l'image Ubuntu 22.04 Cloud
cd /var/lib/vz/template/iso
wget https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img

# 2. Créer une VM template (ID 9000)
qm create 9000 --name ubuntu-22.04-template --memory 2048 --cores 2 --net0 virtio,bridge=vmbr0

# 3. Importer le disque
qm importdisk 9000 /var/lib/vz/template/iso/jammy-server-cloudimg-amd64.img local-lvm

# 4. Attacher le disque
qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9000-disk-0

# 5. Configurer Cloud-Init
qm set 9000 --ide2 local-lvm:cloudinit

# 6. Configurer le boot
qm set 9000 --boot c --bootdisk scsi0

# 7. Ajouter serial console
qm set 9000 --serial0 socket --vga serial0

# 8. Activer l'agent QEMU (optionnel)
qm set 9000 --agent enabled=1

# 9. Convertir en template
qm template 9000

# 10. Vérifier que le template existe
qm list | grep template
EOF

echo ""

# Script de création automatique pour Proxmox
echo -e "${CYAN}=====================================${NC}"
echo -e "${CYAN}  Script de création automatique${NC}"
echo -e "${CYAN}=====================================${NC}"
echo ""

read -p "Voulez-vous générer un script pour créer le template automatiquement? (o/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Oo]$ ]]; then
    cat > create-proxmox-template.sh << 'SCRIPT_EOF'
#!/bin/bash
# Script automatique pour créer un template Ubuntu 22.04 sur Proxmox
# À exécuter sur le serveur Proxmox directement

set -e

TEMPLATE_ID=${1:-9000}
TEMPLATE_NAME="ubuntu-22.04-template"
STORAGE=${2:-local-lvm}

echo "Création du template VM ID: $TEMPLATE_ID"
echo "Storage: $STORAGE"
echo ""

# Télécharger l'image cloud
echo "📥 Téléchargement de l'image Ubuntu 22.04 cloud..."
cd /var/lib/vz/template/iso
if [ ! -f "jammy-server-cloudimg-amd64.img" ]; then
    wget https://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img
else
    echo "✅ Image déjà téléchargée"
fi

# Créer la VM
echo "🔨 Création de la VM..."
qm create $TEMPLATE_ID \
    --name $TEMPLATE_NAME \
    --memory 2048 \
    --cores 2 \
    --net0 virtio,bridge=vmbr0

# Importer le disque
echo "💾 Import du disque..."
qm importdisk $TEMPLATE_ID /var/lib/vz/template/iso/jammy-server-cloudimg-amd64.img $STORAGE

# Configurer la VM
echo "⚙️  Configuration de la VM..."
qm set $TEMPLATE_ID --scsihw virtio-scsi-pci --scsi0 ${STORAGE}:vm-${TEMPLATE_ID}-disk-0
qm set $TEMPLATE_ID --ide2 ${STORAGE}:cloudinit
qm set $TEMPLATE_ID --boot c --bootdisk scsi0
qm set $TEMPLATE_ID --serial0 socket --vga serial0
qm set $TEMPLATE_ID --agent enabled=1

# Convertir en template
echo "📦 Conversion en template..."
qm template $TEMPLATE_ID

echo ""
echo "✅ Template créé avec succès!"
echo ""
echo "Détails:"
qm config $TEMPLATE_ID
echo ""
echo "Pour utiliser ce template, configurez dans .env:"
echo "TEMPLATE_NAME=$TEMPLATE_NAME"
echo "# ou"
echo "TEMPLATE_NAME=$TEMPLATE_ID"
SCRIPT_EOF

    chmod +x create-proxmox-template.sh
    echo -e "${GREEN}✅ Script créé: create-proxmox-template.sh${NC}"
    echo -e "${YELLOW}   Copiez ce script sur votre serveur Proxmox et exécutez-le${NC}"
    echo ""
fi

# Proposer de mettre à jour .env
echo -e "${CYAN}=====================================${NC}"
echo -e "${CYAN}  Mise à jour recommandée${NC}"
echo -e "${CYAN}=====================================${NC}"
echo ""

read -p "Voulez-vous mettre à jour TEMPLATE_NAME dans .env? (o/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Oo]$ ]]; then
    echo ""
    echo -e "${CYAN}Choisissez une option:${NC}"
    echo "1. Utiliser le nom du template (ex: ubuntu-22.04-template)"
    echo "2. Utiliser l'ID du template (ex: 9000)"
    echo ""
    
    read -p "Votre choix (1/2): " choice
    
    if [ "$choice" == "1" ]; then
        read -p "Entrez le nom du template: " new_template_name
        if [ -n "$new_template_name" ]; then
            sed -i.bak "s/^TEMPLATE_NAME=.*/TEMPLATE_NAME=$new_template_name/" .env
            echo -e "${GREEN}✅ TEMPLATE_NAME mis à jour: $new_template_name${NC}"
        fi
    elif [ "$choice" == "2" ]; then
        read -p "Entrez l'ID du template: " new_template_id
        if [ -n "$new_template_id" ]; then
            sed -i.bak "s/^TEMPLATE_NAME=.*/TEMPLATE_NAME=$new_template_id/" .env
            echo -e "${GREEN}✅ TEMPLATE_NAME mis à jour: $new_template_id${NC}"
        fi
    fi
fi

echo ""
echo -e "${CYAN}=====================================${NC}"
echo -e "${CYAN}  Test de connectivité${NC}"
echo -e "${CYAN}=====================================${NC}"
echo ""

# Tester la connectivité réseau
echo -e "${YELLOW}Test de connectivité réseau...${NC}"

TEST_URLS=("registry.terraform.io" "github.com" "releases.hashicorp.com")

for url in "${TEST_URLS[@]}"; do
    if ping -c 1 -W 2 "$url" &> /dev/null; then
        echo -e "${GREEN}✅ $url : OK${NC}"
    else
        echo -e "${RED}❌ $url : ÉCHEC${NC}"
    fi
done

echo ""
echo -e "${CYAN}=====================================${NC}"
echo -e "${CYAN}  Résumé${NC}"
echo -e "${CYAN}=====================================${NC}"
echo ""

if [ ${#MISSING_VARS[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ Configuration .env complète${NC}"
else
    echo -e "${YELLOW}⚠️  Configuration .env incomplète - vérifiez les variables${NC}"
fi

echo ""
echo -e "${CYAN}📚 Pour plus d'informations, consultez:${NC}"
echo "   - QUICK_FIX.md : Guide de résolution rapide"
echo "   - docs/INSTALLATION.md : Guide d'installation complet"
echo "   - docs/TROUBLESHOOTING.md : Guide de dépannage"
echo ""
echo -e "${GREEN}🚀 Pour démarrer l'application: ./start.sh${NC}"
echo ""
