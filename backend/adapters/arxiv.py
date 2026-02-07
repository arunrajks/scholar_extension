import xml.etree.ElementTree as ET
from adapters.base import BaseAdapter
from models import ScholarlyPaper, Author, PaperSource
from typing import List
import httpx

class ArxivAdapter(BaseAdapter):
    async def search(self, query: str, limit: int = 10) -> List[ScholarlyPaper]:
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query}",
            "max_results": limit
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                root = ET.fromstring(response.text)
            
            # XML namespaces
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            results = []
            for entry in root.findall('atom:entry', ns):
                title = entry.find('atom:title', ns).text.strip()
                authors = [Author(name=a.find('atom:name', ns).text) for a in entry.findall('atom:author', ns)]
                
                published = entry.find('atom:published', ns).text
                year = int(published[:4]) if published else None
                
                arxiv_id = entry.find('atom:id', ns).text.split('/abs/')[-1]
                sources = []
                
                # Abstract page
                sources.append(PaperSource(
                    url=f"https://arxiv.org/abs/{arxiv_id}",
                    label="Preprint Page",
                    access_type="preprint"
                ))
                
                # PDF link
                pdf_url = None
                for link in entry.findall('atom:link', ns):
                    if link.attrib.get('title') == 'pdf':
                        pdf_url = link.attrib.get('href')
                
                if pdf_url:
                    sources.append(PaperSource(
                        url=pdf_url,
                        label="Open Access PDF",
                        access_type="oa"
                    ))
                
                results.append(ScholarlyPaper(
                    title=title,
                    authors=authors,
                    year=year,
                    journal="arXiv",
                    sources=sources,
                    source_api="arXiv"
                ))
            return results
        except Exception as e:
            print(f"arXiv Error: {e}")
            return []
