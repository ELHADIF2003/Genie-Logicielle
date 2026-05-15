/**
 * Logique de la page connexion.html (Admin)
 * - Soumet le formulaire de login
 * - Stocke le JWT en localStorage
 * - Redirige vers le dashboard si succès
 */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    if (!form) return;

    // Si déjà connecté en tant qu'admin, rediriger direct vers le dashboard
    if (API.isAuthenticated()) {
        // On vérifie quand même que le token est encore valide
        API.getMe()
            .then(user => {
                if (user.role === 'admin') {
                    window.location.href = 'admin_dashboard.html';
                }
            })
            .catch(() => {
                // Token invalide → on le supprime, l'utilisateur doit se reconnecter
                API.logout();
            });
    }

    // Gestion du submit
    form.addEventListener('submit', async (e) => {
        e.preventDefault(); // empêche le rechargement de la page

        const email = emailInput.value.trim();
        const password = passwordInput.value;

        // Reset des erreurs précédentes
        clearError();

        try {
            // Étape 1 : login
            await API.login(email, password);

            // Étape 2 : vérifier que c'est bien un admin
            const user = await API.getMe();

            if (user.role !== 'admin') {
                API.logout();
                showError('Accès réservé aux administrateurs.');
                return;
            }

            // Étape 3 : redirection
            window.location.href = 'admin_dashboard.html';

        } catch (error) {
            showError(error.message || 'Email ou mot de passe incorrect.');
        }
    });
});


function showError(message) {
    let errorEl = document.querySelector('.login-error');
    if (!errorEl) {
        errorEl = document.createElement('p');
        errorEl.className = 'login-error';
        errorEl.style.cssText = 'color: #DC2626; text-align: center; margin-top: 1rem; font-size: 0.9rem;';
        const form = document.querySelector('form');
        if (form) form.appendChild(errorEl);
    }
    errorEl.textContent = '⚠️ ' + message;
}


function clearError() {
    const errorEl = document.querySelector('.login-error');
    if (errorEl) errorEl.remove();
}