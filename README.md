# Scholarly: Universal Scholarly Search Engine

A domain-agnostic scholarly search engine that functions as a universal discovery and redirection tool for researchers.

## Core Principles
- **Discovery & Redirection**: Locates articles across all disciplines, regardless of paywall status.
- **Legitimate Sources**: Only links to official publisher pages, repositories, and open-access PDFs.
- **Multi-Source Display**: Surfaces all available legitimate links for a single record.

## Architecture
- **Backend**: FastAPI (Python) with modular adapters for Crossref, OpenAlex, Semantic Scholar, CORE, and arXiv.
- **Frontend**: Chrome Extension (Manifest V3) with a premium, researcher-friendly UI.
- **Deduplication**: Multi-stage logic using DOI primary key and Title+Year+Author fallback.

## Prerequisites
- Python 3.9+
- Chrome Browser

## Setup
1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```
2. **Extension**:
   - Go to `chrome://extensions/`.
   - Load the `extension` folder as an unpacked extension.

## Usage
- Search by keywords, title, or author.
- View a comprehensive list of sources for each paper.
- Export citations in BibTeX or RIS format directly from the results.
