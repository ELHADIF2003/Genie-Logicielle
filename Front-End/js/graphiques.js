/**
 * Logique de la page graphiques.html
 * - 3 graphiques Chart.js (scatter, bar, line) alimentés par l'API
 * - Filtrable par niveau géographique (National / Régional)
 * - Export PDF
 */

const COLORS = {
    primary: '#217346',
    primaryDark: '#0B572B',
    primaryLight: 'rgba(33, 115, 70, 0.5)',
    accent: '#5CB85C',
    grid: '#EAEFEA',
};

// Stockage des instances Chart.js pour pouvoir les détruire avant recréation
let chartCorrelation = null;
let chartTop = null;
let chartEvolution = null;

// Niveau géographique courant ('national' ou 'regional')
let currentLevel = 'national';


document.addEventListener('DOMContentLoaded', async () => {
    bindLevelSelector();
    bindExportPDF();
    await loadAllCharts();
});


// ============================================================
// SELECTEUR DE NIVEAU GÉOGRAPHIQUE
// ============================================================

function bindLevelSelector() {
    const select = document.querySelector('.charts-toolbar .form-select');
    if (!select) {
        console.warn('[graphiques.js] Select niveau géographique introuvable.');
        return;
    }

    select.addEventListener('change', async (e) => {
        // Normaliser : minuscules + suppression des accents
        const value = e.target.value.toLowerCase()
            .normalize('NFD').replace(/[\u0300-\u036f]/g, '');
        currentLevel = value.includes('region') ? 'regional' : 'national';
        console.log('[graphiques.js] Niveau changé :', currentLevel);

        await loadAllCharts();
    });
}


async function loadAllCharts() {
    await Promise.all([
        loadCorrelationChart(),
        loadTopChart(),
        loadEvolutionChart(),
    ]);
}


// ============================================================
// 1. SCATTER PLOT : Corrélation IPS × Taux de réussite
// ============================================================

