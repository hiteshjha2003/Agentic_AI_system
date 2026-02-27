/**
 * js/app.js
 * Optimized Entry Point for SambaNova Code Agent SPA
 */

const App = {
    init() {
        console.log("🚀 SambaNova Modular Frontend Initialized");

        // Initialize Core Components
        Router.init('page-content');
        Events.bindGlobalEvents();

        // Initial Route
        this.navigate('home');

        // Health Monitoring
        this.checkStatus();
        setInterval(() => this.checkStatus(), 10000);
    },

    navigate(pageId) {
        Router.navigate(pageId);
    },

    async checkStatus() {
        try {
            await SambaAPI.checkHealth();
            this.updateStatusUI(true);
        } catch (e) {
            this.updateStatusUI(false);
        }
    },

    updateStatusUI(online) {
        const statusEl = document.getElementById('connection-status');
        const dashStatus = document.getElementById('dash-status');

        const html = online
            ? '<div style="width: 8px; height: 8px; border-radius: 50%; background: var(--success); box-shadow: 0 0 10px var(--success);"></div><span>Online</span>'
            : '<div style="width: 8px; height: 8px; border-radius: 50%; background: var(--error); box-shadow: 0 0 10px var(--error);"></div><span>Offline</span>';

        if (statusEl) statusEl.innerHTML = html;
        if (dashStatus) dashStatus.innerHTML = html;
    }
};

window.App = App;
document.addEventListener('DOMContentLoaded', () => App.init());
