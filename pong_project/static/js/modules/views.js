
const Views = {
    async initializeViewFromHash() {
        console.log('initializeViewFromHash');
        const hash = window.location.hash.substring(1) || 'core-home'; // Hash par défaut si vide
        const [app, view] = hash.split('-');
    
        // Si le hash est mal formé, rediriger vers la page par défaut
        if (!app || !view) {
            window.location.hash = '#core-home';
            return;
        }

        console.log(app, view);

        // Table de correspondance des vues avec importation dynamique
        const viewInitializers = {
            'core-home': async () => (await import('../landing/coreHome.js')).initializeHomeView(),
            'accounts-login': async () => (await import('../auth/index.js')).handleLogin(),
            'accounts-register': async () => (await import('../auth/index.js')).initializeRegisterView(),
            'accounts-gestion_profil': async () => (await import('../accountManagement/index.js')).handleAccountsManagement(),
            'accounts-enable_2fa': async () => (await import('../auth/index.js')).initializeEnable2FAView(),
            'accounts-verify_2fa_login': async () => (await import('../auth/index.js')).initializeLogin2FAView(),
            'accounts-disable_2fa': async () => (await import('../auth/index.js')).initializeDisable2FAView(),
            'game-invite_game': async () => (await import('../game/index.js')).initializeFriendInvitation(),
            'game-home': async () => (await import('../game/index.js')).initializeGameHomeView(),
			'game-select_tournament': async () => (await import('../game/index.js')).handleSeclectTournament(),
        };
    
        // Appeler l'initialisateur correspondant, ou ne rien faire par défaut
        const initializer = viewInitializers[`${app}-${view}`];
        console.log(initializer);
        if (initializer) await initializer();
        else console.error('Aucun initialisateur trouvé pour la vue', app, view);
        console.log('Fin de initializeViewFromHash');
    }
};

export default Views;