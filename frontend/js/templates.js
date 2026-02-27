/**
 * js/templates.js
 * HTML Page Templates for the SPA
 */

const UI = {
    templates: {
        home: () => `
            <header>
                <h1>Welcome to SambaNova</h1>
                <p class="subtitle">AI-powered multimodal code companion.</p>
            </header>
            
            <div class="card" style="background: var(--accent-gradient); text-align: center; color: white; border: none;">
                <h2 style="font-size: 2.2rem; margin-bottom: 1rem;">Analyze smarter. Build better.</h2>
                <p style="opacity: 0.9; font-size: 1.1rem;">Code, screenshots, audio meetings — all in one unified workspace.</p>
            </div>

            <div class="grid-3">
                <div class="card clickable" onclick="App.navigate('code-analysis')">
                    <i data-lucide="search" style="color: var(--accent-primary); width: 32px; height:32px; margin-bottom: 1rem;"></i>
                    <h3>Code Analysis</h3>
                    <p style="font-size: 0.9rem; color: var(--text-muted); margin: 0.5rem 0 1.5rem 0;">Debug, review, explain, and refactor your repository.</p>
                    <button class="btn btn-secondary" style="width:100%">Open</button>
                </div>
                <div class="card clickable" onclick="App.navigate('screenshot-analysis')">
                    <i data-lucide="camera" style="color: var(--accent-secondary); width: 32px; height:32px; margin-bottom: 1rem;"></i>
                    <h3>Screenshot</h3>
                    <p style="font-size: 0.9rem; color: var(--text-muted); margin: 0.5rem 0 1.5rem 0;">Upload error screens or UI designs for visual debugging.</p>
                    <button class="btn btn-secondary" style="width:100%">Open</button>
                </div>
                <div class="card clickable" onclick="App.navigate('audio-transcription')">
                    <i data-lucide="mic" style="color: var(--success); width: 32px; height:32px; margin-bottom: 1rem;"></i>
                    <h3>Audio Discussion</h3>
                    <p style="font-size: 0.9rem; color: var(--text-muted); margin: 0.5rem 0 1.5rem 0;">Transcribe meetings and extract action items instantly.</p>
                    <button class="btn btn-secondary" style="width:100%">Open</button>
                </div>
            </div>
            
            <div class="card">
                <div style="display:flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3>🚀 Recent Activity</h3>
                        <p class="subtitle">Quick access to your latest results.</p>
                    </div>
                    <button class="btn btn-primary" onclick="App.navigate('analysis')">Dashboard →</button>
                </div>
            </div>
        `,

        analysis: () => {
            const last = AppState.lastAnalysis;
            return `
            <header>
                <h1>📊 Analysis Dashboard</h1>
                <p class="subtitle">Central overview of all recent analyses.</p>
            </header>
            
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 2rem;">
                <div class="left-col">
                    <h3 style="margin-bottom: 1.5rem;">Latest Results</h3>
                    
                    <div class="card">
                        <div style="display:flex; justify-content:space-between;">
                            <div>
                                <h4 style="display:flex; align-items:center; gap:8px;">
                                    <i data-lucide="search" style="color:var(--accent-primary)"></i> Code Analysis
                                </h4>
                                <div style="margin-top:1rem">
                                    ${last ? `
                                        <p><strong>Query:</strong> ${last.query || '—'}</p>
                                        <p style="margin-top:0.5rem; color:var(--text-dim); overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">
                                            ${last.summary}
                                        </p>
                                    ` : '<p style="color:var(--text-muted)">No recent code analysis.</p>'}
                                </div>
                            </div>
                            ${last ? `<button class="btn btn-secondary" onclick="App.navigate('code-analysis')">Details</button>` : ''}
                        </div>
                    </div>

                    <div class="card">
                        <div style="display:flex; justify-content:space-between;">
                            <div>
                                <h4 style="display:flex; align-items:center; gap:8px;">
                                    <i data-lucide="camera" style="color:var(--accent-secondary)"></i> Screenshot Analysis
                                </h4>
                                <div style="margin-top:1rem">
                                    ${AppState.lastScreenshot ? `
                                        <p><strong>Processed:</strong> ${new Date().toLocaleDateString()}</p>
                                        <p style="margin-top:0.5rem; color:var(--text-dim)">Visual analysis complete.</p>
                                    ` : '<p style="color:var(--text-muted)">No recent screenshots.</p>'}
                                </div>
                            </div>
                            ${AppState.lastScreenshot ? `<button class="btn btn-secondary" onclick="App.navigate('screenshot-analysis')">Details</button>` : ''}
                        </div>
                    </div>
                </div>

                <div class="right-col">
                    <h3 style="margin-bottom: 1.5rem;">System Health</h3>
                    <div class="card" style="padding:1.5rem">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span>Backend</span>
                            <div id="dash-status" style="display:flex; align-items:center; gap:8px">
                                <div style="width:10px; height:10px; border-radius:50%; background:var(--success)"></div>
                                <span>Online</span>
                            </div>
                        </div>
                        <div style="margin-top:1.5rem; padding-top:1.5rem; border-top:1px solid var(--border-subtle)">
                            <p style="font-size:0.85rem; color:var(--text-dim)">Workspace: <span style="color:var(--text-bright)">${AppState.settings.workspaceId}</span></p>
                            <p style="font-size:0.85rem; color:var(--text-dim); margin-top:0.5rem">Agent: <span style="color:var(--text-bright)">SambaNova-Orchestrator</span></p>
                        </div>
                    </div>
                </div>
            </div>
            `;
        },

        codeAnalysis: () => `
            <header>
                <h1>🔍 Code Analysis</h1>
                <p class="subtitle">Analyze your repository with SambaNova AI.</p>
            </header>
            
            <div class="card">
                <h3>1. Ingest Codebase</h3>
                <div class="input-group" style="margin-top:1.5rem">
                    <label class="input-label">Project Absolute Path</label>
                    <div style="display:flex; gap:1rem">
                        <input type="text" id="repo-path" placeholder="/Users/name/projects/my-app" style="flex:1" value="${localStorage.getItem('last_repo_path') || ''}">
                        <button class="btn btn-primary" id="btn-ingest">📥 Ingest Repository</button>
                    </div>
                    <p style="font-size: 0.75rem; color:var(--text-dim); margin-top:0.5rem">
                        ${AppState.repoIngested ? '✅ Repository already ingested for this session' : '⚠️ Ingestion required before analysis'}
                    </p>
                </div>
            </div>

            <div class="grid-2" style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top:2rem">
                <div class="card">
                    <h3>2. Run Analysis</h3>
                    <div class="input-group" style="margin-top:1.5rem">
                        <label class="input-label">AI Agent Query</label>
                        <textarea id="ai-query" placeholder="e.g., 'Explain the authentication flow' or 'Find memory leaks in the loop'" style="height:120px"></textarea>
                    </div>
                    <div class="input-group">
                        <label class="input-label">Analysis Type</label>
                        <select id="analysis-type">
                            <option value="explain">Explain Code</option>
                            <option value="review">Bug Discovery / Review</option>
                            <option value="debug">Debug Specific Issue</option>
                            <option value="refactor">Suggest Refactoring</option>
                        </select>
                    </div>
                    <button class="btn btn-primary" id="btn-analyze" style="width:100%">🚀 Run Analysis</button>
                </div>
                
                <div id="results-area">
                    <!-- Results Load Here -->
                    ${AppState.lastAnalysis ? UI.subTemplates.analysisResult(AppState.lastAnalysis) : '<div class="card" style="height:100%; display:flex; align-items:center; justify-content:center; color:var(--text-dim)">Run an analysis to see results</div>'}
                </div>
            </div>
        `,

        screenshotAnalysis: () => `
            <header>
                <h1>📸 Screenshot Analysis</h1>
                <p class="subtitle">Visual visual debugging for UI issues and error screens.</p>
            </header>
            <div class="grid-2" style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                <div class="card">
                    <h3>Upload Image</h3>
                    <div class="file-upload-area" id="drop-zone" style="margin-top:1.5rem; height: 200px; border: 2px dashed var(--border-subtle); border-radius:12px; display:flex; flex-direction:column; align-items:center; justify-content:center; cursor:pointer">
                        <i data-lucide="upload-cloud" style="width:40px; height:40px; color:var(--text-dim)"></i>
                        <p style="margin-top:1rem">Click or drag image here</p>
                        <span id="file-name" style="font-size:0.8rem; color:var(--accent-primary); margin-top:0.5rem"></span>
                        <input type="file" id="ss-file" hidden accept="image/*">
                    </div>
                    
                    <div class="input-group" style="margin-top:1.5rem">
                        <label class="input-label">Describe Context (Optional)</label>
                        <textarea id="ss-context" placeholder="What should I look for?" style="height:80px"></textarea>
                    </div>
                    
                    <button class="btn btn-primary" id="btn-analyze-ss" style="width:100%">🚀 Analyze Screenshot</button>
                </div>
                
                <div id="ss-results-area">
                    <div class="card" style="min-height:300px">
                        <h3>Preview</h3>
                        <div id="ss-preview" style="margin-top:1.5rem; text-align:center">
                             ${AppState.lastScreenshot ? UI.subTemplates.screenshotResult(AppState.lastScreenshot) : '<p style="color:var(--text-dim)">Upload an image to start</p>'}
                        </div>
                    </div>
                </div>
            </div>
        `,

        audioTranscription: () => `
            <header>
                <h1>🎙️ Audio Transcription</h1>
                <p class="subtitle">Extract action items from meeting recordings.</p>
            </header>
            <div class="card">
                <div class="grid-2" style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                    <div>
                        <h3>Meeting Recording</h3>
                        <div class="input-group" style="margin-top:1.5rem">
                            <label class="input-label">Choose Audio File (WAV/MP3)</label>
                            <input type="file" id="audio-file" accept="audio/*">
                        </div>
                        <div class="input-group">
                            <label class="input-label">Meeting Participants</label>
                            <input type="text" id="audio-participants" placeholder="e.g. Alice, Bob, Charlie">
                        </div>
                        <button class="btn btn-primary" id="btn-process-audio" style="width:100%">🚀 Process Audio</button>
                    </div>
                    <div id="audio-results-area">
                         ${AppState.lastAudio ? UI.subTemplates.audioResult(AppState.lastAudio) : '<div style="height:100%; display:flex; align-items:center; justify-content:center; color:var(--text-dim)">Results will appear here</div>'}
                    </div>
                </div>
            </div>
        `,

        actionsFixes: () => `
            <header>
                <h1>🔧 Actions & Fixes</h1>
                <p class="subtitle">Review and apply AI-suggested improvements.</p>
            </header>
            
            <div id="actions-container">
                ${AppState.lastAnalysis ? UI.subTemplates.actionsList(AppState.lastAnalysis.suggested_actions) : UI.subTemplates.noActions()}
            </div>
        `,

        settings: () => `
            <header>
                <h1>⚙️ Settings</h1>
                <p class="subtitle">Configure your SambaNova Code Agent environment.</p>
            </header>
            <div class="grid-2" style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                <div class="card">
                    <h3>Backend Configuration</h3>
                    <div class="input-group" style="margin-top:1.5rem">
                        <label class="input-label">FastAPI Backend URL</label>
                        <input type="text" id="settings-url" value="${AppState.settings.backendUrl}">
                    </div>
                    <div class="input-group">
                        <label class="input-label">Workspace ID</label>
                        <input type="text" id="settings-workspace" value="${AppState.settings.workspaceId}">
                    </div>
                    <button class="btn btn-primary" id="btn-save-settings" style="width:100%">Save Configuration</button>
                </div>
                
                <div class="card">
                    <h3>Environment Info</h3>
                    <div style="padding:1rem; background:rgba(0,0,0,0.2); border-radius:8px; font-family:'JetBrains Mono'; font-size:0.85rem; color:var(--text-muted)">
                        <p>OS: Mac</p>
                        <p>Core: FastAPI 0.100+</p>
                        <p>Analysis: SambaNova Cloud</p>
                        <p>UI Version: 2.1 (Modular SPA)</p>
                    </div>
                </div>
            </div>
        `
    },

    subTemplates: {
        analysisResult: (res) => `
            <div class="card markdown-content">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h2>Analysis Result</h2>
                    <button class="btn btn-secondary" onclick="App.navigate('actions-fixes')">View Suggested Actions →</button>
                </div>
                <div style="margin-top:2rem">
                    <h4 style="color:var(--accent-primary)">Executive Summary</h4>
                    <p style="margin-top:0.5rem">${res.summary}</p>
                    
                    <h4 style="margin-top:2rem; border-bottom:1px solid var(--border-subtle); padding-bottom:0.5rem">Detailed Report</h4>
                    <div style="margin-top:1rem; white-space: pre-wrap; font-family: 'Inter';">${res.detailed_analysis}</div>
                    
                    <h4 style="margin-top:2rem;">Relevant Code Context</h4>
                    <div style="margin-top:1rem; display:flex; flex-direction:column; gap:1rem">
                        ${(res.relevant_contexts || []).map(c => `
                            <div style="padding:1rem; background:#0f172a; border-radius:8px; border:1px solid var(--border-subtle)">
                                <div style="font-size:0.75rem; color:var(--accent-primary); margin-bottom:0.5rem;">${c.source}</div>
                                <pre style="margin:0; padding:0; background:transparent; border:none; font-size:0.85rem">${c.content.substring(0, 300)}...</pre>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `,

        screenshotResult: (res) => {
            const vision = res.analysis.vision_analysis || {};
            const analysis = res.analysis || {};
            return `
            <div class="markdown-content">
                <h3 style="color:var(--success)">Processed Successfully</h3>
                
                <div style="margin-top:2rem; text-align:left">
                    <h4>📝 Extracted Text</h4>
                    <div style="background:#0f172a; padding:1rem; border-radius:8px; margin-top:0.5rem; font-family:'JetBrains Mono'; font-size:0.8rem">
                        ${vision.extracted_text || 'None'}
                    </div>
                    
                    <h4 style="margin-top:2rem">📖 Detailed Explanation</h4>
                    <p style="margin-top:0.5rem">${analysis.detailed_explanation || 'None'}</p>
                    
                    <h4 style="margin-top:2rem">🏗️ Architectural Components</h4>
                    <div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:0.5rem">
                        ${(analysis.architectural_components || []).map(c => `<span style="background:rgba(99,102,241,0.1); color:var(--accent-primary); padding:4px 12px; border-radius:100px; font-size:0.8rem">${c}</span>`).join('')}
                    </div>
                </div>
            </div>
            `;
        },

        audioResult: (res) => `
            <div class="markdown-content" style="text-align:left">
                <h3 style="color:var(--success)">Transcription Complete</h3>
                <div style="margin-top:2rem">
                    <h4>📝 Transcription</h4>
                    <p style="margin-top:0.5rem">${res.transcription || 'None'}</p>
                    
                    <h4 style="margin-top:2rem">🛠️ Detected Action Items</h4>
                    <div style="margin-top:0.5rem">
                        ${(res.action_items || []).map(item => `
                            <div style="padding:1rem; background:rgba(255,255,255,0.03); border-radius:8px; margin-bottom:0.5rem; border-left:4px solid var(--accent-primary)">
                                <p>${item.text}</p>
                                <span style="font-size:0.75rem; color:var(--text-dim)">Confidence: ${item.confidence}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `,

        actionsList: (actions) => {
            if (!actions || actions.length === 0) return UI.subTemplates.noActions();
            return `
                <div class="card">
                    <h3>Suggested Improvements</h3>
                    <p class="subtitle">Select the ones you'd like to apply.</p>
                    
                    <div style="margin-top:2rem">
                        ${actions.map((act, idx) => `
                            <div class="action-item" style="display:flex; gap:1.5rem; padding:1.5rem; background:rgba(255,255,255,0.03); border-radius:12px; margin-bottom:1rem; border:1px solid var(--border-subtle)">
                                <input type="checkbox" class="action-check" data-idx="${idx}" style="width:20px; height:20px; margin-top:4px">
                                <div style="flex:1">
                                    <div style="display:flex; justify-content:space-between;">
                                        <h4 style="color:var(--accent-primary)">${act.action_type.toUpperCase()}</h4>
                                        <span class="badge" style="background:rgba(99,102,241,0.1); color:var(--accent-primary); padding:2px 8px; border-radius:100px; font-size:0.75rem">${act.target_file}</span>
                                    </div>
                                    <p style="margin-top:0.5rem; font-size:0.95rem">${act.description}</p>
                                    ${act.reasoning ? `<p style="margin-top:0.5rem; color:var(--text-dim); font-size:0.85rem"><em>Reasoning: ${act.reasoning}</em></p>` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    
                    <button class="btn btn-primary" id="btn-apply-actions" style="margin-top:1rem; width:100%">Apply Selected Actions</button>
                </div>
            `;
        },

        noActions: () => `
            <div class="card" style="text-align:center; padding:4rem">
                <i data-lucide="check-circle" style="width:48px; height:48px; color:var(--success); margin-bottom:1rem"></i>
                <h3>No Recent Actions</h3>
                <p style="color:var(--text-dim)">Run a code analysis to get suggested improvements.</p>
                <button class="btn btn-secondary" onclick="App.navigate('code-analysis')" style="margin-top:1.5rem">Go to Code Analysis</button>
            </div>
        `
    }
};

window.UI = UI;
