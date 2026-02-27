/**
 * js/api.js
 * Optimized Fetch-based client for SambaNova Code Agent Backend
 */

const API_BASE_URL = localStorage.getItem('backend_url') || 'http://localhost:8000';

const client = {
    async request(endpoint, method = 'GET', body = null, isFile = false) {
        const url = `${API_BASE_URL}${endpoint}`;
        const options = {
            method,
            headers: {}
        };

        if (body) {
            if (isFile) {
                // Let browser set boundary for FormData
                options.body = body;
            } else {
                options.headers['Content-Type'] = 'application/json';
                options.body = JSON.stringify(body);
            }
        }

        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || `HTTP Error ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`[API Error] ${endpoint}:`, error);
            throw error;
        }
    },

    // 1. Codebase Ingestion
    async ingestCodebase(repoPath, workspaceId = 'default') {
        return this.request('/ingest/codebase', 'POST', {
            repo_path: repoPath,
            workspace_id: workspaceId
        });
    },

    // 2. Chat / Code Analysis
    async analyze(query, analysisType = 'explain', includeCodebase = true) {
        return this.request('/analyze', 'POST', {
            query,
            analysis_type: analysisType,
            include_codebase: includeCodebase
        });
    },

    // 3. Screenshot Analysis
    async ingestScreenshot(imageFile, context = '') {
        const formData = new FormData();
        formData.append('file', imageFile);
        formData.append('context', context);
        return this.request('/ingest/screenshot', 'POST', formData, true);
    },

    // 4. Audio Ingestion
    async ingestAudio(audioFile, participants = '') {
        const formData = new FormData();
        formData.append('file', audioFile);
        formData.append('participants', participants);
        return this.request('/ingest/audio', 'POST', formData, true);
    },

    // 5. Action Execution
    async executeActions(actions) {
        return this.request('/actions/execute', 'POST', actions);
    },

    // 6. Health Check
    async checkHealth() {
        return this.request('/health');
    }
};

window.SambaAPI = client;
