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

def generate_ieee(paper: ScholarlyPaper) -> str:
    """Generates IEEE style citation: [1] I. Initials Surname, "Title," Journal, vol. V, no. N, pp. P, Year."""
    authors = []
    for a in paper.authors:
        names = a.name.split()
        if len(names) > 1:
            initials = "".join([n[0] + "." for n in names[:-1]])
            authors.append(f"{initials} {names[-1]}")
        else:
            authors.append(a.name)
    
    author_str = ", ".join(authors[:6]) + (", et al." if len(authors) > 6 else "")
    journal = paper.journal if paper.journal else "Unknown Journal"
    vol = f", vol. {paper.volume}" if paper.volume else ""
    no = f", no. {paper.issue}" if paper.issue else ""
    pp = f", pp. {paper.pages}" if paper.pages else ""
    year = f", {paper.year}" if paper.year else ""
    
    return f"{author_str}, \"{paper.title},\" {journal}{vol}{no}{pp}{year}."

def generate_harvard(paper: ScholarlyPaper) -> str:
    """Generates Harvard style citation: Surname, I. (Year) 'Title', Journal, Vol(No), pp. P."""
    authors = []
    for a in paper.authors:
        names = a.name.split()
        if len(names) > 1:
            authors.append(f"{names[-1]}, {names[0][0]}.")
        else:
            authors.append(a.name)
    
    author_str = ", ".join(authors[:3]) + (" et al." if len(authors) > 3 else "")
    year = f"({paper.year})" if paper.year else "(n.d.)"
    journal = f"{paper.journal}" if paper.journal else "Unknown Journal"
    vol_no = f"{paper.volume}" + (f"({paper.issue})" if paper.issue else "")
    pp = f", pp. {paper.pages}" if paper.pages else ""
    
    return f"{author_str} {year} '{paper.title}', {journal}, {vol_no}{pp}."

def generate_vancouver(paper: ScholarlyPaper) -> str:
    """Generates Vancouver style citation: Author I. Title. Journal. Year;Vol(No):Page."""
    authors = []
    for a in paper.authors:
        names = a.name.split()
        if len(names) > 1:
            authors.append(f"{names[-1]} {names[0][0]}")
        else:
            authors.append(a.name)
    
    author_str = ", ".join(authors[:6]) + (", et al." if len(authors) > 6 else "")
    journal = paper.journal if paper.journal else "Unknown Journal"
    vol_no = f"{paper.volume}" + (f"({paper.issue})" if paper.issue else "")
    pages = f":{paper.pages}" if paper.pages else ""
    
    return f"{author_str}. {paper.title}. {journal}. {paper.year};{vol_no}{pages}."

def generate_chicago(paper: ScholarlyPaper) -> str:
    """Generates Chicago style citation: Author, I. "Title." Journal Vol, no. No (Year): Page."""
    author_str = paper.authors[0].name if paper.authors else "Unknown"
    if len(paper.authors) > 1:
        author_str += " et al."
        
    journal = paper.journal if paper.journal else "Unknown Journal"
    vol = f" {paper.volume}" if paper.volume else ""
    no = f", no. {paper.issue}" if paper.issue else ""
    year = f" ({paper.year})" if paper.year else ""
    pages = f": {paper.pages}" if paper.pages else ""
    
    return f"{author_str}. \"{paper.title}.\" {journal}{vol}{no}{year}{pages}."

def generate_mla(paper: ScholarlyPaper) -> str:
    """Generates MLA style citation: Author, I. \"Title.\" Journal, vol. V, no. N, Year, pp. P."""
    author_str = paper.authors[0].name if paper.authors else "Unknown"
    if len(paper.authors) > 2:
        author_str += ", et al."
    elif len(paper.authors) == 2:
        author_str += ", and " + paper.authors[1].name
        
    journal = paper.journal if paper.journal else "Unknown Journal"
    vol = f", vol. {paper.volume}" if paper.volume else ""
    no = f", no. {paper.issue}" if paper.issue else ""
    year = f", {paper.year}" if paper.year else ""
    pp = f", pp. {paper.pages}" if paper.pages else ""
    
    return f"{author_str}. \"{paper.title}.\" {journal}{vol}{no}{year}{pp}."

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

def generate_pnas(paper: ScholarlyPaper) -> str:
    """PNAS style: Author Initial Surname, et al. (Year) Title. Proc Natl Acad Sci USA Vol(Issue):Pages."""
    authors = []
    for a in paper.authors:
        names = a.name.split()
        if len(names) > 1:
            authors.append(f"{names[-1]} {names[0][0]}")
        else:
            authors.append(a.name)
    
    author_str = ", ".join(authors[:5]) + (" et al." if len(authors) > 5 else "")
    journal = paper.journal if paper.journal else "Proc Natl Acad Sci USA"
    vol_issue = f"{paper.volume}" + (f"({paper.issue})" if paper.issue else "")
    pages = f":{paper.pages}" if paper.pages else ""
    return f"{author_str} ({paper.year}) {paper.title}. {journal} {vol_issue}{pages}."

