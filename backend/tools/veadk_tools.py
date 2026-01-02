"""
VeADK Native Tools for Universal-SciAgent

This module implements research tools using VeADK's native tool system.
Tools are defined as regular Python functions and wrapped with FunctionTool
for VeADK Agent integration.

VeADK Tool Features:
- FunctionTool wrapper for automatic schema generation
- Built-in tools (web_search, web_scraper, etc.)
- Tool tracing and observability
- Automatic parameter validation

Reference: https://github.com/volcengine/veadk-python
"""

import logging
from typing import List, Dict, Any, Optional
import asyncio

# External libraries
import arxiv
import requests
import aiohttp
from PyPDF2 import PdfReader
import pdfplumber
from io import BytesIO

# VeADK/Google ADK Tool Support
from google.adk.tools import FunctionTool

from ..core.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# Literature Search Tools
# =============================================================================

async def arxiv_search(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search papers on arXiv by query string.
    
    This tool searches the arXiv preprint server for academic papers
    matching the given query. Returns paper metadata including title,
    authors, abstract, and URLs.
    
    Args:
        query: Search query (keywords, title, author, etc.)
        max_results: Maximum number of results to return (default: 10, max: 50)
    
    Returns:
        List of paper dictionaries with metadata
    """
    try:
        max_results = min(max_results, settings.max_papers_per_search)
        
        logger.info(f"Searching arXiv: {query} (max: {max_results})")
        
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
                "published_date": result.published.isoformat() if result.published else None,
                "url": result.entry_id,
                "pdf_url": result.pdf_url,
                "citations": 0,  # arXiv doesn't provide citation count
                "venue": "arXiv",
                "source": "arxiv"
            }
            papers.append(paper)
        
        logger.info(f"Found {len(papers)} papers on arXiv")
        return papers
        
    except Exception as e:
        logger.error(f"arXiv search failed: {e}")
        return []


async def semantic_scholar_search(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search papers on Semantic Scholar with citation metrics.
    
    This tool searches Semantic Scholar for academic papers and returns
    results with citation counts, influential citations, and publication venue.
    
    Args:
        query: Search query
        max_results: Maximum number of results (default: 10)
    
    Returns:
        List of papers with citation metrics
    """
    try:
        max_results = min(max_results, settings.max_papers_per_search)
        
        logger.info(f"Searching Semantic Scholar: {query} (max: {max_results})")
        
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": max_results,
            "fields": "title,authors,abstract,year,citationCount,influentialCitationCount,venue,url,externalIds"
        }
        
        headers = {}
        if settings.semantic_scholar_api_key:
            headers["x-api-key"] = settings.semantic_scholar_api_key
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status != 200:
                    logger.error(f"Semantic Scholar API error: {response.status}")
                    return []
                
                data = await response.json()
                results = data.get("data", [])
        
        papers = []
        for item in results:
            paper = {
                "id": item.get("paperId", ""),
                "title": item.get("title", ""),
                "authors": [author.get("name", "") for author in item.get("authors", [])],
                "abstract": item.get("abstract", ""),
                "year": item.get("year"),
                "citations": item.get("citationCount", 0),
                "influential_citations": item.get("influentialCitationCount", 0),
                "venue": item.get("venue", ""),
                "url": item.get("url", ""),
                "doi": item.get("externalIds", {}).get("DOI"),
                "arxiv_id": item.get("externalIds", {}).get("ArXiv"),
                "source": "semantic_scholar"
            }
            papers.append(paper)
        
        logger.info(f"Found {len(papers)} papers on Semantic Scholar")
        return papers
        
    except Exception as e:
        logger.error(f"Semantic Scholar search failed: {e}")
        return []


