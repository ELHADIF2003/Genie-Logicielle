/**
 * Module centralisé pour les appels à l'API back-end.
 * Gère l'URL de base, l'auth JWT, les erreurs.
 */

// === CONFIGURATION ===
const API_BASE_URL = 'http://localhost:8000';

// === STOCKAGE DU TOKEN JWT ===
const TOKEN_KEY = 'idmc_jwt_token';

function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
}

function isAuthenticated() {
    return getToken() !== null;
}

// === FONCTION FETCH GÉNÉRIQUE ===
async function apiFetch(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;

    // Headers par défaut
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    // Ajouter le JWT si présent
    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(url, { ...options, headers });

        if (!response.ok) {
            // Si 401, le token a expiré → on déconnecte
            if (response.status === 401) {
                clearToken();
            }
            const errorBody = await response.json().catch(() => ({}));
            throw new Error(errorBody.detail || `Erreur ${response.status}`);
        }

        // 204 No Content : pas de body
        if (response.status === 204) return null;

        return await response.json();
    } catch (error) {
        console.error(`[API] ${endpoint} :`, error.message);
        throw error;
    }
}

// === FONCTIONS HAUT NIVEAU ===

// --- Auth ---
async function login(email, password) {
    const data = await apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
    });
    setToken(data.access_token);
    return data;
}

async function getMe() {
    return await apiFetch('/auth/me');
}

function logout() {
    clearToken();
}

// --- Académies ---
async function getAcademies() {
    return await apiFetch('/academies/');
}

// --- Indicateurs ---
async function getNationalIndicators(annee = null) {
    const query = annee ? `?annee=${annee}` : '';
    return await apiFetch(`/indicateurs/national${query}`);
}

async function getAcademyIndicators(annee = null) {
    const query = annee ? `?annee=${annee}` : '';
    return await apiFetch(`/indicateurs/academies${query}`);
}

async function getComparateur(acadA, acadB, annee = null) {
    let url = `/indicateurs/comparateur?acad_a=${acadA}&acad_b=${acadB}`;
    if (annee) url += `&annee=${annee}`;
    return await apiFetch(url);
}

async function getCorrelation(annee = null) {
    const query = annee ? `?annee=${annee}` : '';
    return await apiFetch(`/indicateurs/correlation${query}`);
}

async function getEvolution() {
    return await apiFetch('/indicateurs/evolution');
}

async function getDatasetsPublics() {
    return await apiFetch('/indicateurs/datasets-publics');
}

async function getTopAcademies(critere = 'ips', n = 5, annee = null) {
    let url = `/indicateurs/top-academies?critere=${critere}&n=${n}`;
    if (annee) url += `&annee=${annee}`;
    return await apiFetch(url);
}

async function getRegions(annee = null) {
    const query = annee ? `?annee=${annee}` : '';
    return await apiFetch(`/indicateurs/regions${query}`);
}

async function getCorrelationRegions(annee = null) {
    const query = annee ? `?annee=${annee}` : '';
    return await apiFetch(`/indicateurs/correlation-regions${query}`);
}

async function getTopRegions(critere = 'ips', n = 5, annee = null) {
    let url = `/indicateurs/top-regions?critere=${critere}&n=${n}`;
    if (annee) url += `&annee=${annee}`;
    return await apiFetch(url);
}

// --- Admin ---
async function getAdminStats() {
    return await apiFetch('/admin/stats');
}

async function getDatasets() {
    return await apiFetch('/admin/datasets');
}

function getDownloadUrl(datasetId) {
    return `${API_BASE_URL}/indicateurs/datasets-publics/${datasetId}/download`;
}
// Exposer ces fonctions au scope global pour que les autres scripts les utilisent
window.API = {
    // Auth
    login, logout, getMe, isAuthenticated,
    // Public
    getAcademies,
    getNationalIndicators, getAcademyIndicators,
    getComparateur, getCorrelation, getEvolution, getTopAcademies,
    // Admin
    getAdminStats, getDatasets,
    getDatasetsPublics,getDownloadUrl,getRegions, getCorrelationRegions, getTopRegions,
};

