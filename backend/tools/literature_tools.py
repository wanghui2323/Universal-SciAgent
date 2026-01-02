"""Tools for literature search and PDF processing"""
import asyncio
import aiohttp
import arxiv
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import quote
from tenacity import retry, stop_after_attempt, wait_exponential

from ..core.models import Paper
from .registry import tool_registry

logger = logging.getLogger(__name__)


@tool_registry.register(
    name="arxiv_search",
    description="Search papers on arXiv",
    required_params=["query"]
)
async def arxiv_search(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search arXiv for papers
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of paper dictionaries
    """
    try:
        # Use arxiv library for search
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        papers = []
        for result in search.results():
            paper = {
                "id": result.entry_id.split("/")[-1],
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "abstract": result.summary,
                "year": result.published.year if result.published else None,
                "url": result.entry_id,
                "pdf_url": result.pdf_url,
                "citations": 0,  # arXiv doesn't provide citation count
                "venue": "arXiv"
            }
            papers.append(paper)
        
        logger.info(f"Found {len(papers)} papers on arXiv for query: {query}")
        return papers
        
    except Exception as e:
        logger.error(f"arXiv search failed: {e}")
        return []


@tool_registry.register(
    name="semantic_scholar_search",
    description="Search papers on Semantic Scholar",
    required_params=["query"]
)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def semantic_scholar_search(
    query: str,
    max_results: int = 10,
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search Semantic Scholar for papers
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        api_key: Optional API key for higher rate limits
        
    Returns:
        List of paper dictionaries
    """
    try:
        base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": max_results,
            "fields": "paperId,title,abstract,year,authors,citationCount,url,venue,externalIds"
        }
        
        headers = {}
        if api_key:
            headers["x-api-key"] = api_key
        
        async with aiohttp.ClientSession() as session:
            async with session.get(base_url, params=params, headers=headers) as response:
                if response.status != 200:
                    logger.warning(f"Semantic Scholar API returned status {response.status}")
                    return []
                
                data = await response.json()
                papers = []
                
                for item in data.get("data", []):
                    # Extract arXiv ID if available
                    arxiv_id = None
                    if "externalIds" in item and item["externalIds"]:
                        arxiv_id = item["externalIds"].get("ArXiv")
                    
                    paper = {
                        "id": item.get("paperId", ""),
                        "title": item.get("title", ""),
                        "authors": [author["name"] for author in item.get("authors", [])],
                        "abstract": item.get("abstract", ""),
                        "year": item.get("year"),
                        "url": item.get("url", ""),
                        "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf" if arxiv_id else None,
                        "citations": item.get("citationCount", 0),
                        "venue": item.get("venue")
                    }
                    papers.append(paper)
                
                logger.info(f"Found {len(papers)} papers on Semantic Scholar for query: {query}")
                return papers
                
    except Exception as e:
        logger.error(f"Semantic Scholar search failed: {e}")
        return []


@tool_registry.register(
    name="pubmed_search",
    description="Search papers on PubMed (biomedical literature)",
    required_params=["query"]
)
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def pubmed_search(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search PubMed for biomedical papers
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
        
    Returns:
        List of paper dictionaries
    """
    try:
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance"
        }
        
        async with aiohttp.ClientSession() as session:
            # First, get PMIDs
            async with session.get(base_url, params=params) as response:
                if response.status != 200:
                    logger.warning(f"PubMed search returned status {response.status}")
                    return []
                
                data = await response.json()
                pmids = data.get("esearchresult", {}).get("idlist", [])
                
                if not pmids:
                    return []
                
                # Then, fetch paper details
                summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                summary_params = {
                    "db": "pubmed",
                    "id": ",".join(pmids),
                    "retmode": "json"
                }
                
                async with session.get(summary_url, params=summary_params) as summary_response:
                    if summary_response.status != 200:
                        return []
                    
                    summary_data = await summary_response.json()
                    papers = []
                    
                    for pmid in pmids:
                        item = summary_data.get("result", {}).get(pmid, {})
                        if not item:
                            continue
                        
                        # Extract authors
                        authors = [author.get("name", "") for author in item.get("authors", [])]
                        
                        paper = {
                            "id": f"PMID:{pmid}",
                            "title": item.get("title", ""),
                            "authors": authors,
                            "abstract": "",  # PubMed summary doesn't include abstract
                            "year": int(item.get("pubdate", "").split()[0]) if item.get("pubdate") else None,
                            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                            "pdf_url": None,
                            "citations": 0,
                            "venue": item.get("source", "PubMed")
                        }
                        papers.append(paper)
                    
                    logger.info(f"Found {len(papers)} papers on PubMed for query: {query}")
                    return papers
                    
    except Exception as e:
        logger.error(f"PubMed search failed: {e}")
        return []


@tool_registry.register(
    name="pdf_parser",
    description="Download and parse PDF content",
    required_params=["pdf_url"]
)
async def pdf_parser(pdf_url: str, max_pages: int = 50) -> Optional[str]:
    """
    Download and extract text from PDF
    
    Args:
        pdf_url: URL to PDF file
        max_pages: Maximum pages to parse
        
    Returns:
        Extracted text content or None if failed
    """
    try:
        import PyPDF2
        import io
        
        async with aiohttp.ClientSession() as session:
            async with session.get(pdf_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    logger.warning(f"Failed to download PDF from {pdf_url}")
                    return None
                
                pdf_content = await response.read()
        
        # Parse PDF
        pdf_file = io.BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text_content = []
        num_pages = min(len(pdf_reader.pages), max_pages)
        
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            if text:
                text_content.append(text)
        
        full_text = "\n\n".join(text_content)
        
        # Basic cleaning
        full_text = full_text.replace("\n", " ").replace("  ", " ")
        
        logger.info(f"Successfully parsed PDF: {len(full_text)} characters extracted")
        return full_text
        
    except Exception as e:
        logger.error(f"PDF parsing failed for {pdf_url}: {e}")
        return None