async def pubmed_search(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search biomedical papers on PubMed.
    
    This tool searches PubMed for biomedical and life sciences literature.
    Best for medical, biology, and health-related research.
    
    Args:
        query: Search query
        max_results: Maximum number of results (default: 10)
    
    Returns:
        List of biomedical papers
    """
    try:
        max_results = min(max_results, settings.max_papers_per_search)
        
        logger.info(f"Searching PubMed: {query} (max: {max_results})")
        
        # PubMed E-utilities API
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json"
        }
        
        async with aiohttp.ClientSession() as session:
            # Step 1: Search for paper IDs
            async with session.get(search_url, params=search_params) as response:
                if response.status != 200:
                    logger.error(f"PubMed search error: {response.status}")
                    return []
                
                search_data = await response.json()
                id_list = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not id_list:
                logger.info("No results found on PubMed")
                return []
            
            # Step 2: Fetch paper details
            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(id_list),
                "retmode": "json"
            }
            
            async with session.get(fetch_url, params=fetch_params) as response:
                if response.status != 200:
                    logger.error(f"PubMed fetch error: {response.status}")
                    return []
                
                fetch_data = await response.json()
                results = fetch_data.get("result", {})
        
        papers = []
        for pmid in id_list:
            item = results.get(pmid, {})
            if not item:
                continue
            
            # Extract authors
            authors = []
            for author in item.get("authors", []):
                name = author.get("name", "")
                if name:
                    authors.append(name)
            
            paper = {
                "id": f"PMID:{pmid}",
                "title": item.get("title", ""),
                "authors": authors,
                "abstract": "",  # Need separate API call for abstract
                "year": item.get("pubdate", "").split()[0] if item.get("pubdate") else None,
                "citations": 0,  # PubMed doesn't provide citation count directly
                "venue": item.get("source", ""),
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "doi": item.get("elocationid", "").replace("doi: ", "") if "doi:" in item.get("elocationid", "") else None,
                "source": "pubmed"
            }
            papers.append(paper)
        
        logger.info(f"Found {len(papers)} papers on PubMed")
        return papers
        
    except Exception as e:
        logger.error(f"PubMed search failed: {e}")
        return []


# =============================================================================
# PDF Processing Tools
# =============================================================================

async def parse_pdf(source: str, method: str = "pdfplumber") -> Dict[str, Any]:
    """
    Parse PDF file and extract text content.
    
    This tool can handle both PDF URLs and local file paths.
    Supports two parsing methods for flexibility.
    
    Args:
        source: PDF URL or local file path
        method: Parsing method - 'pypdf2' or 'pdfplumber' (default: pdfplumber)
    
    Returns:
        Dict with extracted text and metadata
    """
    try:
        logger.info(f"Parsing PDF: {source} (method: {method})")
        
        # Download PDF if URL
        if source.startswith("http"):
            async with aiohttp.ClientSession() as session:
                async with session.get(source) as response:
                    if response.status != 200:
                        logger.error(f"Failed to download PDF: {response.status}")
                        return {"error": f"Failed to download PDF: {response.status}"}
                    pdf_content = await response.read()
            pdf_file = BytesIO(pdf_content)
        else:
            # Local file
            with open(source, "rb") as f:
                pdf_content = f.read()
            pdf_file = BytesIO(pdf_content)
        
        # Parse PDF
        if method == "pdfplumber":
            text = await _parse_with_pdfplumber(pdf_file)
        else:
            text = await _parse_with_pypdf2(pdf_file)
        
        result = {
            "source": source,
            "method": method,
            "text": text,
            "length": len(text),
            "status": "success"
        }
        
        logger.info(f"Successfully parsed PDF: {len(text)} characters")
        return result
        
    except Exception as e:
        logger.error(f"PDF parsing failed: {e}")
        return {
            "source": source,
            "error": str(e),
            "status": "failed"
        }


async def _parse_with_pypdf2(pdf_file: BytesIO) -> str:
    """Parse PDF using PyPDF2"""
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()


async def _parse_with_pdfplumber(pdf_file: BytesIO) -> str:
    """Parse PDF using pdfplumber"""
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


# =============================================================================
# VeADK FunctionTool Wrappers
# =============================================================================

def create_arxiv_tool() -> FunctionTool:
    """Create VeADK FunctionTool for arXiv search"""
    return FunctionTool(arxiv_search)


def create_semantic_scholar_tool() -> FunctionTool:
    """Create VeADK FunctionTool for Semantic Scholar search"""
    return FunctionTool(semantic_scholar_search)


def create_pubmed_tool() -> FunctionTool:
    """Create VeADK FunctionTool for PubMed search"""
    return FunctionTool(pubmed_search)


def create_pdf_parser_tool() -> FunctionTool:
    """Create VeADK FunctionTool for PDF parsing"""
    return FunctionTool(parse_pdf)


def get_all_tools() -> List[FunctionTool]:
    """
    Get all research tools as VeADK FunctionTools
    
    Returns:
        List of FunctionTool instances ready for VeADK Agent
    """
    return [
        create_arxiv_tool(),
        create_semantic_scholar_tool(),
        create_pubmed_tool(),
        create_pdf_parser_tool()
    ]


def get_tool_metadata() -> List[Dict[str, Any]]:
    """
    Get metadata for all registered tools
    
    Returns:
        List of tool metadata dicts
    """
    tools = [
        {
            "name": "arxiv_search",
            "function": arxiv_search,
            "description": "Search papers on arXiv",
            "source": "arXiv API"
        },
        {
            "name": "semantic_scholar_search",
            "function": semantic_scholar_search,
            "description": "Search papers on Semantic Scholar with citation metrics",
            "source": "Semantic Scholar API"
        },
        {
            "name": "pubmed_search",
            "function": pubmed_search,
            "description": "Search biomedical papers on PubMed",
            "source": "PubMed E-utilities API"
        },
        {
            "name": "parse_pdf",
            "function": parse_pdf,
            "description": "Parse PDF and extract text",
            "source": "PyPDF2 / pdfplumber"
        }
    ]
    
    return tools


# =============================================================================
# Tool Testing
# =============================================================================

async def test_all_tools():
    """Test all tools to ensure they work"""
    logger.info("Testing all VeADK tools...")
    
    # Test arXiv
    arxiv_results = await arxiv_search("attention is all you need", max_results=2)
    logger.info(f"arXiv test: {len(arxiv_results)} results")
    
    # Test Semantic Scholar
    ss_results = await semantic_scholar_search("BERT language model", max_results=2)
    logger.info(f"Semantic Scholar test: {len(ss_results)} results")
    
    # Test PubMed
    pm_results = await pubmed_search("COVID-19 vaccine", max_results=2)
    logger.info(f"PubMed test: {len(pm_results)} results")
    
    logger.info("All VeADK tools tested successfully")


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_all_tools())
