
/**
 * Logique de la page accueil_user.html
 * - Charge les KPI nationaux dans le hero
 * - Remplit le select des académies dynamiquement
 */

document.addEventListener('DOMContentLoaded', async () => {
    await Promise.all([
        loadNationalKPI(),
        loadAcademiesSelect(),
    ]);
});


async function loadNationalKPI() {
    try {
        const data = await API.getNationalIndicators();

        // Mettre à jour le titre de la section avec l'année réelle
        const titre = document.querySelector('.overview-section .section-title');
        if (titre) {
            titre.textContent = `Aperçu National (${data.annee})`;
        }

        // Mettre à jour les 3 KPI
        const kpiValues = document.querySelectorAll('.overview-section .kpi-value');
        if (kpiValues.length >= 3) {
            kpiValues[0].textContent = `${data.taux_reussite_national.toFixed(1)} %`;
            kpiValues[1].textContent = data.ips_moyen_national.toFixed(1);
            kpiValues[2].textContent = data.nb_academies;
        }
    } catch (error) {
        console.error('Erreur chargement KPI :', error);
    }
}


async function loadAcademiesSelect() {
    try {
        const academies = await API.getAcademies();

        // Le 2e select dans .global-filters (Académie)
        const select = document.querySelectorAll('.global-filters .form-select')[1];
        if (!select) return;

        // Vider et ajouter l'option "Toute la France" par défaut
        select.innerHTML = '<option value="">Toute la France</option>';

        // Ajouter chaque académie
        academies.forEach(acad => {
            const option = document.createElement('option');
            option.value = acad.idacademie;
            option.textContent = acad.nomacademie;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Erreur chargement académies :', error);
    }
}