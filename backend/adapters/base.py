from abc import ABC, abstractmethod
from typing import List, Optional
from models import ScholarlyPaper, Researcher
import httpx

class BaseAdapter(ABC):
    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[ScholarlyPaper]:
        pass

    async def search_authors(self, query: str, limit: int = 10) -> List[Researcher]:
        """Optional method for adapters that support author search."""
        return []

    async def fetch_json(self, url: str, params: dict = None) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
