# Script PowerShell pour vérifier et configurer les templates Proxmox
# Usage: .\check-proxmox-templates.ps1

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Vérification Configuration Proxmox" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Fonction pour lire le fichier .env
function Get-EnvValue {
    param([string]$Key)
    
    if (Test-Path ".env") {
        $content = Get-Content ".env"
        foreach ($line in $content) {
            if ($line -match "^$Key=(.+)$") {
                return $matches[1]
            }
        }
    }
    return $null
}

# Vérifier si .env existe
if (!(Test-Path ".env")) {
    Write-Host "⚠️  Fichier .env non trouvé!" -ForegroundColor Yellow
    Write-Host "Création depuis .env.example..." -ForegroundColor Yellow
    
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Fichier .env créé. Veuillez le configurer." -ForegroundColor Green
    } else {
        Write-Host "❌ .env.example non trouvé!" -ForegroundColor Red
        exit 1
    }
}

# Lire les configurations
$proxmoxUrl = Get-EnvValue "PROXMOX_API_URL"
$proxmoxNode = Get-EnvValue "PROXMOX_NODE"
$templateName = Get-EnvValue "TEMPLATE_NAME"
$lxcTemplate = Get-EnvValue "LXC_TEMPLATE"

Write-Host "📋 Configuration actuelle:" -ForegroundColor Cyan
Write-Host "   Proxmox URL: $proxmoxUrl" -ForegroundColor White
Write-Host "   Proxmox Node: $proxmoxNode" -ForegroundColor White
Write-Host "   VM Template: $templateName" -ForegroundColor White
Write-Host "   LXC Template: $lxcTemplate" -ForegroundColor White
Write-Host ""

# Vérifier si les variables critiques sont configurées
$missingVars = @()

if (!$proxmoxUrl -or $proxmoxUrl -like "*proxmox-server.local*") {
    $missingVars += "PROXMOX_API_URL"
}

if (!$templateName -or $templateName -eq "ubuntu-22.04-template") {
    Write-Host "⚠️  TEMPLATE_NAME utilise la valeur par défaut" -ForegroundColor Yellow
    Write-Host "   Assurez-vous qu'un template nommé 'ubuntu-22.04-template' existe sur Proxmox" -ForegroundColor Yellow
    Write-Host ""
}

if ($missingVars.Count -gt 0) {
    Write-Host "❌ Variables manquantes dans .env:" -ForegroundColor Red
    foreach ($var in $missingVars) {
        Write-Host "   - $var" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "📝 Veuillez éditer le fichier .env et configurer ces variables" -ForegroundColor Yellow
    Write-Host ""
}

# Générer les commandes pour créer un template sur Proxmox
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Commandes pour créer le template" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Si vous n'avez pas encore de template, connectez-vous à Proxmox via SSH et exécutez:" -ForegroundColor Yellow
Write-Host ""

$sshCommands = @"
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
"@

Write-Host $sshCommands -ForegroundColor Gray
Write-Host ""

# Proposer de mettre à jour .env
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Mise à jour recommandée" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$updateEnv = Read-Host "Voulez-vous mettre à jour TEMPLATE_NAME dans .env? (o/n)"

if ($updateEnv -eq 'o' -or $updateEnv -eq 'O') {
    Write-Host ""
    Write-Host "Choisissez une option:" -ForegroundColor Cyan
    Write-Host "1. Utiliser le nom du template (ex: ubuntu-22.04-template)" -ForegroundColor White
    Write-Host "2. Utiliser l'ID du template (ex: 9000)" -ForegroundColor White
    Write-Host ""
    
    $choice = Read-Host "Votre choix (1/2)"
    
    if ($choice -eq '1') {
        $newTemplateName = Read-Host "Entrez le nom du template"
        if ($newTemplateName) {
            $envContent = Get-Content ".env"
            $envContent = $envContent -replace "^TEMPLATE_NAME=.*", "TEMPLATE_NAME=$newTemplateName"
            $envContent | Set-Content ".env"
            Write-Host "✅ TEMPLATE_NAME mis à jour: $newTemplateName" -ForegroundColor Green
        }
    }
    elseif ($choice -eq '2') {
        $newTemplateId = Read-Host "Entrez l'ID du template"
        if ($newTemplateId) {
            $envContent = Get-Content ".env"
            $envContent = $envContent -replace "^TEMPLATE_NAME=.*", "TEMPLATE_NAME=$newTemplateId"
            $envContent | Set-Content ".env"
            Write-Host "✅ TEMPLATE_NAME mis à jour: $newTemplateId" -ForegroundColor Green
        }
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Test de connectivité" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Tester la connectivité réseau
Write-Host "Test de connectivité réseau..." -ForegroundColor Yellow

$testUrls = @(
    "registry.terraform.io",
    "github.com",
    "releases.hashicorp.com"
)

foreach ($url in $testUrls) {
    try {
        $result = Test-Connection -ComputerName $url -Count 1 -Quiet
        if ($result) {
            Write-Host "✅ $url : OK" -ForegroundColor Green
        } else {
            Write-Host "❌ $url : ÉCHEC" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ $url : ERREUR" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  Résumé" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

if ($missingVars.Count -eq 0) {
    Write-Host "✅ Configuration .env complète" -ForegroundColor Green
} else {
    Write-Host "⚠️  Configuration .env incomplète - vérifiez les variables" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📚 Pour plus d'informations, consultez:" -ForegroundColor Cyan
Write-Host "   - QUICK_FIX.md : Guide de résolution rapide" -ForegroundColor White
Write-Host "   - docs/INSTALLATION.md : Guide d'installation complet" -ForegroundColor White
Write-Host "   - docs/TROUBLESHOOTING.md : Guide de dépannage" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Pour démarrer l'application: .\start.bat" -ForegroundColor Green
Write-Host ""
