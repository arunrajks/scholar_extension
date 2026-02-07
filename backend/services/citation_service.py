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

def generate_apa(paper: ScholarlyPaper) -> str:
    """Generates APA style citation."""
    authors = ", ".join([a.name for a in paper.authors])
    if len(paper.authors) > 7:
        authors = ", ".join([a.name for a in paper.authors[:6]]) + ", ... " + paper.authors[-1].name
    
    year = f"({paper.year})" if paper.year else "(n.d.)"
    journal = f". {paper.journal}." if paper.journal else "."
    doi = f" https://doi.org/{paper.doi}" if paper.doi else ""
    
    return f"{authors} {year}. {paper.title}{journal}{doi}"

def generate_nature(paper: ScholarlyPaper) -> str:
    """Generates Nature style citation."""
    if not paper.authors:
        authors = "Unknown."
    elif len(paper.authors) > 5:
        authors = f"{paper.authors[0].name} et al."
    else:
        authors = ", ".join([a.name for a in paper.authors])
    
    journal = f" {paper.journal}" if paper.journal else ""
    year = f" ({paper.year})" if paper.year else ""
    
    return f"{authors} {paper.title}.{journal}{year}."

def generate_science(paper: ScholarlyPaper) -> str:
    """Generates Science style citation."""
    authors = ", ".join([a.name for a in paper.authors])
    journal = f" {paper.journal}" if paper.journal else ""
    year = f" ({paper.year})" if paper.year else ""
    
    return f"{authors}, {paper.title}.{journal}{year}."

def generate_standard_list(paper: ScholarlyPaper) -> str:
    """Generates a numbered/CV style citation: First and Second et al. Title. Journal, Vol, Year."""
    if not paper.authors:
        authors = "Unknown"
    elif len(paper.authors) == 1:
        authors = paper.authors[0].name
    elif len(paper.authors) == 2:
        authors = f"{paper.authors[0].name} and {paper.authors[1].name}"
    else:
        # Rule based on user examples: First and Second et al.
        authors = f"{paper.authors[0].name} and {paper.authors[1].name} et al."
    
    title = paper.title
    journal = paper.journal if paper.journal else "Unknown Journal"
    volume = f", {paper.volume}" if paper.volume else ""
    year = f", {paper.year}" if paper.year else ""
    
    return f"{authors}. {title}. {journal}{volume}{year}."

def format_all_citations(paper: ScholarlyPaper):
    """Fills the formatted_citations dictionary."""
    paper.formatted_citations = {
        "APA": generate_apa(paper),
        "Nature": generate_nature(paper),
        "Science": generate_science(paper),
        "Standard": generate_standard_list(paper)
    }
