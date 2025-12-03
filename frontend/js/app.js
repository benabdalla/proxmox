// Configuration API
const API_BASE_URL = window.location.origin;

// État de l'application
let currentDeployments = [];
let refreshInterval = null;

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initForm();
    initResourceSliders();
    checkSystemStatus();
    loadDeployments();
    loadResources();
    
    // Rafraîchissement automatique
    refreshInterval = setInterval(() => {
        if (document.querySelector('#deployments-tab').classList.contains('active')) {
            loadDeployments();
        }
    }, 10000); // Toutes les 10 secondes
});

// Gestion des onglets
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            
            // Retirer active de tous les boutons et contenus
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            // Ajouter active au bouton et contenu sélectionné
            button.classList.add('active');
            document.getElementById(`${tabName}-tab`).classList.add('active');
            
            // Charger les données si nécessaire
            if (tabName === 'deployments') {
                loadDeployments();
            } else if (tabName === 'resources') {
                loadResources();
            }
        });
    });
}

// Initialisation du formulaire
function initForm() {
    const form = document.getElementById('deploymentForm');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        const data = {
            type: formData.get('type'),
            framework: formData.get('framework'),
            github_url: formData.get('github_url'),
            cpu: parseInt(formData.get('cpu')),
            memory: parseInt(formData.get('memory')),
            disk: parseInt(formData.get('disk'))
        };
        
        const name = formData.get('name');
        if (name) {
            data.name = name;
        }
        
        await createDeployment(data);
    });
}

// Synchronisation des sliders avec les inputs
function initResourceSliders() {
    const resources = ['cpu', 'memory', 'disk'];
    
    resources.forEach(resource => {
        const input = document.getElementById(resource);
        const slider = document.getElementById(`${resource}-range`);
        
        // Slider vers input
        slider.addEventListener('input', () => {
            input.value = slider.value;
        });
        
        // Input vers slider
        input.addEventListener('input', () => {
            slider.value = input.value;
        });
    });
}

// Vérification du statut du système
async function checkSystemStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/status`);
        const data = await response.json();
        
        const statusIndicator = document.getElementById('systemStatus');
        
        if (data.system && data.system.proxmox_connected) {
            statusIndicator.className = 'status-indicator connected';
            statusIndicator.innerHTML = '<i class="fas fa-circle"></i> Connecté à Proxmox';
        } else {
            statusIndicator.className = 'status-indicator disconnected';
            statusIndicator.innerHTML = '<i class="fas fa-circle"></i> Proxmox déconnecté';
        }
    } catch (error) {
        console.error('Erreur vérification statut:', error);
        const statusIndicator = document.getElementById('systemStatus');
        statusIndicator.className = 'status-indicator disconnected';
        statusIndicator.innerHTML = '<i class="fas fa-circle"></i> Erreur de connexion';
    }
}

// Créer un déploiement
async function createDeployment(data) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/deploy`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showNotification('Déploiement démarré avec succès!', 'success');
            document.getElementById('deploymentForm').reset();
            
            // Afficher le modal de progression
            showDeploymentProgress(result.deployment.id);
            
            // Passer à l'onglet des déploiements
            setTimeout(() => {
                document.querySelector('[data-tab="deployments"]').click();
            }, 2000);
        } else {
            showNotification(`Erreur: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Erreur création déploiement:', error);
        showNotification('Erreur lors de la création du déploiement', 'error');
    }
}

// Afficher la progression d'un déploiement
function showDeploymentProgress(deploymentId) {
    const modal = document.getElementById('deploymentModal');
    const stepsContainer = document.getElementById('progressSteps');
    const logContainer = document.getElementById('deploymentLog');
    
    // Étapes de déploiement
    const steps = [
        { id: 'init', label: 'Initialisation', icon: 'fa-check-circle' },
        { id: 'terraform', label: 'Création infrastructure Terraform', icon: 'fa-cog' },
        { id: 'vm', label: 'Création VM/LXC', icon: 'fa-server' },
        { id: 'install', label: 'Installation framework', icon: 'fa-download' },
        { id: 'deploy', label: 'Déploiement application', icon: 'fa-rocket' },
        { id: 'done', label: 'Terminé', icon: 'fa-check' }
    ];
    
    stepsContainer.innerHTML = steps.map(step => `
        <div class="step" id="step-${step.id}">
            <i class="fas ${step.icon}"></i>
            <span>${step.label}</span>
        </div>
    `).join('');
    
    logContainer.textContent = 'Déploiement en cours...\n';
    modal.classList.add('active');
    
    // Simuler la progression (dans la réalité, utiliser WebSocket ou polling)
    let currentStep = 0;
    const interval = setInterval(async () => {
        if (currentStep < steps.length) {
            document.getElementById(`step-${steps[currentStep].id}`).classList.add('active');
            
            if (currentStep > 0) {
                document.getElementById(`step-${steps[currentStep - 1].id}`).classList.remove('active');
                document.getElementById(`step-${steps[currentStep - 1].id}`).classList.add('completed');
            }
            
            logContainer.textContent += `✓ ${steps[currentStep].label}\n`;
            currentStep++;
        } else {
            clearInterval(interval);
            setTimeout(() => {
                modal.classList.remove('active');
            }, 2000);
        }
    }, 2000);
}

// Charger les déploiements
async function loadDeployments() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/deployments`);
        const data = await response.json();
        
        currentDeployments = data.deployments || [];
        displayDeployments(currentDeployments);
    } catch (error) {
        console.error('Erreur chargement déploiements:', error);
        document.getElementById('deploymentsList').innerHTML = `
            <div class="loading">
                <i class="fas fa-exclamation-circle"></i> Erreur de chargement
            </div>
        `;
    }
}

