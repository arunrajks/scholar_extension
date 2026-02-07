from adapters.base import BaseAdapter
from models import ScholarlyPaper, Author, PaperSource
from typing import List

class CoreAdapter(BaseAdapter):
    async def search(self, query: str, limit: int = 10) -> List[ScholarlyPaper]:
        url = f"https://core.ac.uk:443/api-v2/articles/search/{query}"
        params = {
            "pageSize": limit
        }
        
        try:
            data = await self.fetch_json(url, params=params)
            items = data.get("data", [])
            
            results = []
            for item in items:
                authors = [Author(name=name) for name in item.get("authors", [])]
                sources = []
                
                # Repository page
                sources.append(PaperSource(
                    url=f"https://core.ac.uk/reader/{item.get('id')}",
                    label="Repository Version",
                    access_type="oa"
                ))
                
                # PDF download link
                if item.get("downloadUrl"):
                    sources.append(PaperSource(
                        url=item["downloadUrl"],
                        label="Open Access PDF",
                        access_type="oa"
                    ))
                
                results.append(ScholarlyPaper(
                    title=item.get("title", "Unknown Title"),
                    authors=authors,
                    year=item.get("year"),
                    journal=item.get("publisher", ""),
                    doi=item.get("doi"),
                    sources=sources,
                    source_api="CORE"
                ))
            return results
        except Exception as e:
            print(f"CORE Error: {e}")
            return []
