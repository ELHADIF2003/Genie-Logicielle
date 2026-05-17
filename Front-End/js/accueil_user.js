/**
 * Logique de la page accueil_user.html
 * - KPI nationaux (avec filtre par année)
 * - 6 indicateurs détaillés
 * - Filtre Année fonctionnel
 */

document.addEventListener('DOMContentLoaded', async () => {
    bindYearFilter();
    bindRefreshButton();
    await loadNationalKPI();
});


// ============================================================
// FILTRE PAR ANNÉE
// ============================================================

function bindYearFilter() {
    const yearSelect = document.getElementById('filter-year');
    if (!yearSelect) return;

    // Recharger automatiquement quand l'année change
    yearSelect.addEventListener('change', async () => {
        await loadNationalKPI();
    });
}


function bindRefreshButton() {
    const btn = document.getElementById('btn-refresh');
    if (!btn) return;

    btn.addEventListener('click', async () => {
        btn.disabled = true;
        const originalText = btn.textContent;
        btn.textContent = '⏳ Chargement...';

        try {
            await loadNationalKPI();
        } finally {
            btn.disabled = false;
            btn.textContent = originalText;
        }
    });
}


// ============================================================
// CHARGEMENT DES KPI NATIONAUX
// ============================================================

async function loadNationalKPI() {
    try {
        // Récupérer l'année sélectionnée
        const yearSelect = document.getElementById('filter-year');
        const annee = yearSelect ? parseInt(yearSelect.value) : null;

        const data = await API.getNationalIndicators(annee);
        console.log('[accueil_user.js] KPI chargés pour', data.annee, ':', data);

        // === Mettre à jour le titre avec l'année ===
// === Mettre à jour le titre avec l'année ===
        const titre = document.getElementById('overview-title');
        if (titre) {
            titre.textContent = `Aperçu National (${data.annee})`;
        }

        // === KPI principaux du hero (3 cartes) ===
        setKPI('kpi-reussite', data.taux_reussite_national, ' %');
        setKPI('kpi-ips', data.ips_moyen_national, '');
        const nbAcadEl = document.getElementById('kpi-nb-acad');
        if (nbAcadEl) nbAcadEl.textContent = data.nb_academies;

        // === KPI détaillés (6 cartes) ===
        setKPI('kpi-mention', data.taux_mention_national, ' %');
        setKPI('kpi-echec', data.taux_echec_national, ' %');
        setKPI('kpi-ips-stddev', data.ips_ecart_type, '');
        setKPI('kpi-taux-f', data.taux_reussite_filles, ' %');
        setKPI('kpi-taux-m', data.taux_reussite_garcons, ' %');

        // Écart F/G : signe + couleur
        const ecartEl = document.getElementById('kpi-ecart-fg');
        if (ecartEl) {
            if (data.ecart_filles_garcons === null || data.ecart_filles_garcons === undefined) {
                ecartEl.textContent = 'N/A';
                ecartEl.style.color = '#666';
            } else {
                const v = data.ecart_filles_garcons;
                const signe = v > 0 ? '+' : '';
                ecartEl.textContent = `${signe}${v.toFixed(1)}`;
                ecartEl.style.color = v > 0 ? '#217346' : (v < 0 ? '#DC2626' : '#666');
            }
        }

    } catch (error) {
        console.error('Erreur chargement KPI :', error);
    }
}


function setKPI(elementId, value, suffix = '') {
    const el = document.getElementById(elementId);
    if (!el) return;
    if (value === null || value === undefined) {
        el.textContent = 'N/A';
    } else {
        el.textContent = value.toFixed(1) + suffix;
    }
}