// Afficher les déploiements
function displayDeployments(deployments) {
    const container = document.getElementById('deploymentsList');
    
    if (!deployments || deployments.length === 0) {
        container.innerHTML = `
            <div class="loading">
                <i class="fas fa-info-circle"></i> Aucun déploiement
            </div>
        `;
        return;
    }
    
    container.innerHTML = deployments.map(deployment => `
        <div class="deployment-item">
            <div class="deployment-header">
                <div class="deployment-name">
                    <i class="fas fa-project-diagram"></i> ${deployment.name}
                </div>
                <span class="deployment-status status-${deployment.status}">
                    ${getStatusLabel(deployment.status)}
                </span>
            </div>
            
            <div class="deployment-info">
                <div class="info-item">
                    <i class="fas fa-code"></i>
                    <span>${deployment.framework}</span>
                </div>
                <div class="info-item">
                    <i class="fas fa-${deployment.type === 'vm' ? 'desktop' : 'box'}"></i>
                    <span>${deployment.type.toUpperCase()}</span>
                </div>
                <div class="info-item">
                    <i class="fas fa-microchip"></i>
                    <span>${deployment.resources.cpu} CPU / ${deployment.resources.memory} MB</span>
                </div>
                ${deployment.proxmox.ip ? `
                <div class="info-item">
                    <i class="fas fa-network-wired"></i>
                    <span>${deployment.proxmox.ip}</span>
                </div>
                ` : ''}
            </div>
            
            <div class="deployment-info">
                <div class="info-item">
                    <i class="fab fa-github"></i>
                    <span>${deployment.github_url}</span>
                </div>
                <div class="info-item">
                    <i class="fas fa-clock"></i>
                    <span>${formatDate(deployment.created_at)}</span>
                </div>
            </div>
            
            <div class="deployment-actions">
                ${deployment.status === 'running' ? `
                    <button class="btn btn-small btn-primary" onclick="window.open('http://${deployment.proxmox.ip}', '_blank')">
                        <i class="fas fa-external-link-alt"></i> Ouvrir
                    </button>
                    <button class="btn btn-small btn-secondary" onclick="restartDeployment(${deployment.id})">
                        <i class="fas fa-redo"></i> Redémarrer
                    </button>
                ` : ''}
                ${deployment.status === 'failed' ? `
                    <button class="btn btn-small" onclick="showLogs(${deployment.id})">
                        <i class="fas fa-file-alt"></i> Voir logs
                    </button>
                ` : ''}
                <button class="btn btn-small btn-danger" onclick="deleteDeployment(${deployment.id})">
                    <i class="fas fa-trash"></i> Supprimer
                </button>
            </div>
        </div>
    `).join('');
}

