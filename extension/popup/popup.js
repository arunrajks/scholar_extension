document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const resultsList = document.getElementById('results-list');
    const loading = document.getElementById('loading');
    const statusMsg = document.getElementById('status-message');

    const API_URL = 'https://scholarly-search-api-70wp.onrender.com/search';

    const performSearch = async () => {
        const query = searchInput.value.trim();
        if (!query) return;

        resultsList.innerHTML = '';
        loading.classList.remove('hidden');
        statusMsg.classList.add('hidden');

        try {
            const response = await fetch(`${API_URL}?q=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error('Failed to fetch results');

            const data = await response.json();
            renderResults(data.results);
        } catch (error) {
            console.error(error);
            showStatus('Error: Make sure the backend server relative to http://localhost:8000 is running.', 'error');
        } finally {
            loading.classList.add('hidden');
        }
    };

    const renderResults = (papers) => {
        if (!papers || papers.length === 0) {
            resultsList.innerHTML = `
                <div class="empty-state">
                    <p>No results found for your query.</p>
                </div>
            `;
            return;
        }

        papers.forEach(paper => {
            const card = document.createElement('div');
            card.className = 'paper-card';

            const authorsStr = paper.authors.map(a => a.name).slice(0, 3).join(', ') +
                (paper.authors.length > 3 ? ' et al.' : '');

            // Find a primary "Open Source" link and an optional "Open PDF" link
            const bestSource = paper.sources.find(s => s.access_type === 'oa' || s.label === 'Publisher Page') || paper.sources[0];
            const pdfSource = paper.sources.find(s => s.label === 'Open Access PDF');

            let sourcesHtml = paper.sources.map(source => `
                <div class="source-item">
                    <a href="${source.url}" target="_blank" class="source-link">${source.label}</a>
                    <span class="access-badge access-${source.access_type}">${source.access_type.toUpperCase()}</span>
                </div>
            `).join('');

            card.innerHTML = `
                <div class="source-badge">${paper.source_api}</div>
                <div class="paper-title">${paper.title}</div>
                <div class="paper-meta">
                    <div class="meta-item">📅 ${paper.year || 'N/A'}</div>
                    <div class="meta-item">👤 ${authorsStr || 'Unknown'}</div>
                    ${paper.journal ? `<div class="meta-item">📖 ${paper.journal}</div>` : ''}
                    ${paper.citation_count ? `<div class="meta-item">📈 ${paper.citation_count} citations</div>` : ''}
                </div>
                
                <div class="paper-actions">
                    <a href="${bestSource?.url || '#'}" target="_blank" class="btn-action btn-paper">
                        Open Source
                    </a>
                    ${pdfSource ? `
                        <a href="${pdfSource.url}" target="_blank" class="btn-action btn-pdf">
                            Open PDF
                        </a>
                    ` : ''}
                </div>

                <div class="source-links-section">
                    <div class="source-links-title">Legitimate Sources</div>
                    ${sourcesHtml}
                </div>

                <div class="export-group">
                    <button class="btn-action btn-export bibtex-btn" data-bibtex="${encodeURIComponent(paper.bibtex)}">Export BibTeX</button>
                    <button class="btn-action btn-export ris-btn" data-ris="${encodeURIComponent(paper.ris)}">Export RIS</button>
                </div>
            `;
            resultsList.appendChild(card);
        });

        // Add event listeners for export buttons
        document.querySelectorAll('.bibtex-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const content = decodeURIComponent(e.target.dataset.bibtex);
                downloadFile(content, 'citation.bib', 'text/plain');
            });
        });

        document.querySelectorAll('.ris-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const content = decodeURIComponent(e.target.dataset.ris);
                downloadFile(content, 'citation.ris', 'text/plain');
            });
        });
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
});
