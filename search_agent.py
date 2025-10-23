# search_agent.py
import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://econ.unitbv.ro"

def search_site(query, max_results=3):
    """
    Perform a simple search on econ.unitbv.ro by crawling internal links.
    Returns a list of (title, url) tuples.
    """
    try:
        # Basic site: search using Google as fallback
        google_query = f"site:econ.unitbv.ro {query}"
        from ddgs import DDGS
        results = DDGS().text(google_query, max_results=max_results)
        output = []
        for r in results:
            title = r.get("title", "")
            href = r.get("href", "")
            if href and href.startswith(BASE_URL):
                output.append((title, href))
        if output:
            return output
    except Exception as e:
        print("DuckDuckGo search failed:", e)

    # Fallback simple crawl of homepage if no search results
    try:
        resp = requests.get(BASE_URL + "/ro/")
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        links = [
            (a.get_text(strip=True), a["href"])
            for a in soup.find_all("a", href=True)
            if "pdf" in a["href"].lower() or query.lower() in a.get_text(strip=True).lower()
        ]
        return [(title, BASE_URL + href if href.startswith("/") else href) for title, href in links]
    except Exception as e:
        print("Fallback crawl failed:", e)
        return []

def invoke_search_agent(user_input: str) -> str:
    """Main callable for the orchestrator."""
    results = search_site(user_input)
    if not results:
        return "I couldn't find any matching pages or PDFs on the econ.unitbv.ro website."
    
    response = "Here are the most relevant results I found:\n"
    for title, url in results:
        response += f"- {title}\n  {url}\n"
    return response
