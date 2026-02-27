/**
 * js/router.js
 * SPA Routing and Page Rendering orchestration
 */

const Router = {
    container: null,

    init(containerId) {
        this.container = document.getElementById(containerId);
    },

    navigate(pageId) {
        // Update nav active states
        document.querySelectorAll('.nav-item').forEach(nav => {
            nav.classList.toggle('active', nav.getAttribute('data-page') === pageId);
        });

        this.renderPage(pageId);
    },

    renderPage(pageId) {
        if (!this.container) return;

        this.container.innerHTML = '';
        const pageElement = document.createElement('div');
        pageElement.className = 'page';

        const templateKey = this.kebabToCamel(pageId);
        const template = UI.templates[templateKey] || UI.templates.home;
        pageElement.innerHTML = template();

        this.container.appendChild(pageElement);

        // Bind page-specific events
        if (window.Events) Events.bindPageEvents(pageId);

        // Re-initialize icons
        if (window.lucide) lucide.createIcons();

        // Scroll to top
        window.scrollTo(0, 0);
    },

    kebabToCamel(str) {
        return str.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
    }
};

window.Router = Router;
