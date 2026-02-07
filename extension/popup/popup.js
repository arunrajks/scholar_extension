document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const resultsList = document.getElementById('results-list');
    const loading = document.getElementById('loading');
    const statusMsg = document.getElementById('status-message');
    const tabPapers = document.getElementById('tab-papers');
    const tabResearchers = document.getElementById('tab-researchers');

    let currentMode = 'papers';
    const API_BASE_URL = 'https://scholarly-search-api-70wp.onrender.com';

    // Tab switching
    const setMode = (mode) => {
        currentMode = mode;
        if (mode === 'papers') {
            tabPapers.classList.add('active');
            tabResearchers.classList.remove('active');
            searchInput.placeholder = 'Search papers, DOIs, journals...';
        } else {
            tabResearchers.classList.add('active');
            tabPapers.classList.remove('active');
            searchInput.placeholder = 'Search scholars, authors, h-index...';
        }
    };

    tabPapers.addEventListener('click', () => setMode('papers'));
    tabResearchers.addEventListener('click', () => setMode('researchers'));

    // Load saved state
    chrome.storage?.local?.get(['lastSearch'], (result) => {
        if (result.lastSearch) {
            const { query, mode, results } = result.lastSearch;
            searchInput.value = query || '';
            setMode(mode || 'papers');
            if (results) {
                if (mode === 'papers') {
                    renderPaperResults(results, false); // false to avoid double-saving
                } else {
                    renderResearcherResults(results, false);
                }
            }
        }
    });

    const performSearch = async () => {
        const query = searchInput.value.trim();
        if (!query) return;

        resultsList.innerHTML = '';
        loading.classList.remove('hidden');
        statusMsg.classList.add('hidden');

        const endpoint = currentMode === 'papers' ? '/search' : '/search/authors';

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}?q=${encodeURIComponent(query)}`);
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Server error (${response.status})`);
            }

            const data = await response.json();
            const results = data.results || [];

            if (currentMode === 'papers') {
                renderPaperResults(results);
            } else {
                renderResearcherResults(results);
            }

            // Save state
            chrome.storage?.local?.set({
                lastSearch: { query, mode: currentMode, results }
            });

        } catch (error) {
            console.error('Search error:', error);
            showStatus(`${error.message || 'Error connecting to server.'}`, 'error');
        } finally {
            loading.classList.add('hidden');
        }
    };

    const renderPaperResults = (results, save = true) => {
        if (!results || results.length === 0) {
            showEmpty('No papers found.');
            return;
        }

        resultsList.innerHTML = ''; // Clear for fresh render

        results.forEach(paper => {
            const card = document.createElement('div');
            card.className = 'paper-card';

            const authors = paper.authors || [];
            const authorsStr = authors.map(a => a.name).slice(0, 3).join(', ') +
                (authors.length > 3 ? ' et al.' : '');

            const sources = paper.sources || [];
            const pdfSource = sources.find(s => s.label === 'Open Access PDF');
            const bestSource = sources.find(s => s.access_type === 'oa') || sources[0];

            const citations = paper.formatted_citations || {};

            card.innerHTML = `
                <div class="source-badge">${paper.source_api || 'API'}</div>
                <div class="paper-title">${paper.title || 'Untitled'}</div>
                <div class="paper-meta">
                    <div class="meta-item">📅 ${paper.year || 'N/A'}</div>
                    <div class="meta-item">👤 ${authorsStr || 'Unknown'}</div>
                    ${paper.citation_count ? `<div class="meta-item">📈 ${paper.citation_count} citations</div>` : ''}
                </div>
                
                <div class="paper-actions">
                    <a href="${bestSource?.url || '#'}" target="_blank" class="btn-action btn-paper">Open Source</a>
                    ${pdfSource ? `<a href="${pdfSource.url}" target="_blank" class="btn-action btn-pdf">Open PDF</a>` : ''}
                </div>

                <div class="export-group">
                    <button class="btn-export bibtex-btn" data-content="${encodeURIComponent(paper.bibtex || '')}" data-name="citation.bib">BibTeX</button>
                    <button class="btn-export ris-btn" data-content="${encodeURIComponent(paper.ris || '')}" data-name="citation.ris">RIS</button>
                </div>

                ${Object.keys(citations).length > 0 ? `
                <div class="citation-options">
                    <div class="citation-header">Journal Styles:</div>
                    <div class="style-list">
                        ${Object.entries(citations).map(([style, content]) => `
                            <button class="btn-style" data-content="${encodeURIComponent(content)}" data-name="${style}.txt">${style}</button>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
            `;
            resultsList.appendChild(card);
        });

        attachActionListeners();
    };

    const renderResearcherResults = (results, save = true) => {
        if (!results || results.length === 0) {
            showEmpty('No scholars found.');
            return;
        }

        resultsList.innerHTML = ''; // Clear for fresh render

        results.forEach(res => {
            if (!res) return;
            const card = document.createElement('div');
            card.className = 'paper-card researcher-card';

            card.innerHTML = `
                <div class="source-badge">${res.source || 'API'}</div>
                <div class="paper-title">${res.name || 'Unknown Researcher'}</div>
                ${res.affiliation ? `<div class="affiliation">${res.affiliation}</div>` : ''}
                
                <div class="stats-grid">
                    <div class="stat-item">
                        <span class="stat-value">${res.h_index || 0}</span>
                        <span class="stat-label">H-Index</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">${(res.citation_count || 0).toLocaleString()}</span>
                        <span class="stat-label">Citations</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">${(res.paper_count || 0).toLocaleString()}</span>
                        <span class="stat-label">Papers</span>
                    </div>
                </div>
                
                <div class="paper-actions" style="grid-template-columns: 1fr;">
                    <a href="${res.url || '#'}" target="_blank" class="btn-action btn-paper">View Profile</a>
                </div>
            `;
            resultsList.appendChild(card);
        });
    };

    const attachActionListeners = () => {
        document.querySelectorAll('.bibtex-btn, .ris-btn, .btn-style').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const content = decodeURIComponent(e.target.dataset.content);
                const name = e.target.dataset.name;
                downloadFile(content, name, 'text/plain');
            });
        });
    };

    const showEmpty = (msg) => {
        resultsList.innerHTML = `<div class="empty-state"><p>${msg}</p></div>`;
    };

    const showStatus = (msg, type) => {
        statusMsg.textContent = msg;
        statusMsg.className = `status-message ${type}`;
        statusMsg.classList.remove('hidden');
    };

    const downloadFile = (content, fileName, contentType) => {
        const a = document.createElement("a");
        const file = new Blob([content], { type: contentType });
        a.href = URL.createObjectURL(file);
        a.download = fileName;
        a.click();
        URL.revokeObjectURL(a.href);
    };

    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });

    document.getElementById('open-sidepanel')?.addEventListener('click', async () => {
        // Open side panel
        const [tab] = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
        if (tab) {
            chrome.sidePanel.open({ tabId: tab.id });
            window.close(); // Close the popup
        }
    });
});
