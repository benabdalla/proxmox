# Script pour convertir la VM 100 en template Proxmox
# Utilisation: Exécutez ce script pour obtenir les commandes à exécuter sur Proxmox

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  CONVERSION DE LA VM 100 EN TEMPLATE PROXMOX" -ForegroundColor Yellow
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "ÉTAPE 1: Vérifier que la VM 100 existe" -ForegroundColor Green
Write-Host "Connectez-vous à votre serveur Proxmox via SSH:" -ForegroundColor White
Write-Host "  ssh root@10.220.201.100" -ForegroundColor Yellow
Write-Host ""

Write-Host "ÉTAPE 2: Vérifier l'état de la VM" -ForegroundColor Green
Write-Host "Exécutez cette commande pour voir si la VM 100 existe:" -ForegroundColor White
Write-Host "  qm list | grep 100" -ForegroundColor Yellow
Write-Host ""

Write-Host "ÉTAPE 3: Arrêter la VM si elle tourne" -ForegroundColor Green
Write-Host "Si la VM est en cours d'exécution, arrêtez-la:" -ForegroundColor White
Write-Host "  qm stop 100" -ForegroundColor Yellow
Write-Host ""

Write-Host "ÉTAPE 4: Convertir la VM en template" -ForegroundColor Green
Write-Host "Convertissez la VM 100 en template:" -ForegroundColor White
Write-Host "  qm template 100" -ForegroundColor Yellow
Write-Host ""

Write-Host "ÉTAPE 5: Vérifier la conversion" -ForegroundColor Green
Write-Host "Vérifiez que la VM est maintenant un template:" -ForegroundColor White
Write-Host "  qm list | grep 100" -ForegroundColor Yellow
Write-Host "  (Vous devriez voir 'T' dans la colonne STATUS)" -ForegroundColor Gray
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "ALTERNATIVE: Si la VM 100 n'existe pas" -ForegroundColor Magenta
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Vous devez créer un template Ubuntu manuellement:" -ForegroundColor White
Write-Host ""
Write-Host "1. Dans l'interface Proxmox (https://10.220.201.100:8006)" -ForegroundColor Yellow
Write-Host "2. Créez une nouvelle VM avec l'ID 100" -ForegroundColor Yellow
Write-Host "3. Installez Ubuntu 22.04 (ou votre OS préféré)" -ForegroundColor Yellow
Write-Host "4. Installez cloud-init:" -ForegroundColor Yellow
Write-Host "     apt update && apt install -y cloud-init qemu-guest-agent" -ForegroundColor Gray
Write-Host "5. Nettoyez la VM:" -ForegroundColor Yellow
Write-Host "     cloud-init clean" -ForegroundColor Gray
Write-Host "     rm -rf /var/lib/cloud/instances" -ForegroundColor Gray
Write-Host "6. Arrêtez la VM" -ForegroundColor Yellow
Write-Host "7. Convertissez-la en template: qm template 100" -ForegroundColor Yellow
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Après la conversion, redémarrez votre application:" -ForegroundColor Green
Write-Host "  cd C:\Users\zeine\OneDrive\Desktop\proxmox" -ForegroundColor Yellow
Write-Host "  .\start.bat" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
