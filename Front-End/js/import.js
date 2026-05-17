/**
 * Logique de la page import.html (Admin)
 * - Upload de fichier CSV via drag & drop ou sélection
 * - Affichage de l'aperçu avant import
 * - Import effectif via API
 */

let fileToUpload = null;

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

    console.log('[import.js] Page admin import chargée, branchement des handlers...');
    bindFileInput();
    bindDropZone();
    bindImportButton();
    bindLogout();
});


// ============================================================
// SÉLECTION DE FICHIER VIA "Parcourir les fichiers"
// ============================================================

function bindFileInput() {
    const input = document.getElementById('file-upload');
    if (!input) {
        console.error('[import.js] Input #file-upload introuvable !');
        return;
    }

    input.addEventListener('change', (e) => {
        console.log('[import.js] Changement détecté sur l\'input', e.target.files);
        if (e.target.files && e.target.files.length > 0) {
            fileToUpload = e.target.files[0];
            console.log('[import.js] Fichier sélectionné :', fileToUpload.name);
            updateFileTable();
        }
    });
}


// ============================================================
// DRAG & DROP
// ============================================================

function bindDropZone() {
    const dropZone = document.getElementById('drop-zone');
    if (!dropZone) return;

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.backgroundColor = '#E6F4EA';
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.style.backgroundColor = '';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.backgroundColor = '';

        if (e.dataTransfer.files.length > 0) {
            fileToUpload = e.dataTransfer.files[0];
            console.log('[import.js] Fichier déposé :', fileToUpload.name);
            updateFileTable();
        }
    });
}


// ============================================================
// AFFICHAGE DU FICHIER EN ATTENTE
// ============================================================

function updateFileTable() {
    const tbody = document.querySelector('.admin-table tbody');
    if (!tbody) {
        console.error('[import.js] Table tbody introuvable !');
        return;
    }
    if (!fileToUpload) return;

    const sizeMo = (fileToUpload.size / (1024 * 1024)).toFixed(2);

    tbody.innerHTML = `
        <tr>
            <td>${escapeHtml(fileToUpload.name)}</td>
            <td>${sizeMo} Mo</td>
            <td><span class="badge success">Prêt</span></td>
            <td><button type="button" class="btn-small action-delete" id="btn-clear-file">Retirer</button></td>
        </tr>
    `;

    // Rebinder le bouton "Retirer"
    const clearBtn = document.getElementById('btn-clear-file');
    if (clearBtn) {
        clearBtn.addEventListener('click', clearFile);
    }
}


function clearFile() {
    fileToUpload = null;
    const tbody = document.querySelector('.admin-table tbody');
    if (tbody) tbody.innerHTML = '';
    const input = document.getElementById('file-upload');
    if (input) input.value = '';
}


// ============================================================
// IMPORT (envoi au back-end)
// ============================================================

function bindImportButton() {
    const btn = document.querySelector('.action-footer .btn-validate');
    if (!btn) return;

    btn.addEventListener('click', async () => {
        if (!fileToUpload) {
            alert('Veuillez d\'abord sélectionner un fichier.');
            return;
        }

        const nomDataset = prompt('Nom du dataset :', fileToUpload.name.replace('.csv', ''));
        if (!nomDataset) return;

        btn.disabled = true;
        const originalText = btn.textContent;
        btn.textContent = '⏳ Import en cours...';

        try {
            const formData = new FormData();
            formData.append('file', fileToUpload);
            formData.append('nom_dataset', nomDataset);
            formData.append('source', 'upload_admin');

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
            alert(
                `✅ Import réussi !\n\n` +
                `Type détecté : ${result.type_detecte}\n` +
                `Lignes brutes : ${result.nb_lignes_brutes}\n` +
                `Lignes importées : ${result.nb_lignes_importees}\n` +
                `Académies : ${result.nb_academies}\n` +
                `Lycées : ${result.nb_lycees}\n` +
                `Résultats bac : ${result.nb_resultats_bac}`
            );
            clearFile();

        } catch (error) {
            alert('❌ Erreur lors de l\'import : ' + error.message);
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