async function loadCorrelationChart() {
    try {
        const points = currentLevel === 'regional'
            ? await API.getCorrelationRegions()
            : await API.getCorrelation();

        const ctx = document.getElementById('chart-correlation');
        if (!ctx) return;

        if (chartCorrelation) chartCorrelation.destroy();

        chartCorrelation = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: currentLevel === 'regional' ? 'Régions' : 'Académies',
                    data: points.map(p => ({
                        x: p.ips,
                        y: p.taux_reussite,
                        nom: p.nomacademie || p.regionacademie,
                    })),
                    backgroundColor: COLORS.primary,
                    borderColor: COLORS.primaryDark,
                    pointRadius: 6,
                    pointHoverRadius: 8,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => {
                                const p = ctx.raw;
                                return `${p.nom} : IPS=${p.x}, Réussite=${p.y}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'IPS moyen' },
                        grid: { color: COLORS.grid },
                    },
                    y: {
                        title: { display: true, text: 'Taux de réussite (%)' },
                        grid: { color: COLORS.grid },
                    }
                }
            }
        });
    } catch (error) {
        console.error('Erreur scatter plot :', error);
    }
}


// ============================================================
// 2. BAR CHART : Top 5 (académies ou régions)
// ============================================================

async function loadTopChart() {
    try {
        const top = currentLevel === 'regional'
            ? await API.getTopRegions('ips', 5)
            : await API.getTopAcademies('ips', 5);

        const ctx = document.getElementById('chart-top');
        if (!ctx) return;

        if (chartTop) chartTop.destroy();

        // Titre dynamique du graphique
        const titre = ctx.closest('.chart-card')?.querySelector('h3');
        if (titre) {
            titre.textContent = currentLevel === 'regional'
                ? 'Top 5 des régions (IPS)'
                : 'Top 5 des académies (IPS)';
        }

        chartTop = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: top.map(a => a.nomacademie || a.regionacademie),
                datasets: [{
                    label: 'IPS moyen',
                    data: top.map(a => a.ipsmoyen),
                    backgroundColor: COLORS.primary,
                    borderColor: COLORS.primaryDark,
                    borderWidth: 1,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: { legend: { display: false } },
                scales: {
                    x: {
                        title: { display: true, text: 'IPS' },
                        grid: { color: COLORS.grid },
                    },
                    y: { grid: { display: false } }
                }
            }
        });
    } catch (error) {
        console.error('Erreur top chart :', error);
    }
}


// ============================================================
// 3. LINE CHART : Évolution nationale
// ============================================================

async function loadEvolutionChart() {
    try {
        const data = await API.getEvolution();
        const ctx = document.getElementById('chart-evolution');
        if (!ctx) return;

        if (chartEvolution) chartEvolution.destroy();

        chartEvolution = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.annee.toString()),
                datasets: [
                    {
                        label: 'Taux de réussite (%)',
                        data: data.map(d => d.taux_reussite),
                        borderColor: COLORS.primary,
                        backgroundColor: COLORS.primaryLight,
                        tension: 0.3,
                        fill: false,
                    },
                    {
                        label: 'Taux de mention (%)',
                        data: data.map(d => d.taux_mention),
                        borderColor: COLORS.primaryDark,
                        backgroundColor: 'rgba(11, 87, 43, 0.3)',
                        tension: 0.3,
                        fill: false,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'top' } },
                scales: {
                    x: {
                        title: { display: true, text: 'Année' },
                        grid: { color: COLORS.grid },
                    },
                    y: {
                        title: { display: true, text: 'Pourcentage' },
                        grid: { color: COLORS.grid },
                    }
                }
            }
        });
    } catch (error) {
        console.error('Erreur evolution chart :', error);
    }
}


// ============================================================
// EXPORT PDF
// ============================================================

function bindExportPDF() {
    const btn = document.querySelector('.charts-toolbar .btn-outline-user');
    if (!btn) return;

    btn.addEventListener('click', async () => {
        btn.disabled = true;
        btn.textContent = '⏳ Génération en cours...';

        try {
            const { jsPDF } = window.jspdf;
            const pdf = new jsPDF('p', 'mm', 'a4');

            pdf.setFontSize(20);
            pdf.setTextColor(11, 87, 43);
            pdf.text('Rapport IDMC - EduData France', 20, 25);

            pdf.setFontSize(11);
            pdf.setTextColor(100, 100, 100);
            const date = new Date().toLocaleDateString('fr-FR');
            pdf.text(`Genere le ${date}`, 20, 33);
            pdf.text(`Niveau : ${currentLevel === 'regional' ? 'Regional' : 'National'}`, 20, 39);

            const charts = document.querySelectorAll('.chart-card');
            let yPos = 50;

            for (let i = 0; i < charts.length; i++) {
                const card = charts[i];
                if (yPos > 220 && i > 0) {
                    pdf.addPage();
                    yPos = 25;
                }

                const canvas = await html2canvas(card, {
                    backgroundColor: '#ffffff',
                    scale: 1.5,
                });

                const imgData = canvas.toDataURL('image/png');
                const imgWidth = 170;
                const imgHeight = (canvas.height * imgWidth) / canvas.width;

                pdf.addImage(imgData, 'PNG', 20, yPos, imgWidth, imgHeight);
                yPos += imgHeight + 10;
            }

            pdf.setFontSize(9);
            pdf.setTextColor(150, 150, 150);
            pdf.text('Plateforme IDMC - M1 MIAGE - Universite de Lorraine', 20, 285);

            pdf.save(`IDMC-rapport-${date.replace(/\//g, '-')}.pdf`);

        } catch (error) {
            console.error('Erreur export PDF :', error);
            alert('Erreur lors de la génération du PDF : ' + error.message);
        } finally {
            btn.disabled = false;
            btn.textContent = '📥 Exporter ce rapport (PDF)';
        }
    });
}