def generate_cell(paper: ScholarlyPaper) -> str:
    """Cell style: Author, A.B., Author, C.D., etc. (Year). Title. Cell Vol, Pages."""
    authors = []
    for a in paper.authors:
        names = a.name.split()
        if len(names) > 1:
            initials = "".join([n[0] + "." for n in names[:-1]])
            authors.append(f"{names[-1]}, {initials}")
        else:
            authors.append(a.name)
    
    author_str = ", ".join(authors[:10]) + (", et al." if len(authors) > 10 else "")
    journal = paper.journal if paper.journal else "Cell"
    vol = f" {paper.volume}" if paper.volume else ""
    pages = f", {paper.pages}" if paper.pages else ""
    return f"{author_str} ({paper.year}). {paper.title}. {journal}{vol}{pages}."

def generate_jama_ama(paper: ScholarlyPaper) -> str:
    """JAMA/AMA style: Author Initials Surname. Title. Journal. Year;Vol(Issue):Pages."""
    authors = []
    for a in paper.authors:
        names = a.name.split()
        if len(names) > 1:
            initials = "".join([n[0] for n in names[:-1]])
            authors.append(f"{names[-1]} {initials}")
        else:
            authors.append(a.name)
    
    author_str = ", ".join(authors[:6]) + (", et al." if len(authors) > 6 else "")
    journal = paper.journal if paper.journal else "Journal"
    vol_issue = f"{paper.volume}" + (f"({paper.issue})" if paper.issue else "")
    pages = f":{paper.pages}" if paper.pages else ""
    return f"{author_str}. {paper.title}. {journal}. {paper.year};{vol_issue}{pages}."

def generate_acs(paper: ScholarlyPaper) -> str:
    """ACS style: Author, A. B.; Author, C. D. Journal Year, Vol, Pages."""
    authors = []
    for a in paper.authors:
        names = a.name.split()
        if len(names) > 1:
            initials = ". ".join([n[0] for n in names[:-1]]) + "."
            authors.append(f"{names[-1]}, {initials}")
        else:
            authors.append(a.name)
    
    author_str = "; ".join(authors[:10]) + ("; et al." if len(authors) > 10 else "")
    journal = paper.journal if paper.journal else "Journal"
    vol = f", {paper.volume}" if paper.volume else ""
    pages = f", {paper.pages}" if paper.pages else ""
    return f"{author_str} {journal} {paper.year}{vol}{pages}."

def generate_aps(paper: ScholarlyPaper) -> str:
    """APS style: A. B. Author and C. D. Author, Journal Vol, Pages (Year)."""
    authors = []
    for a in paper.authors:
        names = a.name.split()
        if len(names) > 1:
            initials = ". ".join([n[0] for n in names[:-1]]) + "."
            authors.append(f"{initials} {names[-1]}")
        else:
            authors.append(a.name)
    
    if len(authors) > 4:
        author_str = f"{authors[0]} et al."
    elif len(authors) > 1:
        author_str = ", ".join(authors[:-1]) + " and " + authors[-1]
    else:
        author_str = authors[0] if authors else "Unknown"

    journal = paper.journal if paper.journal else "Journal"
    vol = f" {paper.volume}" if paper.volume else ""
    pages = f", {paper.pages}" if paper.pages else ""
    return f"{author_str}, {journal}{vol}{pages} ({paper.year})."

def format_all_citations(paper: ScholarlyPaper):
    """Fills the formatted_citations dictionary."""
    paper.formatted_citations = {
        "Standard": generate_standard_list(paper),
        "APA": generate_apa(paper),
        "Nature": generate_nature(paper),
        "Science": generate_science(paper),
        "IEEE": generate_ieee(paper),
        "Harvard": generate_harvard(paper),
        "Vancouver": generate_vancouver(paper),
        "Chicago": generate_chicago(paper),
        "MLA": generate_mla(paper),
        "Cell": generate_cell(paper),
        "Lancet": generate_vancouver(paper),
        "ACM": generate_acm(paper),
        "Bluebook": generate_bluebook(paper),
        "ASA": generate_asa(paper),
        "APSA": generate_asa(paper),
        "AAA": generate_asa(paper),
        "ASCE": generate_ieee(paper),
        "ASME": generate_ieee(paper),
        "PNAS": generate_pnas(paper),
        "NEJM": generate_jama_ama(paper),
        "JAMA": generate_jama_ama(paper),
        "ACS": generate_acs(paper),
        "APS": generate_aps(paper),
        "IOP": generate_aps(paper),
        "Springer": generate_standard_list(paper),
        "Elsevier": generate_standard_list(paper)
    }
