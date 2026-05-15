/**
 * Logique de la page admin_dashboard.html
 * - Vérifie que l'admin est connecté (sinon redirection vers login)
 * - Charge les stats et les datasets depuis l'API
 */

document.addEventListener('DOMContentLoaded', async () => {
    // === Protection de la route ===
    if (!API.isAuthenticated()) {
        window.location.href = 'connexion.html';
        return;
    }

    try {
        const user = await API.getMe();
        if (user.role !== 'admin') {
            API.logout();
            window.location.href = 'connexion.html';
            return;
        }
    } catch (error) {
        API.logout();
        window.location.href = 'connexion.html';
        return;
    }

    // === Chargement des données en parallèle ===
    await Promise.all([
        loadStats(),
        loadDatasets(),
    ]);

    // === Bouton de déconnexion ===
    bindLogout();
});


async function loadStats() {
    try {
        const stats = await API.getAdminStats();

        const kpiCards = document.querySelectorAll('.kpi-grid .kpi-card');
        if (kpiCards.length >= 4) {
            // Carte 1 : Serveur
            const c1 = kpiCards[0].querySelector('.status-text');
            if (c1) c1.textContent = 'Opérationnel';

            // Carte 2 : Base de données
            const c2 = kpiCards[1].querySelector('.status-text');
            if (c2) c2.textContent = 'Connectée';

            // Carte 3 : Total datasets (au lieu du "Taux d'import")
            const c3title = kpiCards[2].querySelector('h4');
            const c3value = kpiCards[2].querySelector('.status-text');
            if (c3title) c3title.textContent = 'Nombre de datasets';
            if (c3value) c3value.textContent = stats.nb_datasets;

            // Carte 4 : Total lycées (au lieu des "Anomalies")
            const c4title = kpiCards[3].querySelector('h4');
            const c4value = kpiCards[3].querySelector('.status-text');
            if (c4title) c4title.textContent = 'Total lycées';
            if (c4value) {
                c4value.textContent = stats.nb_lycees.toLocaleString('fr-FR');
                c4value.classList.remove('warning');
                c4value.classList.add('neutral');
            }
        }
    } catch (error) {
        console.error('Erreur chargement stats :', error);
    }
}


async function loadDatasets() {
    try {
        const datasets = await API.getDatasets();
        const tbody = document.querySelector('.admin-table tbody');
        if (!tbody) return;

        tbody.innerHTML = '';

        if (datasets.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:#666;">Aucun dataset importé.</td></tr>';
            return;
        }

        datasets.forEach(ds => {
            const row = document.createElement('tr');
            const date = ds.dateimportation
                ? new Date(ds.dateimportation).toLocaleDateString('fr-FR')
                : 'N/A';

            row.innerHTML = `
                <td>${escapeHtml(ds.nomdataset || 'Sans nom')}</td>
                <td><span class="badge ${ds.etat === 'valide' ? 'success' : 'warning'}">${escapeHtml(ds.etat || 'N/A')}</span></td>
                <td>${(ds.nb_lignes || 0).toLocaleString('fr-FR')}</td>
                <td>100 %</td>
                <td>0</td>
                <td>${date}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Erreur chargement datasets :', error);
    }
}


function bindLogout() {
    const logoutLink = document.querySelector('.sidebar-footer .back-home');
    if (logoutLink) {
        logoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            API.logout();
            window.location.href = 'connexion.html';
        });
    }
}


function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}