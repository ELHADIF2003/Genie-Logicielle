/**
 * Logique de la page nettoyage.html (Admin)
 * - Upload de fichier CSV
 * - Aperçu des données brutes (5 premières lignes)
 * - Appel à l'API d'import (qui fait le nettoyage)
 * - Affichage des stats du nettoyage
 */

let fileToClean = null;

document.addEventListener('DOMContentLoaded', async () => {
    // === Protection admin ===
    if (!API.isAuthenticated()) {
        window.location.href = 'connexion.html';
        return;
    }
    try {
        const user = await API.getMe();
        if (user.role !== 'admin') {
            window.location.href = 'connexion.html';
            return;
        }
    } catch {
        window.location.href = 'connexion.html';
        return;
    }

    console.log('[nettoyage.js] Page admin nettoyage chargée');
    bindFileInput();
    bindLoadButton();
    bindCleanButton();
    bindLogout();
});


// ============================================================
// SÉLECTION DU FICHIER
// ============================================================

function bindFileInput() {
    const input = document.getElementById('dataset-upload');
    if (!input) return;

    input.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length > 0) {
            fileToClean = e.target.files[0];
            console.log('[nettoyage.js] Fichier choisi :', fileToClean.name);
        }
    });
}


function bindLoadButton() {
    // Bouton "Charger le fichier" dans l'étape 1
    const btn = document.querySelector('.row-upload .btn-action');
    if (!btn) return;

    btn.addEventListener('click', () => {
        if (!fileToClean) {
            alert('Veuillez d\'abord sélectionner un fichier CSV.');
            return;
        }
        previewFile(fileToClean);
    });
}


// ============================================================
// APERÇU DES 5 PREMIÈRES LIGNES
// ============================================================

function previewFile(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const content = e.target.result;
        // Découpe les 6 premières lignes (header + 5 lignes)
        const lines = content.split('\n').slice(0, 6).filter(l => l.trim() !== '');

        // Détecte le séparateur (',' ou ';')
        const sep = (lines[0].split(';').length > lines[0].split(',').length) ? ';' : ',';

        renderPreviewTable(lines, sep, '.preview-container .table-scroll');
    };
    reader.readAsText(file, 'UTF-8');
}


function renderPreviewTable(lines, sep, targetSelector) {
    if (lines.length === 0) return;

    const container = document.querySelector(targetSelector);
    if (!container) return;

    const headers = lines[0].split(sep).map(h => h.trim().replace(/^"|"$/g, ''));
    const rows = lines.slice(1).map(line =>
        line.split(sep).map(c => c.trim().replace(/^"|"$/g, ''))
    );

    // Limiter à 6 colonnes max pour pas exploser visuellement
    const MAX_COLS = 6;
    const limitedHeaders = headers.slice(0, MAX_COLS);
    const limitedRows = rows.map(r => r.slice(0, MAX_COLS));

    let html = '<table class="admin-table data-table"><thead><tr>';
    limitedHeaders.forEach(h => {
        html += `<th>${escapeHtml(h)}</th>`;
    });
    if (headers.length > MAX_COLS) {
        html += `<th>...</th>`;
    }
    html += '</tr></thead><tbody>';

    limitedRows.forEach(row => {
        html += '<tr>';
        limitedHeaders.forEach((_, i) => {
            html += `<td>${escapeHtml(row[i] || '')}</td>`;
        });
        if (headers.length > MAX_COLS) {
            html += `<td>...</td>`;
        }
        html += '</tr>';
    });
    html += '</tbody></table>';

    container.innerHTML = html;
}


// ============================================================
// LANCER LE NETTOYAGE (= import via API)
// ============================================================

function bindCleanButton() {
    const btn = document.querySelector('.action-center .btn-action');
    if (!btn) return;

    btn.addEventListener('click', async () => {
        if (!fileToClean) {
            alert('Veuillez d\'abord charger un fichier (étape 1).');
            return;
        }

        btn.disabled = true;
        const originalText = btn.textContent;
        btn.textContent = '⏳ Nettoyage en cours...';

        try {
            const formData = new FormData();
            formData.append('file', fileToClean);
            formData.append('nom_dataset', fileToClean.name.replace('.csv', '') + ' (nettoyé)');
            formData.append('source', 'admin_nettoyage');

            const response = await fetch('http://localhost:8000/admin/datasets/import', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('idmc_jwt_token')}`,
                },
                body: formData,
            });

            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                throw new Error(err.detail || `Erreur ${response.status}`);
            }

            const result = await response.json();
            console.log('[nettoyage.js] Stats reçues :', result);
            alert(
                `✅ Nettoyage terminé !\n\n` +
                `Type détecté : ${result.type_detecte}\n` +
                `Lignes brutes : ${result.nb_lignes_brutes}\n` +
                `Lignes importées : ${result.nb_lignes_importees}\n` +
                `Académies : ${result.nb_academies}\n` +
                `Lycées : ${result.nb_lycees}\n` +
                `Résultats bac : ${result.nb_resultats_bac}`
            );
            // Rediriger vers le dashboard pour voir le nouveau dataset
            setTimeout(() => {
                window.location.href = 'admin_dashboard.html';
            }, 300);

        } catch (error) {
            alert('❌ Erreur lors du nettoyage : ' + error.message);
        } finally {
            btn.disabled = false;
            btn.textContent = originalText;
        }
    });
}

// ============================================================
// DÉCONNEXION
// ============================================================

function bindLogout() {
    const logoutLink = document.querySelector('.btn-logout');
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