/**
 * js/state.js
 * State Management and LocalStorage synchronization
 */

const AppState = {
    lastAnalysis: null, // Reset on reload
    repoIngested: localStorage.getItem('repo_ingested') === 'true',
    lastScreenshot: null, // Reset on reload
    lastAudio: null, // Reset on reload
    settings: {
        backendUrl: localStorage.getItem('backend_url') || 'http://localhost:8000',
        workspaceId: localStorage.getItem('workspace_id') || 'default'
    },

    save(key, value) {
        this[key] = value;
        const storageValue = typeof value === 'object' ? JSON.stringify(value) : value;
        localStorage.setItem(this.getStorageKey(key), storageValue);
    },

    getStorageKey(key) {
        const mapping = {
            'lastAnalysis': 'last_analysis',
            'repoIngested': 'repo_ingested',
            'lastScreenshot': 'last_screenshot',
            'lastAudio': 'last_audio',
            'settings': {
                'backendUrl': 'backend_url',
                'workspaceId': 'workspace_id'
            }
        };
        // Simplified for now, just direct mapping where possible
        if (key === 'repoIngested') return 'repo_ingested';
        if (key === 'lastAnalysis') return 'last_analysis';
        if (key === 'lastScreenshot') return 'last_screenshot';
        if (key === 'lastAudio') return 'last_audio';
        return key;
    },

    updateSettings(backendUrl, workspaceId) {
        this.settings.backendUrl = backendUrl;
        this.settings.workspaceId = workspaceId;
        localStorage.setItem('backend_url', backendUrl);
        localStorage.setItem('workspace_id', workspaceId);
    }
};

window.AppState = AppState;
