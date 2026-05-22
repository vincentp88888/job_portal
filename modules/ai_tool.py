import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from typing import List, Dict, Optional


class AIToolSearch:
    """Search AI agent skill information from the internet."""

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )

    def __init__(self, timeout: int = 20):
        self.timeout = timeout
        self.headers = {
            "User-Agent": self.USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }

    def search_skill(self, query: str, limit: int = 6) -> List[Dict[str, str]]:
        query = query.strip()
        if not query:
            return []

        url = f"https://duckduckgo.com/html/?q={quote_plus(query + ' ai agent skill')}"
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results: List[Dict[str, str]] = []

        for element in soup.select("a.result__a, a.result-link"):  # DuckDuckGo result links
            if len(results) >= limit:
                break

            href = element.get("href")
            title = element.get_text(strip=True)
            if not href or not title:
                continue

            summary = ""
            snippet_el = element.find_parent().select_one("a.result__snippet, .result__snippet, .result__summary")
            if snippet_el:
                summary = snippet_el.get_text(strip=True)

            results.append({
                "title": title,
                "url": href,
                "summary": summary,
            })

        return results

    def search_skill_text(self, query: str, limit: int = 6) -> str:
        results = self.search_skill(query, limit=limit)
        if not results:
            return "No internet search results were found for this skill query." 

        lines = [f"{i + 1}. {item['title']}\n{item['url']}" for i, item in enumerate(results)]
        return "\n\n".join(lines)
