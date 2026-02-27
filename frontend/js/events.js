/**
 * js/events.js
 * Event handlers and interaction logic
 */

const Events = {
    bindGlobalEvents() {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const page = item.getAttribute('data-page');
                App.navigate(page);
            });
        });
    },

    bindPageEvents(pageId) {
        switch (pageId) {
            case 'code-analysis':
                this.bindCodeAnalysis();
                break;
            case 'screenshot-analysis':
                this.bindScreenshotAnalysis();
                break;
            case 'audio-transcription':
                this.bindAudioTranscription();
                break;
            case 'actions-fixes':
                this.bindActionsFixes();
                break;
            case 'settings':
                this.bindSettings();
                break;
            case 'history':
                this.bindHistory();
                break;
        }
    },

    bindCodeAnalysis() {
        const btnIngest = document.getElementById('btn-ingest');
        const btnAnalyze = document.getElementById('btn-analyze');

        btnIngest?.addEventListener('click', async () => {
            const path = document.getElementById('repo-path').value;
            if (!path) return alert("Please provide path");
            try {
                btnIngest.disabled = true;
                btnIngest.innerText = "Ingesting...";
                await SambaAPI.ingestCodebase(path, AppState.settings.workspaceId);

                AppState.save('repoIngested', true);
                localStorage.setItem('last_repo_path', path);

                alert("Ingestion started in background!");
                Router.renderPage('code-analysis');
            } catch (e) {
                alert(e.message);
                btnIngest.disabled = false;
                btnIngest.innerText = "📥 Ingest Repository";
            }
        });

        btnAnalyze?.addEventListener('click', async () => {
            const query = document.getElementById('ai-query').value;
            const type = document.getElementById('analysis-type').value;
            if (!query) return alert("Enter query");

            const resultsArea = document.getElementById('results-area');
            try {
                btnAnalyze.disabled = true;
                btnAnalyze.innerText = "Thinking...";
                resultsArea.innerHTML = '<div class="card" style="text-align:center"><div class="loader"></div><p style="margin-top:1rem">Analyzing with SambaNova...</p></div>';

                const res = await SambaAPI.analyze(query, type);
                const completeRes = { ...res, query, analysis_type: type };
                AppState.save('lastAnalysis', completeRes);

                resultsArea.innerHTML = UI.subTemplates.analysisResult(completeRes);
                btnAnalyze.disabled = false;
                btnAnalyze.innerText = "🚀 Run Analysis";
            } catch (e) {
                alert(e.message);
                btnAnalyze.disabled = false;
                btnAnalyze.innerText = "🚀 Run Analysis";
                resultsArea.innerHTML = '<div class="card">Error: ' + e.message + '</div>';
            }
        });
    },

    bindScreenshotAnalysis() {
        const fileInput = document.getElementById('ss-file');
        const btnAnalyze = document.getElementById('btn-analyze-ss');
        const dropZone = document.getElementById('drop-zone');

        dropZone?.addEventListener('click', () => fileInput.click());

        fileInput?.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                document.getElementById('file-name').innerText = file.name;
                const reader = new FileReader();
                reader.onload = (re) => {
                    document.getElementById('ss-preview').innerHTML = `<img src="${re.target.result}" style="max-width:100%; max-height:400px; border-radius:8px">`;
                };
                reader.readAsDataURL(file);
            }
        });

        btnAnalyze?.addEventListener('click', async () => {
            const file = fileInput.files[0];
            const context = document.getElementById('ss-context').value;
            if (!file) return alert("Choose an image");

            try {
                btnAnalyze.disabled = true;
                btnAnalyze.innerText = "Processing...";

                const res = await SambaAPI.ingestScreenshot(file, context);
                AppState.save('lastScreenshot', res);

                document.getElementById('ss-preview').innerHTML = UI.subTemplates.screenshotResult(res);
                btnAnalyze.disabled = false;
                btnAnalyze.innerText = "🚀 Analyze Screenshot";
            } catch (e) {
                alert(e.message);
                btnAnalyze.disabled = false;
                btnAnalyze.innerText = "🚀 Analyze Screenshot";
            }
        });
    },

    bindAudioTranscription() {
        const btnProcess = document.getElementById('btn-process-audio');
        btnProcess?.addEventListener('click', async () => {
            const fileInput = document.getElementById('audio-file');
            const participants = document.getElementById('audio-participants').value;
            const file = fileInput.files[0];
            if (!file) return alert("Choose audio file");

            try {
                btnProcess.disabled = true;
                btnProcess.innerText = "Transcribing...";

                const res = await SambaAPI.ingestAudio(file, participants);
                AppState.save('lastAudio', res);

                document.getElementById('audio-results-area').innerHTML = UI.subTemplates.audioResult(res);
                btnProcess.disabled = false;
                btnProcess.innerText = "🚀 Process Audio";
            } catch (e) {
                alert(e.message);
                btnProcess.disabled = false;
                btnProcess.innerText = "🚀 Process Audio";
            }
        });
    },

    bindActionsFixes() {
        const btnApply = document.getElementById('btn-apply-actions');
        btnApply?.addEventListener('click', async () => {
            const checks = document.querySelectorAll('.action-check:checked');
            const selectedActions = Array.from(checks).map(c => {
                const idx = c.getAttribute('data-idx');
                return AppState.lastAnalysis.suggested_actions[idx];
            });

            if (selectedActions.length === 0) return alert("Select at least one action");

            try {
                btnApply.disabled = true;
                btnApply.innerText = "Applying...";
                await SambaAPI.executeActions(selectedActions);
                alert("Actions executed successfully!");
                btnApply.innerText = "Applied";
            } catch (e) {
                alert("Execution failed: " + e.message);
                btnApply.disabled = false;
                btnApply.innerText = "Apply Selected Actions";
            }
        });
    },

    async bindHistory() {
        const listContainer = document.getElementById('history-list-container');
        const searchInput = document.getElementById('history-search');
        const typeFilter = document.getElementById('history-type-filter');
        const btnFilter = document.getElementById('btn-filter-history');

        let allEntries = [];

        const renderFiltered = () => {
            if (!listContainer) return;
            const query = searchInput?.value.toLowerCase() || "";
            const type = typeFilter?.value || "all";

            const filtered = allEntries.filter(e => {
                const matchQuery = e.query.toLowerCase().includes(query);
                const matchType = type === 'all' || e.type === type;
                return matchQuery && matchType;
            });

            listContainer.innerHTML = UI.subTemplates.historyList(filtered);
            if (window.lucide) lucide.createIcons();
        };

        try {
            allEntries = await SambaAPI.getHistory();
            renderFiltered();
        } catch (e) {
            if (listContainer) {
                listContainer.innerHTML = `<div class="card" style="color:var(--error)">Failed to load history: ${e.message}</div>`;
            }
        }

        btnFilter?.addEventListener('click', renderFiltered);
        searchInput?.addEventListener('input', renderFiltered);
    },

    async loadHistoryEntry(entryId) {
        try {
            const history = await SambaAPI.getHistory();
            const entry = history.find(e => e.id === entryId);
            if (!entry) return alert("Entry not found");

            // Load into state
            if (entry.type === 'code_analysis') {
                AppState.save('lastAnalysis', entry.data);
                App.navigate('code-analysis');
            } else if (entry.type === 'screenshot') {
                AppState.save('lastScreenshot', entry.data);
                App.navigate('screenshot-analysis');
            } else if (entry.type === 'audio') {
                AppState.save('lastAudio', entry.data);
                App.navigate('audio-transcription');
            }
        } catch (e) {
            alert("Failed to load history entry: " + e.message);
        }
    },

    bindSettings() {
        const btnSave = document.getElementById('btn-save-settings');
        btnSave?.addEventListener('click', () => {
            const url = document.getElementById('settings-url').value;
            const ws = document.getElementById('settings-workspace').value;
            AppState.updateSettings(url, ws);
            alert("Settings saved! Reloading...");
            location.reload();
        });

        const btnClear = document.getElementById('btn-clear-history');
        btnClear?.addEventListener('click', async () => {
            if (!confirm("Are you sure you want to clear ALL history? This cannot be undone.")) return;
            try {
                await SambaAPI.clearHistory();
                alert("History cleared!");
                location.reload();
            } catch (e) {
                alert("Failed to clear history: " + e.message);
            }
        });
    }
};

window.Events = Events;
