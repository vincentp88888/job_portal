import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin
from typing import List, Dict, Optional
from modules.gemini_llm import GeminiLLM
import os


class JobScraper:
    """Search jobs across popular job sites using keyword and location preferences."""

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )

    def __init__(self, timeout: int = 20, use_gemini_search: bool = False, gemini_api_key: Optional[str] = None, gemini_model: str = "gemini-2.5-flash"):
        self.timeout = timeout
        self.use_gemini_search = use_gemini_search
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        self.gemini_model = gemini_model
        self.headers = {
            "User-Agent": self.USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }

    def search(
        self,
        title: str,
        location: str = "",
        sites: Optional[List[str]] = None,
        per_site_limit: int = 20,
        overall_limit: int = 100,
    ) -> List[Dict[str, str]]:
        if sites is None:
            sites = [
                "LinkedIn",
                "Google",
                "Indeed",
                "JobStreet",
                "JobsDB",
                "Foundit",
                "MyFutureCareer",
            ]

        title = title.strip()
        location = location.strip()
        results: List[Dict[str, str]] = []

        if not title:
            return results

        for site in sites:
            try:
                if site == "Indeed":
                    results.extend(self.search_indeed(title, location, per_site_limit))
                elif site == "LinkedIn":
                    results.extend(self.search_linkedin(title, location, per_site_limit))
                elif site == "Google":
                    # If enabled, use Gemini's google_search grounding tool to do live web searches
                    if self.use_gemini_search and self.gemini_api_key:
                        try:
                            gem = GeminiLLM(api_key=self.gemini_api_key, model_name=self.gemini_model, enable_google_search=True)
                            resp = gem.google_search_jobs(f"{title}", limit=per_site_limit)
                            # Add as a single aggregated result when parsing isn't available
                            results.append({
                                "source": "Google(Gemini)",
                                "title": title,
                                "company": "",
                                "location": location,
                                "summary": resp,
                                "url": "",
                            })
                        except Exception:
                            # fallback to direct google scraping
                            results.extend(self.search_google(title, location, per_site_limit))
                    else:
                        results.extend(self.search_google(title, location, per_site_limit))
                elif site == "JobStreet":
                    results.extend(self.search_jobstreet(title, location, per_site_limit))
                elif site == "JobsDB":
                    results.extend(self.search_jobsdb(title, location, per_site_limit))
                elif site == "Foundit":
                    results.extend(self.search_foundit(title, location, per_site_limit))
                elif site == "MyFutureCareer":
                    results.extend(self.search_myfuturecareer(title, location, per_site_limit))
            except Exception:
                # Skip broken scrapers without blocking the rest
                continue

        unique = []
        seen = set()
        for job in results:
            key = (job.get("source"), job.get("title"), job.get("company"), job.get("url"))
            if key not in seen:
                seen.add(key)
                unique.append(job)

        return unique[:overall_limit]

    def _fetch_soup(self, url: str) -> BeautifulSoup:
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def _normalize_text(self, value: Optional[str]) -> str:
        return value.strip() if isinstance(value, str) else ""

    def fetch_job_description(self, url: str) -> str:
        try:
            soup = self._fetch_soup(url)
        except Exception:
            return ""

        selectors = [
            "div.jobDescriptionText",
            "div.description",
            "div#jobDetails",
            "div.job-description",
            "div.job-desc",
            "article",
            "section",
        ]

        for selector in selectors:
            block = soup.select_one(selector)
            if block and block.get_text(strip=True):
                return self._normalize_text(block.get_text(separator="\n\n"))

        paragraphs = soup.select("p")
        if paragraphs:
            texts = [self._normalize_text(p.get_text()) for p in paragraphs[:15] if p.get_text(strip=True)]
            return "\n\n".join(texts)

        return ""

    def search_indeed(self, title: str, location: str, limit: int) -> List[Dict[str, str]]:
        query = quote_plus(title)
        loc = quote_plus(location)
        url = f"https://www.indeed.com/jobs?q={query}&l={loc}"
        soup = self._fetch_soup(url)
        jobs = []

        for card in soup.select("a[href*='/rc/clk?'], a[href*='/pagead/']"):
            if len(jobs) >= limit:
                break

            title_text = self._normalize_text(card.get_text())
            href = card.get("href")
            if not title_text or not href:
                continue

            url = urljoin("https://www.indeed.com", href)
            company = ""
            summary = ""
            parent = card.find_parent()
            if parent:
                company_elem = parent.select_one("span.companyName, div.companyName")
                summary_elem = parent.select_one("div.job-snippet, div.summary")
                company = self._normalize_text(company_elem.get_text() if company_elem else "")
                summary = self._normalize_text(summary_elem.get_text() if summary_elem else "")

            jobs.append({
                "source": "Indeed",
                "title": title_text,
                "company": company,
                "location": location,
                "summary": summary,
                "url": url,
            })

        return jobs

    def search_linkedin(self, title: str, location: str, limit: int) -> List[Dict[str, str]]:
        query = quote_plus(title)
        loc = quote_plus(location)
        url = f"https://www.linkedin.com/jobs/search?keywords={query}&location={loc}"
        soup = self._fetch_soup(url)
        jobs = []

        for item in soup.select("a[href*='/jobs/view/']"):
            if len(jobs) >= limit:
                break

            title_text = self._normalize_text(item.get_text())
            href = item.get("href")
            if not title_text or not href:
                continue

            job_url = href if href.startswith("http") else urljoin("https://www.linkedin.com", href)
            company = self._normalize_text(item.select_one("h4") and item.select_one("h4").get_text())
            summary = ""

            jobs.append({
                "source": "LinkedIn",
                "title": title_text,
                "company": company,
                "location": location,
                "summary": summary,
                "url": job_url,
            })

        return jobs

    def search_google(self, title: str, location: str, limit: int) -> List[Dict[str, str]]:
        query = quote_plus(f"{title} jobs {location}")
        url = f"https://www.google.com/search?q={query}"
        soup = self._fetch_soup(url)
        jobs = []

        for link in soup.select("a[href]"):
            if len(jobs) >= limit:
                break

            href = link.get("href")
            if not href:
                continue

            if href.startswith("/url?q="):
                job_url = href.split("/url?q=")[1].split("&")[0]
            elif href.startswith("http"):
                job_url = href
            else:
                continue

            title_text = self._normalize_text(link.get_text())
            if not title_text or "google.com" in job_url or "webcache.googleusercontent.com" in job_url:
                continue

            jobs.append({
                "source": "Google",
                "title": title_text,
                "company": "",
                "location": location,
                "summary": "",
                "url": job_url,
            })

        return jobs

    def search_jobstreet(self, title: str, location: str, limit: int) -> List[Dict[str, str]]:
        query = quote_plus(title)
        loc = quote_plus(location)
        url = f"https://www.jobstreet.com.sg/en/job-search/job-vacancy.php?key={query}&location={loc}"
        soup = self._fetch_soup(url)
        jobs = []

        for link in soup.select("a[href*='/en/job/']"):
            if len(jobs) >= limit:
                break

            title_text = self._normalize_text(link.get_text())
            href = link.get("href")
            if not title_text or not href:
                continue

            job_url = urljoin("https://www.jobstreet.com.sg", href)
            company = self._normalize_text(link.find_next("span") and link.find_next("span").get_text())
            summary = ""
            jobs.append({
                "source": "JobStreet",
                "title": title_text,
                "company": company,
                "location": location,
                "summary": summary,
                "url": job_url,
            })

        return jobs

    def search_jobsdb(self, title: str, location: str, limit: int) -> List[Dict[str, str]]:
        query = quote_plus(title)
        loc = quote_plus(location)
        url = f"https://sg.jobsdb.com/en-hk/jobs/{query}-jobs-in-{loc}"
        soup = self._fetch_soup(url)
        jobs = []

        for card in soup.select("a[href*='/job/']"):
            if len(jobs) >= limit:
                break

            title_text = self._normalize_text(card.get_text())
            href = card.get("href")
            if not title_text or not href:
                continue

            job_url = urljoin("https://sg.jobsdb.com", href)
            company = self._normalize_text(card.find_previous("span") and card.find_previous("span").get_text())
            jobs.append({
                "source": "JobsDB",
                "title": title_text,
                "company": company,
                "location": location,
                "summary": "",
                "url": job_url,
            })

        return jobs

    def search_foundit(self, title: str, location: str, limit: int) -> List[Dict[str, str]]:
        query = quote_plus(title)
        loc = quote_plus(location)
        url = f"https://www.foundit.com.sg/search/jobs?keywords={query}&location={loc}"
        soup = self._fetch_soup(url)
        jobs = []

        for card in soup.select("a[href*='/job/'], article a[href]"):
            if len(jobs) >= limit:
                break

            title_text = self._normalize_text(card.get_text())
            href = card.get("href")
            if not title_text or not href:
                continue

            job_url = urljoin("https://www.foundit.com.sg", href)
            company = self._normalize_text(card.find_previous("span") and card.find_previous("span").get_text())
            jobs.append({
                "source": "Foundit",
                "title": title_text,
                "company": company,
                "location": location,
                "summary": "",
                "url": job_url,
            })

        return jobs

    def search_myfuturecareer(self, title: str, location: str, limit: int) -> List[Dict[str, str]]:
        query = quote_plus(title)
        loc = quote_plus(location)
        url = f"https://www.myfuturecareer.com/search?keyword={query}&location={loc}"
        soup = self._fetch_soup(url)
        jobs = []

        for card in soup.select("a[href*='/job/'], a[href*='job-listing']"):
            if len(jobs) >= limit:
                break

            title_text = self._normalize_text(card.get_text())
            href = card.get("href")
            if not title_text or not href:
                continue

            job_url = urljoin("https://www.myfuturecareer.com", href)
            company = self._normalize_text(card.find_next("span") and card.find_next("span").get_text())
            jobs.append({
                "source": "MyFutureCareer",
                "title": title_text,
                "company": company,
                "location": location,
                "summary": "",
                "url": job_url,
            })

        return jobs