// Charger les ressources
async function loadResources() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/resources`);
        const data = await response.json();
        
        displayResources(data);
    } catch (error) {
        console.error('Erreur chargement ressources:', error);
        document.getElementById('resourcesInfo').innerHTML = `
            <div class="loading">
                <i class="fas fa-exclamation-circle"></i> Erreur de chargement
            </div>
        `;
    }
}

// Afficher les ressources
function displayResources(data) {
    const container = document.getElementById('resourcesInfo');
    
    if (data.error) {
        container.innerHTML = `
            <div class="loading">
                <i class="fas fa-exclamation-circle"></i> ${data.error}
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="resources-grid">
            <div class="resource-card">
                <h3><i class="fas fa-server"></i> Noeud Proxmox</h3>
                <div class="resource-stat">
                    <span>Nom:</span>
                    <strong>${data.node.name}</strong>
                </div>
                <div class="resource-stat">
                    <span>Statut:</span>
                    <strong style="color: var(--success-color)">${data.node.status}</strong>
                </div>
            </div>
            
            <div class="resource-card">
                <h3><i class="fas fa-microchip"></i> CPU</h3>
                <div class="resource-stat">
                    <span>Coeurs:</span>
                    <strong>${data.node.cpu.cores}</strong>
                </div>
                <div class="resource-stat">
                    <span>Utilisation:</span>
                    <strong>${data.node.cpu.usage}%</strong>
                </div>
            </div>
            
            <div class="resource-card">
                <h3><i class="fas fa-memory"></i> Mémoire</h3>
                <div class="resource-stat">
                    <span>Total:</span>
                    <strong>${data.node.memory.total} GB</strong>
                </div>
                <div class="resource-stat">
                    <span>Utilisée:</span>
                    <strong>${data.node.memory.used} GB</strong>
                </div>
                <div class="resource-stat">
                    <span>Disponible:</span>
                    <strong>${data.node.memory.free} GB</strong>
                </div>
            </div>
            
            <div class="resource-card">
                <h3><i class="fas fa-desktop"></i> Machines Virtuelles</h3>
                <div class="resource-stat">
                    <span>Total:</span>
                    <strong>${data.vms.total}</strong>
                </div>
                <div class="resource-stat">
                    <span>En cours:</span>
                    <strong>${data.vms.running}</strong>
                </div>
            </div>
            
            <div class="resource-card">
                <h3><i class="fas fa-box"></i> Conteneurs LXC</h3>
                <div class="resource-stat">
                    <span>Total:</span>
                    <strong>${data.containers.total}</strong>
                </div>
                <div class="resource-stat">
                    <span>En cours:</span>
                    <strong>${data.containers.running}</strong>
                </div>
            </div>
        </div>
    `;
}

// Actions sur les déploiements
async function deleteDeployment(id) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce déploiement ?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/deployments/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('Déploiement supprimé', 'success');
            loadDeployments();
        } else {
            const data = await response.json();
            showNotification(`Erreur: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Erreur suppression:', error);
        showNotification('Erreur lors de la suppression', 'error');
    }
}

async function restartDeployment(id) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/deployments/${id}/restart`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showNotification('Déploiement redémarré', 'success');
            setTimeout(() => loadDeployments(), 2000);
        } else {
            const data = await response.json();
            showNotification(`Erreur: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Erreur redémarrage:', error);
        showNotification('Erreur lors du redémarrage', 'error');
    }
}

async function showLogs(id) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/deployments/${id}/logs`);
        const data = await response.json();
        
        alert(`Logs du déploiement ${id}:\n\n${data.deployment_log || 'Aucun log disponible'}`);
    } catch (error) {
        console.error('Erreur récupération logs:', error);
        showNotification('Erreur lors de la récupération des logs', 'error');
    }
}

// Utilitaires
function getStatusLabel(status) {
    const labels = {
        'pending': 'En attente',
        'creating': 'Création...',
        'running': 'En cours',
        'failed': 'Échoué',
        'stopped': 'Arrêté',
        'deleted': 'Supprimé'
    };
    return labels[status] || status;
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleString('fr-FR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function showNotification(message, type = 'info') {
    // Créer une notification simple
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        z-index: 9999;
        animation: slideIn 0.3s;
        background: ${type === 'success' ? 'var(--success-color)' : 
                     type === 'error' ? 'var(--danger-color)' : 
                     'var(--primary-color)'};
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Cleanup
window.addEventListener('beforeunload', () => {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});
