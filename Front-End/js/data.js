/**
 * Logique de la page data.html
 * Charge dynamiquement la liste des datasets depuis l'API.
 */

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const datasets = await API.getDatasetsPublics();
        renderDatasets(datasets);
    } catch (error) {
        console.error('Erreur chargement datasets :', error);
    }
});


function renderDatasets(datasets) {
    const catalog = document.querySelector('.data-catalog');
    if (!catalog) return;

    if (datasets.length === 0) {
        catalog.innerHTML = '<p class="text-muted text-center">Aucun dataset disponible.</p>';
        return;
    }

    // Vider et reconstruire
    catalog.innerHTML = '';

    datasets.forEach(ds => {
        const card = createDatasetCard(ds);
        catalog.appendChild(card);
    });
}


function createDatasetCard(ds) {
    // Date au format français
    let dateStr = 'Date inconnue';
    if (ds.dateimportation) {
        const d = new Date(ds.dateimportation);
        dateStr = d.toLocaleDateString('fr-FR', {
            day: 'numeric',
            month: 'long',
            year: 'numeric',
        });
    }

    // Icône selon le nom du dataset
    const icon = ds.nomdataset && ds.nomdataset.toLowerCase().includes('acad') ? '🗺️' : '📄';

    // Construction de la carte
    const card = document.createElement('div');
    card.className = 'dataset-card';
    card.innerHTML = `
        <div class="dataset-icon">${icon}</div>
        <div class="dataset-content">
            <h3>${escapeHtml(ds.nomdataset || 'Sans nom')}</h3>
            <p>Dataset importé depuis : <strong>${escapeHtml(ds.source || 'Source inconnue')}</strong></p>
            <div class="dataset-meta">
                <span class="meta-tag format-csv">CSV</span>
                <span class="meta-tag">Importé : ${dateStr}</span>
                <span class="meta-tag">État : ${escapeHtml(ds.etat || 'N/A')}</span>
                <span class="meta-tag">ID : ${ds.iddataset}</span>
            </div>
        </div>
        <div class="dataset-action">
            <a href="${API.getDownloadUrl(ds.iddataset)}" download class="btn-user-primary btn-download">                
            📥 Télécharger
            </a>
        </div>
    `;
    return card;
}


// Échappement HTML pour éviter les injections XSS
function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}