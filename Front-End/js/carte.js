/**
 * Logique de la page carte.html
 * - Carte Leaflet des académies
 * - Coloration selon l'indicateur choisi (IPS / Taux réussite / Mention)
 * - Filtrable par année
 * - Bouton "Comparer cette académie" qui redirige vers le comparateur
 */

let map = null;
let geoJsonLayer = null;
let geoJsonData = null;       // GeoJSON brut, gardé en mémoire pour redessiner
let indicateursMap = {};      // {nom_normalise: indicateurs}
let academieSelectionnee = null; // {id, nom} pour le bouton "Comparer"

// Indicateur actif (clé dans les données API)
let indicateurActif = 'ipsmoyen'; // ou 'taux_reussite' ou 'taux_mention'

// Configuration des indicateurs disponibles
const INDICATEURS = {
    ipsmoyen: {
        label: 'IPS',
        unit: '',
        thresholds: [95, 100, 105, 115],  // bornes pour les couleurs
        legendLow: '< 90',
        legendHigh: '> 120',
    },
    taux_reussite: {
        label: 'Taux de réussite',
        unit: ' %',
        thresholds: [85, 90, 93, 96],
        legendLow: '< 85 %',
        legendHigh: '> 96 %',
    },
    taux_mention: {
        label: 'Taux de mention',
        unit: ' %',
        thresholds: [45, 55, 65, 75],
        legendLow: '< 45 %',
        legendHigh: '> 75 %',
    },
};


document.addEventListener('DOMContentLoaded', async () => {
    initMap();
    bindControls();
    await loadGeoJson();
    await loadIndicateurs(); // utilise l'année par défaut (la plus récente)
});


// ============================================================
// INITIALISATION DE LA CARTE
// ============================================================

function initMap() {
    map = L.map('map-leaflet').setView([46.6, 2.5], 6);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '© OpenStreetMap, © CARTO',
        maxZoom: 18,
    }).addTo(map);
}


// ============================================================
// CHARGEMENT DES DONNÉES
// ============================================================

async function loadGeoJson() {
    try {
        const response = await fetch('../data/academies.geojson');
        geoJsonData = await response.json();
    } catch (error) {
        console.error('Erreur chargement GeoJSON :', error);
    }
}


async function loadIndicateurs(annee = null) {
    try {
        const data = await API.getAcademyIndicators(annee);

        // Reconstruire le dict {nom_normalise: indicateurs}
        indicateursMap = {};
        data.forEach(acad => {
            const key = normalizeName(acad.nomacademie);
            indicateursMap[key] = acad;
        });

        // Redessiner la carte avec ces données
        redrawMap();

    } catch (error) {
        console.error('Erreur chargement indicateurs :', error);
    }
}


// ============================================================
// CONTRÔLES (selects, bouton)
// ============================================================

function bindControls() {
    const selects = document.querySelectorAll('.map-sidebar .form-select');

    // Select 1 : Indicateur affiché
    if (selects[0]) {
        selects[0].addEventListener('change', (e) => {
            const idx = e.target.selectedIndex;
            // Mapping des index vers les clés de notre API
            const mapping = ['ipsmoyen', 'taux_reussite', 'taux_mention'];
            indicateurActif = mapping[idx] || 'ipsmoyen';
            redrawMap();
            updateLegend();
        });
    }

    // Select 2 : Année
    if (selects[1]) {
        selects[1].addEventListener('change', async (e) => {
            // "2023 - 2024" => 2024 ; "2022 - 2023" => 2023
            const text = e.target.value;
            const match = text.match(/(\d{4})\s*$/); // capture l'année finale
            const annee = match ? parseInt(match[1]) : null;
            await loadIndicateurs(annee);
        });
    }

    // Bouton "Comparer cette académie"
    const btn = document.querySelector('.selected-academy-card .btn-outline-user');
    if (btn) {
        btn.addEventListener('click', () => {
            if (!academieSelectionnee) {
                alert('Veuillez d\'abord cliquer sur une académie sur la carte.');
                return;
            }
            // Redirection avec paramètre URL
            window.location.href = `comparateur.html?acad_a=${academieSelectionnee.id}`;
        });
    }
}


// ============================================================
// REDRAW DE LA CARTE
// ============================================================

