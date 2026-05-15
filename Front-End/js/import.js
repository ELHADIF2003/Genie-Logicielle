/**
 * Logique de la page import.html (Admin)
 * - Upload de fichier CSV
 * - Affichage du résultat d'import
 */

let fileToUpload = null;

document.addEventListener('DOMContentLoaded', async () => {
    // Protection
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

    bindFileInput();
    bindDropZone();
    bindImportButton();
    bindLogout();
});


function bindFileInput() {
    const input = document.getElementById('file-upload');
    if (!input) return;

    input.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileToUpload = e.target.files[0];
            updateFileTable();
        }
    });
}


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
            updateFileTable();
        }
    });
}


function updateFileTable() {
    const tbody = document.querySelector('.admin-table tbody');
    if (!tbody || !fileToUpload) return;

    const sizeMo = (fileToUpload.size / (1024 * 1024)).toFixed(2);

    tbody.innerHTML = `
        <tr>
            <td>${escapeHtml(fileToUpload.name)}</td>
            <td>${sizeMo} Mo</td>
            <td><span class="badge success">Prêt</span></td>
            <td><button class="btn-small action-delete" onclick="clearFile()">Retirer</button></td>
        </tr>
    `;
}


function clearFile() {
    fileToUpload = null;
    const tbody = document.querySelector('.admin-table tbody');
    if (tbody) tbody.innerHTML = '';
    const input = document.getElementById('file-upload');
    if (input) input.value = '';
}


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
            btn.textContent = 'Lancer l\'importation de tous les fichiers';
        }
    });
}


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