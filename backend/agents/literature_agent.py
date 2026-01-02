"""Literature Agent for paper search and knowledge extraction"""
import asyncio
import logging
from typing import Dict, Any, List
import chromadb
from chromadb.config import Settings as ChromaSettings

from .base_agent import BaseAgent
from ..core.models import AgentOutput, Paper, LiteratureContext
from ..core.config import settings
from ..tools.registry import tool_registry

logger = logging.getLogger(__name__)


class LiteratureAgent(BaseAgent):
    """
    Literature Agent responsibilities:
    1. Multi-source literature search (arXiv, Semantic Scholar, PubMed)
    2. PDF parsing and full-text extraction
    3. Knowledge extraction and vectorization
    4. Literature trend analysis
    """
    
    def __init__(self):
        super().__init__(name="LiteratureAgent", description="Literature search and knowledge extraction")
        
        # Initialize ChromaDB for vector storage
        self.chroma_client = chromadb.Client(ChromaSettings(
            persist_directory=settings.chroma_persist_dir,
            anonymized_telemetry=False
        ))
        
        # Create or get collection
        try:
            self.collection = self.chroma_client.get_or_create_collection(
                name="research_papers",
                metadata={"description": "Research paper embeddings"}
            )
            self.logger.info("ChromaDB collection initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB: {e}")
            self.collection = None
    
    async def execute(self, context: Dict[str, Any]) -> AgentOutput:
        """
        Execute literature search and analysis
        
        Expected context keys:
        - keywords: List[str] - Search keywords
        - domains: List[str] - Research domains
        - max_papers: int - Maximum papers to retrieve
        - time_range: Optional[tuple] - (start_year, end_year)
        """
        self.log_progress("Starting literature search...")
        
        keywords = context.get("keywords", [])
        domains = context.get("domains", [])
        max_papers = context.get("max_papers", 20)
        time_range = context.get("time_range")
        
        # Build search query
        query = " ".join(keywords)
        
        # Search papers from multiple sources
        papers = await self._search_papers(query, domains, max_papers, time_range)
        
        # Download and parse PDFs (for top papers)
        papers = await self._parse_pdfs(papers, max_pdfs=10)
        
        # Store in vector database
        if self.collection and papers:
            await self._store_papers(papers)
        
        # Generate trend analysis
        trend_summary = await self._analyze_trends(papers, query)
        
        # Identify research gaps
        research_gaps = await self._identify_gaps(papers, query)
        
        # Create literature context
        literature_context = LiteratureContext(
            paper_ids=[p["id"] for p in papers],
            summary=trend_summary,
            key_methods=self._extract_key_methods(papers),
            research_gaps=research_gaps,
            technical_bottlenecks=self._extract_bottlenecks(papers)
        )
        
        output = {
            "papers": papers,
            "literature_context": literature_context.dict(),
            "stats": {
                "total_papers": len(papers),
                "with_full_text": sum(1 for p in papers if p.get("full_text"))
            }
        }
        
        self.log_progress(f"✅ Found {len(papers)} papers")
        
        return self.create_output(
            action="literature_search",
            output=output,
            metadata={"query": query, "domains": domains}
        )
    
    async def _search_papers(
        self,
        query: str,
        domains: List[str],
        max_papers: int,
        time_range: Any
    ) -> List[Dict[str, Any]]:
        """Search papers from multiple sources"""
        papers_by_source = {}
        
        # Determine which sources to use based on domain
        sources = []
        if any(d in ["computer_science", "physics", "mathematics"] for d in domains):
            sources.append("arxiv")
        if any(d in ["biomedical"] for d in domains):
            sources.append("pubmed")
        sources.append("semantic_scholar")  # Always include Semantic Scholar
        
        # Search from each source
        tasks = []
        for source in sources:
            if source == "arxiv":
                tasks.append(tool_registry.call("arxiv_search", query=query, max_results=max_papers // 2))
            elif source == "semantic_scholar":
                tasks.append(tool_registry.call(
                    "semantic_scholar_search",
                    query=query,
                    max_results=max_papers // 2,
                    api_key=settings.semantic_scholar_api_key
                ))
            elif source == "pubmed":
                tasks.append(tool_registry.call("pubmed_search", query=query, max_results=max_papers // 2))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Merge results
        all_papers = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.warning(f"Source {sources[i]} failed: {result}")
                continue
            if result:
                all_papers.extend(result)
        
        # Deduplicate by title similarity
        unique_papers = self._deduplicate_papers(all_papers)
        
        # Sort by citations and take top N
        unique_papers.sort(key=lambda p: p.get("citations", 0), reverse=True)
        
        return unique_papers[:max_papers]
    
    def _deduplicate_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate papers by ID or title"""
        seen_ids = set()
        seen_titles = set()
        unique = []
        
        for paper in papers:
            # Check by ID
            paper_id = paper.get("id", "")
            if paper_id and paper_id in seen_ids:
                continue
            
            # Check by title (lowercase, remove special chars)
            title = paper.get("title", "").lower().strip()
            if title in seen_titles:
                continue
            
            seen_ids.add(paper_id)
            seen_titles.add(title)
            unique.append(paper)
        
        return unique
    
    async def _parse_pdfs(self, papers: List[Dict[str, Any]], max_pdfs: int = 10) -> List[Dict[str, Any]]:
        """Parse PDFs for top papers"""
        self.log_progress(f"Parsing PDFs for top {max_pdfs} papers...")
        
        # Select top papers with PDF URLs
        papers_with_pdf = [p for p in papers if p.get("pdf_url")][:max_pdfs]
        
        # Parse PDFs in parallel
        tasks = [
            tool_registry.call("pdf_parser", pdf_url=p["pdf_url"])
            for p in papers_with_pdf
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Add full text to papers
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.warning(f"PDF parsing failed: {result}")
                papers_with_pdf[i]["full_text"] = None
            else:
                papers_with_pdf[i]["full_text"] = result
        
        return papers
    
    async def _store_papers(self, papers: List[Dict[str, Any]]):
        """Store papers in vector database"""
        if not self.collection:
            return
        
        self.log_progress("Storing papers in vector database...")
        
        try:
            documents = []
            metadatas = []
            ids = []
            
            for paper in papers:
                # Use abstract or full text
                text = paper.get("full_text") or paper.get("abstract", "")
                if not text:
                    continue
                
                documents.append(text)
                metadatas.append({
                    "title": paper.get("title", ""),
                    "authors": ", ".join(paper.get("authors", [])),
                    "year": str(paper.get("year", "")),
                    "url": paper.get("url", "")
                })
                ids.append(paper["id"])
            
            if documents:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                self.logger.info(f"Stored {len(documents)} papers in ChromaDB")
                
        except Exception as e:
            self.logger.error(f"Failed to store papers: {e}")
    
    async def _analyze_trends(self, papers: List[Dict[str, Any]], query: str) -> str:
        """Generate trend analysis summary"""
        if not papers:
            return "No papers found for analysis."
        
        # Prepare context for LLM
        papers_summary = "\n\n".join([
            f"Title: {p.get('title')}\nYear: {p.get('year')}\nAbstract: {p.get('abstract', '')[:300]}..."
            for p in papers[:10]
        ])
        
        system_prompt = """你是资深的科研领域专家。请基于提供的论文列表，生成一份500字的研究趋势总结。

总结应包括：
1. 主要研究方向（3-5个）
2. 代表性方法
3. 当前技术瓶颈
4. 未来研究机会

使用学术语言，简洁明了。"""
        
        user_prompt = f"""研究主题: {query}

论文列表:
{papers_summary}

请生成研究趋势总结："""
        
        try:
            trend_summary = await self.call_llm(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=1000
            )
            return trend_summary
        except Exception as e:
            self.logger.error(f"Failed to generate trend analysis: {e}")
            return "Failed to generate trend analysis."
    
    async def _identify_gaps(self, papers: List[Dict[str, Any]], query: str) -> str:
        """Identify research gaps"""
        if not papers:
            return "No papers available for gap analysis."
        
        system_prompt = """你是资深的科研领域专家。请基于提供的论文，识别当前研究的空白和未解决的问题。

输出200字，包括：
1. 主要研究空白（2-3个）
2. 未充分探索的方向
3. 潜在的突破点"""
        
        papers_summary = "\n\n".join([
            f"Title: {p.get('title')}\nAbstract: {p.get('abstract', '')[:200]}..."
            for p in papers[:10]
        ])
        
        user_prompt = f"""研究主题: {query}

论文摘要:
{papers_summary}

请识别研究空白："""
        
        try:
            gaps = await self.call_llm(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=500
            )
            return gaps
        except Exception as e:
            self.logger.error(f"Failed to identify gaps: {e}")
            return "Failed to identify research gaps."
    
    def _extract_key_methods(self, papers: List[Dict[str, Any]]) -> List[str]:
        """Extract key methods from paper titles/abstracts"""
        # Simple keyword extraction (can be enhanced with NLP)
        methods = set()
        keywords = [
            "method", "approach", "algorithm", "technique", "framework",
            "model", "network", "architecture", "strategy"
        ]
        
        for paper in papers[:10]:
            title = paper.get("title", "").lower()
            abstract = paper.get("abstract", "").lower()
            
            # Extract potential method names (simple heuristic)
            for kw in keywords:
                if kw in title or kw in abstract:
                    # Extract surrounding words
                    pass
        
        return list(methods)[:5] if methods else ["Various methods"]
    
    def _extract_bottlenecks(self, papers: List[Dict[str, Any]]) -> List[str]:
        """Extract technical bottlenecks"""
        # Simple keyword-based extraction
        bottleneck_keywords = [
            "challenge", "limitation", "bottleneck", "difficulty", "issue", "problem"
        ]
        
        bottlenecks = []
        for paper in papers[:10]:
            abstract = paper.get("abstract", "").lower()
            for kw in bottleneck_keywords:
                if kw in abstract:
                    bottlenecks.append(f"Issues mentioned in {paper.get('title', 'paper')[:50]}...")
                    break
        
        return bottlenecks[:3] if bottlenecks else ["General technical challenges"]

