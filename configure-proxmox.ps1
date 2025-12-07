# Script de Configuration Interactive Proxmox
# Usage: .\configure-proxmox.ps1

Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                          ║" -ForegroundColor Cyan
Write-Host "║     Configuration Interactive Proxmox pour PaaS          ║" -ForegroundColor Cyan
Write-Host "║                                                          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Fonction pour valider une IP
function Test-IPAddress {
    param([string]$IP)
    try {
        [System.Net.IPAddress]::Parse($IP) | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Vérifier que .env existe
if (!(Test-Path ".env")) {
    Write-Host "⚠️  Fichier .env non trouvé!" -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Fichier .env créé depuis .env.example`n" -ForegroundColor Green
    } else {
        Write-Host "❌ .env.example non trouvé! Impossible de continuer." -ForegroundColor Red
        exit 1
    }
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host " ÉTAPE 1 : Configuration de l'Adresse Proxmox" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

# Demander l'adresse IP
do {
    $proxmoxIP = Read-Host "Entrez l'adresse IP de votre serveur Proxmox (ex: 192.168.1.50)"
    if (!(Test-IPAddress $proxmoxIP)) {
        Write-Host "❌ Adresse IP invalide. Réessayez." -ForegroundColor Red
    }
} while (!(Test-IPAddress $proxmoxIP))

Write-Host "✅ IP Proxmox: $proxmoxIP`n" -ForegroundColor Green

# Tester la connectivité
Write-Host "🔍 Test de connectivité vers $proxmoxIP..." -ForegroundColor Cyan
if (Test-Connection -ComputerName $proxmoxIP -Count 1 -Quiet) {
    Write-Host "✅ Serveur accessible`n" -ForegroundColor Green
} else {
    Write-Host "⚠️  Impossible de ping le serveur (peut être normal si ICMP est bloqué)`n" -ForegroundColor Yellow
}

# Tester le port 8006
Write-Host "🔍 Test du port 8006 (API Proxmox)..." -ForegroundColor Cyan
try {
    $tcpTest = Test-NetConnection -ComputerName $proxmoxIP -Port 8006 -WarningAction SilentlyContinue
    if ($tcpTest.TcpTestSucceeded) {
        Write-Host "✅ Port 8006 accessible`n" -ForegroundColor Green
    } else {
        Write-Host "❌ Port 8006 inaccessible!" -ForegroundColor Red
        Write-Host "   Vérifiez que Proxmox est démarré et accessible`n" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Impossible de tester le port (peut nécessiter des droits admin)`n" -ForegroundColor Yellow
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host " ÉTAPE 2 : Configuration du Token API" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

Write-Host "Pour créer un token API sur Proxmox:" -ForegroundColor White
Write-Host "1. Ouvrez https://${proxmoxIP}:8006 dans votre navigateur" -ForegroundColor Gray
Write-Host "2. Datacenter → Permissions → Users → Add" -ForegroundColor Gray
Write-Host "   - Username: terraform@pve" -ForegroundColor Gray
Write-Host "3. Datacenter → Permissions → Add → User Permission" -ForegroundColor Gray
Write-Host "   - Path: /, User: terraform@pve, Role: Administrator" -ForegroundColor Gray
Write-Host "4. Datacenter → Permissions → API Tokens → Add" -ForegroundColor Gray
Write-Host "   - User: terraform@pve, Token ID: terraform-token" -ForegroundColor Gray
Write-Host "   - ❌ DÉCOCHER 'Privilege Separation'" -ForegroundColor Red
Write-Host "`n"

$openBrowser = Read-Host "Voulez-vous ouvrir Proxmox dans le navigateur maintenant? (o/n)"
if ($openBrowser -eq 'o' -or $openBrowser -eq 'O') {
    Start-Process "https://${proxmoxIP}:8006"
    Write-Host "✅ Navigateur ouvert`n" -ForegroundColor Green
}

Write-Host "Avez-vous déjà créé le token API? (o/n)" -ForegroundColor Cyan
$hasToken = Read-Host

if ($hasToken -eq 'o' -or $hasToken -eq 'O') {
    Write-Host "`nEntrez les informations du token:`n" -ForegroundColor Cyan
    
    # Token ID
    $defaultTokenID = "terraform@pve!terraform-token"
    $tokenID = Read-Host "Token ID (appuyez sur Entrée pour utiliser '$defaultTokenID')"
    if ([string]::IsNullOrWhiteSpace($tokenID)) {
        $tokenID = $defaultTokenID
    }
    Write-Host "✅ Token ID: $tokenID`n" -ForegroundColor Green
    
    # Token Secret
    do {
        $tokenSecret = Read-Host "Token Secret (format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)"
        if ([string]::IsNullOrWhiteSpace($tokenSecret)) {
            Write-Host "❌ Le secret ne peut pas être vide!" -ForegroundColor Red
        }
    } while ([string]::IsNullOrWhiteSpace($tokenSecret))
    Write-Host "✅ Secret configuré`n" -ForegroundColor Green
    
} else {
    Write-Host "`n⚠️  Vous devez d'abord créer le token API sur Proxmox!" -ForegroundColor Yellow
    Write-Host "Relancez ce script après avoir créé le token.`n" -ForegroundColor Yellow
    pause
    exit 0
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host " ÉTAPE 3 : Configuration du Nœud Proxmox" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

$defaultNode = "pve"
$proxmoxNode = Read-Host "Nom du nœud Proxmox (appuyez sur Entrée pour '$defaultNode')"
if ([string]::IsNullOrWhiteSpace($proxmoxNode)) {
    $proxmoxNode = $defaultNode
}
Write-Host "✅ Nœud: $proxmoxNode`n" -ForegroundColor Green

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host " ÉTAPE 4 : Configuration du Template" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

Write-Host "Avez-vous un template VM sur Proxmox? (o/n)" -ForegroundColor Cyan
$hasTemplate = Read-Host

if ($hasTemplate -eq 'o' -or $hasTemplate -eq 'O') {
    $templateName = Read-Host "Entrez l'ID ou le nom du template (ex: 9000 ou ubuntu-22.04-template)"
    Write-Host "✅ Template: $templateName`n" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Aucun template trouvé!" -ForegroundColor Yellow
    Write-Host "Vous devrez créer un template avant de faire un déploiement.`n" -ForegroundColor Yellow
    Write-Host "Utiliser le template par défaut pour l'instant..." -ForegroundColor Gray
    $templateName = "ubuntu-22.04-template"
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host " ÉTAPE 5 : Mise à Jour du Fichier .env" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

# Lire le fichier .env
$envContent = Get-Content ".env"

# Remplacer les valeurs
$envContent = $envContent -replace "^PROXMOX_API_URL=.*", "PROXMOX_API_URL=https://${proxmoxIP}:8006/api2/json"
$envContent = $envContent -replace "^PROXMOX_API_TOKEN_ID=.*", "PROXMOX_API_TOKEN_ID=$tokenID"
$envContent = $envContent -replace "^PROXMOX_API_TOKEN_SECRET=.*", "PROXMOX_API_TOKEN_SECRET=$tokenSecret"
$envContent = $envContent -replace "^PROXMOX_NODE=.*", "PROXMOX_NODE=$proxmoxNode"
$envContent = $envContent -replace "^TEMPLATE_NAME=.*", "TEMPLATE_NAME=$templateName"

# Sauvegarder
$envContent | Set-Content ".env"

Write-Host "✅ Fichier .env mis à jour!`n" -ForegroundColor Green

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host " ÉTAPE 6 : Test de Connexion" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

Write-Host "🔍 Test de l'API Proxmox..." -ForegroundColor Cyan

try {
    $url = "https://${proxmoxIP}:8006/api2/json/version"
    $headers = @{
        "Authorization" = "PVEAPIToken=${tokenID}=${tokenSecret}"
    }
    
    $response = Invoke-RestMethod -Uri $url -Headers $headers -SkipCertificateCheck -ErrorAction Stop
    
    Write-Host "✅ Connexion réussie!" -ForegroundColor Green
    Write-Host "`nInformations Proxmox:" -ForegroundColor Cyan
    Write-Host "  Version: $($response.data.version)" -ForegroundColor White
    Write-Host "  Release: $($response.data.release)`n" -ForegroundColor White
    
    $connectionSuccess = $true
} catch {
    Write-Host "❌ Échec de connexion!" -ForegroundColor Red
    Write-Host "Erreur: $($_.Exception.Message)`n" -ForegroundColor Red
    Write-Host "Vérifiez:" -ForegroundColor Yellow
    Write-Host "  - L'adresse IP est correcte" -ForegroundColor White
    Write-Host "  - Le token API est valide" -ForegroundColor White
    Write-Host "  - Les permissions sont correctes`n" -ForegroundColor White
    
    $connectionSuccess = $false
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host " RÉSUMÉ DE LA CONFIGURATION" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Gray

Write-Host "Configuration actuelle:" -ForegroundColor Cyan
Write-Host "  Proxmox URL     : https://${proxmoxIP}:8006" -ForegroundColor White
Write-Host "  Token ID        : $tokenID" -ForegroundColor White
Write-Host "  Nœud            : $proxmoxNode" -ForegroundColor White
Write-Host "  Template        : $templateName" -ForegroundColor White
Write-Host "  Connexion       : $(if ($connectionSuccess) {'✅ OK'} else {'❌ ÉCHEC'})" -ForegroundColor $(if ($connectionSuccess) {'Green'} else {'Red'})
Write-Host ""

if ($connectionSuccess) {
    Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                                                          ║" -ForegroundColor Green
    Write-Host "║  ✅ CONFIGURATION RÉUSSIE!                               ║" -ForegroundColor Green
    Write-Host "║                                                          ║" -ForegroundColor Green
    Write-Host "║  Vous pouvez maintenant démarrer l'application :         ║" -ForegroundColor Green
    Write-Host "║  .\start.bat                                             ║" -ForegroundColor Green
    Write-Host "║                                                          ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    
    if ($hasTemplate -eq 'n' -or $hasTemplate -eq 'N') {
        Write-Host "⚠️  N'oubliez pas de créer un template avant le premier déploiement!" -ForegroundColor Yellow
        Write-Host "   Consultez GUIDE_CONFIGURATION_PROXMOX.md pour les instructions`n" -ForegroundColor Yellow
    }
    
    $startNow = Read-Host "Voulez-vous démarrer l'application maintenant? (o/n)"
    if ($startNow -eq 'o' -or $startNow -eq 'O') {
        Write-Host "`n🚀 Démarrage de l'application...`n" -ForegroundColor Cyan
        .\start.bat
    }
    
} else {
    Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║                                                          ║" -ForegroundColor Red
    Write-Host "║  ❌ ÉCHEC DE LA CONFIGURATION                            ║" -ForegroundColor Red
    Write-Host "║                                                          ║" -ForegroundColor Red
    Write-Host "║  La connexion à Proxmox a échoué.                        ║" -ForegroundColor Red
    Write-Host "║                                                          ║" -ForegroundColor Red
    Write-Host "║  Actions recommandées :                                  ║" -ForegroundColor Red
    Write-Host "║  1. Vérifiez que Proxmox est accessible                  ║" -ForegroundColor Red
    Write-Host "║  2. Vérifiez le token API                                ║" -ForegroundColor Red
    Write-Host "║  3. Consultez GUIDE_CONFIGURATION_PROXMOX.md             ║" -ForegroundColor Red
    Write-Host "║                                                          ║" -ForegroundColor Red
    Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Red
    Write-Host ""
}

Write-Host "📚 Documentation disponible:" -ForegroundColor Cyan
Write-Host "   - GUIDE_CONFIGURATION_PROXMOX.md : Guide détaillé" -ForegroundColor White
Write-Host "   - QUICK_FIX.md : Solutions rapides" -ForegroundColor White
Write-Host "   - check-proxmox-templates.ps1 : Vérification templates`n" -ForegroundColor White