function redrawMap() {
    if (!geoJsonData) return;

    if (geoJsonLayer) {
        map.removeLayer(geoJsonLayer);
    }

    geoJsonLayer = L.geoJSON(geoJsonData, {
        style: featureStyle,
        onEachFeature: bindFeatureEvents,
    }).addTo(map);

    updateLegend();
}


// ============================================================
// STYLE DES POLYGONES (couleur selon indicateur actif)
// ============================================================

function getColor(value, indicateur) {
    if (value === null || value === undefined) return '#CCCCCC';

    const cfg = INDICATEURS[indicateur];
    const t = cfg.thresholds; // ex: [95, 100, 105, 115]

    if (value >= t[3]) return '#0B572B';
    if (value >= t[2]) return '#217346';
    if (value >= t[1]) return '#5CB85C';
    if (value >= t[0]) return '#A8D5BA';
    return '#E6F4EA';
}


function featureStyle(feature) {
    const nomAcad = getFeatureName(feature);
    const acad = indicateursMap[normalizeName(nomAcad)];
    const value = acad ? acad[indicateurActif] : null;

    return {
        fillColor: getColor(value, indicateurActif),
        weight: 1.5,
        opacity: 1,
        color: 'white',
        fillOpacity: 0.85,
    };
}


function getFeatureName(feature) {
    const props = feature.properties || {};
    return props.aca_nom || props.nom_aca || props.libelle ||
           props.NOM || props.name || props.nom || '';
}


// ============================================================
// ÉVÉNEMENTS SUR LES ACADÉMIES (hover, click, popup)
// ============================================================

function bindFeatureEvents(feature, layer) {
    const nomAcad = getFeatureName(feature);
    const acad = indicateursMap[normalizeName(nomAcad)];

    let popupContent = `<strong>${nomAcad}</strong><br>`;
    if (acad) {
        popupContent += `IPS : <strong>${acad.ipsmoyen?.toFixed(1) ?? 'N/A'}</strong><br>`;
        popupContent += `Réussite : <strong>${acad.taux_reussite?.toFixed(1) ?? 'N/A'} %</strong><br>`;
        popupContent += `Mention : <strong>${acad.taux_mention?.toFixed(1) ?? 'N/A'} %</strong>`;
    } else {
        popupContent += '<em>Données indisponibles</em>';
    }
    layer.bindPopup(popupContent);

    layer.on({
        mouseover: (e) => {
            e.target.setStyle({ weight: 3, color: '#0B572B' });
        },
        mouseout: (e) => {
            geoJsonLayer.resetStyle(e.target);
        },
        click: (e) => {
            map.fitBounds(e.target.getBounds());
            updateSidebar(nomAcad, acad);
        }
    });
}


// ============================================================
// MISE À JOUR DE LA SIDEBAR AU CLIC
// ============================================================

function updateSidebar(nomAcad, acad) {
    const nameEl = document.querySelector('.academy-name');
    const statRows = document.querySelectorAll('.stat-row strong');

    if (nameEl) nameEl.textContent = nomAcad;

    if (statRows.length >= 2 && acad) {
        statRows[0].textContent = acad.ipsmoyen?.toFixed(1) ?? 'N/A';
        statRows[1].textContent = (acad.taux_reussite?.toFixed(1) ?? 'N/A') + ' %';
    } else if (statRows.length >= 2) {
        statRows[0].textContent = 'N/A';
        statRows[1].textContent = 'N/A';
    }

    // Mémoriser pour le bouton "Comparer cette académie"
    if (acad) {
        academieSelectionnee = { id: acad.idacademie, nom: nomAcad };
    } else {
        academieSelectionnee = null;
    }
}


// ============================================================
// MISE À JOUR DE LA LÉGENDE (en bas à droite)
// ============================================================

function updateLegend() {
    const cfg = INDICATEURS[indicateurActif];
    const legendTitle = document.querySelector('.map-legend h4');
    const labels = document.querySelectorAll('.legend-labels span');

    if (legendTitle) {
        legendTitle.textContent = `Légende (${cfg.label})`;
    }

    if (labels.length >= 2) {
        labels[0].textContent = cfg.legendLow;
        labels[1].textContent = cfg.legendHigh;
    }
}


// ============================================================
// UTILS
// ============================================================

function normalizeName(name) {
    if (!name) return '';
    return name
        .toUpperCase()
        .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
        .replace(/[\s\-']/g, '');
}