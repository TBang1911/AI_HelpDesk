import asyncio
from typing import Any
from ddgs import DDGS
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from playwright.async_api import async_playwright
import trafilatura

class LangTools:
    def __init__(self) -> None:
        pass

    async def duckduckgo_search(self, query: str, max_result = 5) -> Any:
        try:
            urls = []
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=max_result, region="vn-vi")
                if not results:
                    return "Không tìm thấy kết quả"
                for result in results:
                    urls.append(result["href"])
            print(f"response: {urls}")
            return urls
        except Exception as e:
            print(e)

    async def ascrawl_web(self, url: str):
        text = await self.crawl_web(url)

        if not text:
            yield "Ko tìm thấy kết quả"
            return

        step = 100
        scale = 0.1
        for i in range(0, len(text), step):
            chunk = text[i:i+step]
            yield chunk
            await asyncio.sleep((step/1000) * scale)

    async def crawl_web(self, url: str):
        if not url or not url.startswith(('http://', 'https://')):
            return f"Invalid URL: {url}"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=[
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--disable-extensions",
                "--disable-blink-features=AutomationControlled",
            ])
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            await page.goto(url, wait_until="domcontentloaded")

            html = await page.content()

            await browser.close()

        text = trafilatura.extract(html)
        return text

@tool
def add(a: int, b: int):
    """Cộng hai số nguyên."""
    return a + b
...

@tool
def test():
    """test tooling calling"""
    return "Test tooling calling"
...

@tool
def duckduckgo_search_tool(query: str, max_result = 5) -> Any:
    """
    Tìm kiếm thông tin trên internet qua DuckDuckGo. 
    """
    tool = LangTools()
    return tool.duckduckgo_search(query, max_result)
...

@tool("crawl_web")
async def crawl_web_tool(url: str):
    """
    Lấy thông thông tin trên internet qua url. 
    """
    tool = LangTools()
    return await tool.crawl_web(url)
...

@tool("ascrawl_web")
async def ascrawl_web_tool(url: str):
    """
    Lấy thông tin trên internet qua url và streaming trả về.
    """
    tool = LangTools()
    return await tool.ascrawl_web(url)
...

@tool
def rewrite_query(query: str) -> str:
    """
    Rewrite query for better search.
    Args:
        query: Original query to improve
    """
    # This will need the provider to be passed when called
    # For now, return a basic rewrite
    question_words = ["là", "gì", "như thế nào", "tại sao", "ở đâu", "khi nào"]
    cleaned_query = query.lower()
    
    for word in question_words:
        cleaned_query = cleaned_query.replace(word, "")
    
    cleaned_query = " ".join(cleaned_query.split()).strip()
    
    if not cleaned_query:
        return query
    
    return f"Tìm thông tin chi tiết về {cleaned_query}"

@tool
def check_relevance(query_docs: str) -> str:
    """
    Check relevance between query and documents.
    Args:
        query_docs: Format "query||docs" - query and documents separated by ||
    """
    try:
        if "||" not in query_docs:
            return "Error: Input must be in format 'query||docs'"
            
        query, docs = query_docs.split("||", 1)
        
        # Simple keyword matching for relevance
        query_words = set(query.lower().split())
        docs_words = set(docs.lower().split())
        
        common_words = query_words.intersection(docs_words)
        relevance_score = len(common_words) / len(query_words) if query_words else 0
        
        if relevance_score > 0.5:
            return "Cao: Ngữ cảnh có nhiều thông tin liên quan"
        elif relevance_score > 0.2:
            return "Trung bình: Ngữ cảnh có một số thông tin liên quan"
        else:
            return "Thấp: Ngữ cảnh ít liên quan"
            
    except Exception as e:
        return f"Error: {str(e)}"


