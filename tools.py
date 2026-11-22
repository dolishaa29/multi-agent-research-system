import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@tool
def web_search(query: str) -> str:
    """Search the web for recent information and return titles, URLs, and snippets."""
    results = tavily.search(query=query, max_results=5)

    snippets = []
    for result in results["results"]:
        snippets.append(
            f"Title :{result['title']}\n"
            f"URL:{result['url']}\n"
            f"Snippet:{result['content'][:300]}\n"
        )

    return "\n----\n".join(snippets)


@tool
def scrape_url(url: str) -> str:
    """Fetch a page and return its visible text for further reading."""
    try:
        response = requests.get(url, timeout=9, headers={"User-Agent": "Mozilla/5.0"})
        page = BeautifulSoup(response.text, "html.parser")
        for tag in page(["script", "style", "nav", "footer"]):
            tag.decompose()
        return page.get_text(separator=" ", strip=True)[:3000]
    except Exception as error:
        return f"could not scrape URL:{error}"
