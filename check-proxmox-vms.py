#!/usr/bin/env python3
"""
Script pour vérifier les VMs et templates disponibles sur Proxmox
"""

import os
from dotenv import load_dotenv
from proxmoxer import ProxmoxAPI

# Charger les variables d'environnement
load_dotenv()

def main():
    print("=" * 70)
    print("  VÉRIFICATION DES VMs ET TEMPLATES PROXMOX")
    print("=" * 70)
    print()
    
    # Configuration
    api_url = os.getenv('PROXMOX_API_URL', 'https://10.220.201.100:8006')
    token_id = os.getenv('PROXMOX_API_TOKEN_ID', 'root@pam!zeineb')
    token_secret = os.getenv('PROXMOX_API_TOKEN_SECRET')
    node = os.getenv('PROXMOX_NODE', 'pve')
    
    print(f"📡 Connexion à Proxmox: {api_url}")
    print(f"🔑 Token ID: {token_id}")
    print(f"🖥️  Node: {node}")
    print()
    
    try:
        # Se connecter à Proxmox
        user, token_name = token_id.split('!')
        
        proxmox = ProxmoxAPI(
            api_url,
            user=user,
            token_name=token_name,
            token_value=token_secret,
            verify_ssl=False
        )
        
        print("✅ Connexion réussie!")
        print()
        
        # Récupérer les VMs
        vms = proxmox.nodes(node).qemu.get()
        
        print(f"📋 VMs trouvées sur le node '{node}':")
        print("-" * 70)
        print(f"{'ID':<8} {'Nom':<25} {'Status':<12} {'Template':<10}")
        print("-" * 70)
        
        templates_found = []
        regular_vms = []
        
        for vm in vms:
            vm_id = vm.get('vmid', 'N/A')
            vm_name = vm.get('name', 'N/A')
            vm_status = vm.get('status', 'N/A')
            is_template = vm.get('template', 0)
            
            template_str = "✅ OUI" if is_template else "❌ Non"
            
            print(f"{vm_id:<8} {vm_name:<25} {vm_status:<12} {template_str:<10}")
            
            if is_template:
                templates_found.append((vm_id, vm_name))
            else:
                regular_vms.append((vm_id, vm_name))
        
        print("-" * 70)
        print()
        
        # Résumé
        print("=" * 70)
        print("  RÉSUMÉ")
        print("=" * 70)
        print()
        
        if templates_found:
            print(f"✅ {len(templates_found)} template(s) trouvé(s):")
            for vm_id, vm_name in templates_found:
                print(f"   - ID {vm_id}: {vm_name}")
            print()
            print("💡 Pour utiliser un de ces templates, modifiez le .env:")
            print(f"   TEMPLATE_NAME={templates_found[0][0]}")
        else:
            print("❌ Aucun template trouvé!")
            print()
            print("💡 VMs disponibles pour conversion en template:")
            if regular_vms:
                for vm_id, vm_name in regular_vms:
                    print(f"   - ID {vm_id}: {vm_name}")
                    print(f"     Conversion: ssh root@{api_url.split('//')[1].split(':')[0]} 'qm template {vm_id}'")
            else:
                print("   Aucune VM disponible. Vous devez créer une VM d'abord.")
        
        print()
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
