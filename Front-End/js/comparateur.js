/**
 * Logique de la page comparateur.html
 * - Charge les 2 selects avec les académies
 * - Compare 2 académies à chaque changement
 * - Lit le paramètre ?acad_a=X dans l'URL pour pré-sélectionner depuis la carte
 */

let academiesCache = [];

document.addEventListener('DOMContentLoaded', async () => {
    try {
        // 1. Charger les académies dans les 2 selects
        academiesCache = await API.getAcademies();
        const selects = document.querySelectorAll('.comparator-selectors .form-select');

        // Lire le paramètre URL (passé depuis la carte)
        const urlParams = new URLSearchParams(window.location.search);
        const preAcadA = urlParams.get('acad_a');
        const preAcadB = urlParams.get('acad_b');

        selects.forEach((select, index) => {
            select.innerHTML = '';
            academiesCache.forEach((acad, i) => {
                const option = document.createElement('option');
                option.value = acad.idacademie;
                option.textContent = acad.nomacademie;

                // Pré-sélection selon URL ou par défaut
                if (index === 0 && preAcadA && acad.idacademie == preAcadA) {
                    option.selected = true;
                } else if (index === 1 && preAcadB && acad.idacademie == preAcadB) {
                    option.selected = true;
                } else if (index === i && !preAcadA && !preAcadB) {
                    // Comportement par défaut : 1ère acad pour A, 2ème pour B
                    option.selected = true;
                }
                select.appendChild(option);
            });

            select.addEventListener('change', updateComparison);
        });

        await updateComparison();

    } catch (error) {
        console.error('Erreur initialisation comparateur :', error);
    }
});


async function updateComparison() {
    const selects = document.querySelectorAll('.comparator-selectors .form-select');
    const acadA = selects[0].value;
    const acadB = selects[1].value;

    if (!acadA || !acadB) return;

    try {
        const data = await API.getComparateur(acadA, acadB);
        renderComparison(data);
    } catch (error) {
        console.error('Erreur comparaison :', error);
    }
}


function renderComparison(data) {
    const rows = document.querySelectorAll('.comparison-row');
    if (rows.length < 2) return;

    const ipsA = data.academie_a.ipsmoyen || 0;
    const ipsB = data.academie_b.ipsmoyen || 0;
    const ipsMax = Math.max(ipsA, ipsB, 130);

    updateRow(rows[0], 'IPS', ipsA, ipsB, ipsMax, '');

    const tauxA = data.academie_a.taux_reussite || 0;
    const tauxB = data.academie_b.taux_reussite || 0;

    updateRow(rows[1], 'Taux de réussite au Bac', tauxA, tauxB, 100, ' %');
}


function updateRow(row, title, valA, valB, maxVal, suffix) {
    const titleEl = row.querySelector('.comp-title');
    if (titleEl) titleEl.textContent = title;

    const statVals = row.querySelectorAll('.stat-val');
    if (statVals.length >= 2) {
        statVals[0].textContent = valA.toFixed(1) + suffix;
        statVals[1].textContent = valB.toFixed(1) + suffix;
    }

    const bars = row.querySelectorAll('.bar');
    if (bars.length >= 2) {
        bars[0].style.width = `${(valA / maxVal) * 100}%`;
        bars[1].style.width = `${(valB / maxVal) * 100}%`;
    }
}