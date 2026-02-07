from models import ScholarlyPaper

def generate_bibtex(paper: ScholarlyPaper) -> str:
    """Generates a BibTeX string for the paper."""
    # Create a unique key (author + year or title snippet)
    author_key = paper.authors[0].name.split()[-1] if paper.authors else "Unknown"
    year_key = paper.year if paper.year else "n.d."
    key = f"{author_key}{year_key}".lower().replace(" ", "")
    
    authors = " and ".join([a.name for a in paper.authors])
    
    bibtex = f"@article{{{key},\n"
    bibtex += f"  title = {{{paper.title}}},\n"
    bibtex += f"  author = {{{authors}}},\n"
    if paper.year:
        bibtex += f"  year = {{{paper.year}}},\n"
    if paper.journal:
        bibtex += f"  journal = {{{paper.journal}}},\n"
    if paper.doi:
        bibtex += f"  doi = {{{paper.doi}}},\n"
    if paper.sources:
        bibtex += f"  url = {{{paper.sources[0].url}}}\n"
    bibtex += "}"
    return bibtex

def generate_ris(paper: ScholarlyPaper) -> str:
    """Generates an RIS string for the paper."""
    ris = "TY  - JOUR\n"
    ris += f"TI  - {paper.title}\n"
    for author in paper.authors:
        ris += f"AU  - {author.name}\n"
    if paper.year:
        ris += f"PY  - {paper.year}\n"
    if paper.journal:
        ris += f"JO  - {paper.journal}\n"
    if paper.doi:
        ris += f"DO  - {paper.doi}\n"
    if paper.sources:
        ris += f"UR  - {paper.sources[0].url}\n"
    ris += "ER  - \n"
    return ris
