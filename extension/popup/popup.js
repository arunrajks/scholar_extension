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

    const tabCollection = document.getElementById('tab-collection');
    const collectionView = document.getElementById('collection-view');
    const collectionList = document.getElementById('collection-list');
    const searchContainer = document.getElementById('search-container');
    const collectCount = document.getElementById('collect-count');
    const clearBtn = document.getElementById('clear-collection');
    const exportBtn = document.getElementById('export-collection');

    let collectedCitations = [];

    // Tab switching
    const setMode = (mode) => {
        currentMode = mode;
        tabPapers.classList.toggle('active', mode === 'papers');
        tabResearchers.classList.toggle('active', mode === 'researchers');
        tabCollection.classList.toggle('active', mode === 'collection');

        if (mode === 'collection') {
            resultsList.classList.add('hidden');
            searchContainer.classList.add('hidden');
            collectionView.classList.remove('hidden');
            renderCollection();
        } else {
            collectionView.classList.add('hidden');
            resultsList.classList.remove('hidden');
            searchContainer.classList.remove('hidden');
            searchInput.placeholder = mode === 'papers' ?
                'Search papers, DOIs, journals...' :
                'Search scholars, authors, h-index...';
        }
    };

    tabPapers.addEventListener('click', () => setMode('papers'));
    tabResearchers.addEventListener('click', () => setMode('researchers'));
    tabCollection.addEventListener('click', () => setMode('collection'));

    const updateCollectCount = () => {
        collectCount.textContent = collectedCitations.length;
        chrome.storage?.local?.set({ collectedCitations });
    };

    // Load saved state
    chrome.storage?.local?.get(['lastSearch', 'collectedCitations'], (result) => {
        if (result.collectedCitations) {
            collectedCitations = result.collectedCitations;
            updateCollectCount();
        }
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

    const toggleCollect = (paper) => {
        const index = collectedCitations.findIndex(c => (c.doi && c.doi === paper.doi) || (c.title === paper.title));
        if (index > -1) {
            collectedCitations.splice(index, 1);
        } else {
            collectedCitations.push({
                title: paper.title,
                standard: paper.formatted_citations.Standard,
                bibtex: paper.bibtex,
                doi: paper.doi
            });
        }
        updateCollectCount();

        // Re-render current view to update button states
        if (currentMode === 'papers') {
            chrome.storage.local.get(['lastSearch'], (res) => {
                if (res.lastSearch?.results) renderPaperResults(res.lastSearch.results, false);
            });
        } else if (currentMode === 'collection') {
            renderCollection();
        }
    };

    const renderPaperResults = (results, save = true) => {
        if (!results || results.length === 0) {
            showEmpty('No papers found.');
            return;
        }

        resultsList.innerHTML = ''; // Clear for fresh render

        results.forEach((paper, index) => {
            const isCollected = collectedCitations.some(c => (c.doi && c.doi === paper.doi) || (c.title === paper.title));
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
                <div class="paper-actions-top">
                    <div class="source-badge">${paper.source_api || 'API'}</div>
                    <button class="btn-collect ${isCollected ? 'collected' : ''}" data-index="${index}">
                        ${isCollected ? '⭐ Collected' : '☆ Collect'}
                    </button>
                </div>
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
                        ${Object.entries(citations).map(([style, content]) => {
                // Prepend index for Standard style as requested by user
                const finalContent = style === 'Standard' ? `[${index + 1}] ${content}` : content;
                return `<button class="btn-style" data-content="${encodeURIComponent(finalContent)}" data-name="${style}.txt">${style}</button>`;
            }).join('')}
                    </div>
                </div>
                ` : ''}
            `;
            card.querySelector('.btn-collect').addEventListener('click', () => toggleCollect(paper));
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
