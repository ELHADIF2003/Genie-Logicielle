/**
 * Logique de la page graphiques.html
 * Génère 3 graphiques Chart.js alimentés par l'API.
 */

// Couleurs cohérentes avec la charte verte du projet
const COLORS = {
    primary: '#217346',
    primaryDark: '#0B572B',
    primaryLight: 'rgba(33, 115, 70, 0.5)',
    accent: '#5CB85C',
    grid: '#EAEFEA',
};

document.addEventListener('DOMContentLoaded', async () => {
    await Promise.all([
        loadCorrelationChart(),
        loadTopChart(),
        loadEvolutionChart(),
    ]);
    bindExportPDF();  // ← AJOUTE CETTE LIGNE
});


// ============================================================
// 1. SCATTER PLOT : Corrélation IPS × Taux de réussite
// ============================================================

async function loadCorrelationChart() {
    try {
        const points = await API.getCorrelation();

        const ctx = document.getElementById('chart-correlation');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Académies',
                    data: points.map(p => ({
                        x: p.ips,
                        y: p.taux_reussite,
                        nom: p.nomacademie,
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
// 2. BAR CHART : Top 5 académies par IPS
// ============================================================

async function loadTopChart() {
    try {
        const top = await API.getTopAcademies('ips', 5);

        const ctx = document.getElementById('chart-top');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: top.map(a => a.nomacademie),
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
                indexAxis: 'y', // barres horizontales
                plugins: {
                    legend: { display: false },
                },
                scales: {
                    x: {
                        title: { display: true, text: 'IPS' },
                        grid: { color: COLORS.grid },
                    },
                    y: {
                        grid: { display: false },
                    }
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

        new Chart(ctx, {
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
                plugins: {
                    legend: { position: 'top' },
                },
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

            // Titre du PDF
            pdf.setFontSize(20);
            pdf.setTextColor(11, 87, 43); // vert
            pdf.text('Rapport IDMC - EduData France', 20, 25);

            pdf.setFontSize(11);
            pdf.setTextColor(100, 100, 100);
            const date = new Date().toLocaleDateString('fr-FR');
            pdf.text(`Genere le ${date}`, 20, 33);

            // Capturer chaque graphique
            const charts = document.querySelectorAll('.chart-card');
            let yPos = 45;

            for (let i = 0; i < charts.length; i++) {
                const card = charts[i];

                // Nouvelle page si ça déborde
                if (yPos > 220 && i > 0) {
                    pdf.addPage();
                    yPos = 25;
                }

                // Capture en image avec html2canvas
                const canvas = await html2canvas(card, {
                    backgroundColor: '#ffffff',
                    scale: 1.5, // meilleure qualite
                });

                const imgData = canvas.toDataURL('image/png');
                const imgWidth = 170; // mm
                const imgHeight = (canvas.height * imgWidth) / canvas.width;

                pdf.addImage(imgData, 'PNG', 20, yPos, imgWidth, imgHeight);
                yPos += imgHeight + 10;
            }

            // Footer
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