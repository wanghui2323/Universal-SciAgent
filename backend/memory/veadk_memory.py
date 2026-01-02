"""
VeADK Native Memory Management for Universal-SciAgent

This module implements memory management using VeADK's native Memory system:
- ShortTermMemory: Conversation context with session management
- LongTermMemory: Knowledge persistence with vector search

VeADK Memory Features:
- Automatic session management
- Multiple backend support (SQLite, MySQL, PostgreSQL)
- Vector search integration
- TTL and cleanup policies

Reference: https://github.com/volcengine/veadk-python
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# VeADK Native Memory Imports
from veadk.memory.short_term_memory import ShortTermMemory
from veadk.memory.long_term_memory import LongTermMemory

from ..core.config import settings

logger = logging.getLogger(__name__)


class SciAgentMemory:
    """
    Memory Management for Universal-SciAgent using VeADK Native Memory
    
    VeADK provides two memory layers:
    - ShortTermMemory: Recent conversation context with session support
    - LongTermMemory: Persistent knowledge base with vector search
    
    VeADK automatically manages:
    - Context window optimization
    - Session persistence (SQLite/MySQL/PostgreSQL)
    - Vector embedding and search
    - Memory cleanup and TTL
    
    Configuration is read from config.yaml automatically.
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize VeADK native memory system
        
        Args:
            session_id: Optional session ID for short-term memory
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self._init_memory()
    
    def _init_memory(self):
        """Initialize VeADK native memory components"""
        self.logger.info("Initializing VeADK native memory system")
        
        try:
            # Initialize ShortTermMemory
            # VeADK reads backend config from config.yaml (SQLite by default)
            self.short_term = ShortTermMemory()
            self.logger.info("VeADK ShortTermMemory initialized")
            
            # Initialize LongTermMemory
            # VeADK supports multiple backends (VikingDB, local vector store, etc.)
            self.long_term = LongTermMemory()
            self.logger.info("VeADK LongTermMemory initialized")
            
            self.logger.info("VeADK memory system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize VeADK memory: {e}")
            raise RuntimeError(f"VeADK memory initialization failed: {e}")
    
    # =========================================================================
    # Short-Term Memory (Conversation Context)
    # =========================================================================
    
    async def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a message to short-term memory
        
        Args:
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            metadata: Optional metadata
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        try:
            # VeADK ShortTermMemory uses session-based storage
            session = await self.short_term.get_session(self.session_id)
            if session:
                # Add message to session
                session.events.append(message)
                await self.short_term.update_session(session)
            else:
                # Create new session with this message
                await self.short_term.create_session(
                    session_id=self.session_id,
                    events=[message]
                )
            
            self.logger.debug(f"Added message to short-term memory: {role}")
            
        except Exception as e:
            self.logger.error(f"Failed to add message: {e}")
            raise
    
    async def get_conversation_history(
        self,
        last_n: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history from short-term memory
        
        Args:
            last_n: Get last N messages (None for all)
        
        Returns:
            List of messages
        """
        try:
            session = await self.short_term.get_session(self.session_id)
            
            if not session or not hasattr(session, 'events'):
                return []
            
            history = list(session.events)
            
            if last_n:
                history = history[-last_n:]
            
            return history
            
        except Exception as e:
            self.logger.error(f"Failed to get conversation history: {e}")
            return []
    
    async def clear_conversation(self) -> None:
        """Clear conversation history for current session"""
        try:
            await self.short_term.delete_session(self.session_id)
            self.logger.info(f"Cleared conversation history for session: {self.session_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to clear conversation: {e}")
    
    async def create_new_session(self, session_id: Optional[str] = None) -> str:
        """
        Create a new conversation session
        
        Args:
            session_id: Optional custom session ID
        
        Returns:
            New session ID
        """
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            await self.short_term.create_session(session_id=self.session_id)
            self.logger.info(f"Created new session: {self.session_id}")
            return self.session_id
            
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            raise
    
    # =========================================================================
    # Long-Term Memory (Knowledge Base)
    # =========================================================================
    
    async def store_paper(
        self,
        paper: Dict[str, Any],
        domain: Optional[str] = None
    ) -> str:
        """
        Store paper in long-term memory with vector indexing
        
        Args:
            paper: Paper metadata and content
            domain: Research domain
        
        Returns:
            Document ID
        """
        # Prepare document for vector storage
        doc_content = f"{paper.get('title', '')} {paper.get('abstract', '')}"
        doc_metadata = {
            "type": "paper",
            "paper_id": paper.get("id", ""),
            "title": paper.get("title", ""),
            "authors": ", ".join(paper.get("authors", [])),
            "year": paper.get("year"),
            "citations": paper.get("citations", 0),
            "venue": paper.get("venue", ""),
            "url": paper.get("url", ""),
            "domain": domain or "unknown",
            "stored_at": datetime.now().isoformat()
        }
        
        try:
            # VeADK LongTermMemory handles vector embedding automatically
            doc_id = await self.long_term.add(
                content=doc_content,
                metadata=doc_metadata
            )
            
            self.logger.debug(f"Stored paper in long-term memory: {doc_id}")
            return doc_id
            
        except Exception as e:
            self.logger.error(f"Failed to store paper: {e}")
            raise
    
    async def store_hypothesis(
        self,
        hypothesis: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store research hypothesis in long-term memory
        
        Args:
            hypothesis: Hypothesis content
            metadata: Optional metadata
        
        Returns:
            Document ID
        """
        doc_metadata = {
            "type": "hypothesis",
            "timestamp": datetime.now().isoformat(),
            **(metadata or {})
        }
        
        try:
            doc_id = await self.long_term.add(
                content=hypothesis,
                metadata=doc_metadata
            )
            
            self.logger.debug(f"Stored hypothesis in long-term memory: {doc_id}")
            return doc_id
            
        except Exception as e:
            self.logger.error(f"Failed to store hypothesis: {e}")
            raise
    
    async def store_knowledge(
        self,
        content: str,
        knowledge_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store general knowledge in long-term memory
        
        Args:
            content: Knowledge content
            knowledge_type: Type of knowledge
            metadata: Optional metadata
        
        Returns:
            Document ID
        """
        doc_metadata = {
            "type": knowledge_type,
            "timestamp": datetime.now().isoformat(),
            **(metadata or {})
        }
        
        try:
            doc_id = await self.long_term.add(
                content=content,
                metadata=doc_metadata
            )
            
            self.logger.debug(f"Stored knowledge in long-term memory: {doc_id}")
            return doc_id
            
        except Exception as e:
            self.logger.error(f"Failed to store knowledge: {e}")
            raise
    
    async def search_relevant(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search relevant documents from long-term memory using vector search
        
        VeADK LongTermMemory provides:
        - Semantic similarity search
        - Metadata filtering
        - Relevance scoring
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
        
        Returns:
            List of relevant documents with scores
        """
        try:
            results = await self.long_term.search(
                query=query,
                top_k=top_k,
                filter=filter_metadata
            )
            
            self.logger.debug(f"Retrieved {len(results)} relevant documents for query: {query[:50]}...")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search memory: {e}")
            return []
    
    async def get_papers_by_domain(
        self,
        domain: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get all papers for a specific domain
        
        Args:
            domain: Research domain
            limit: Maximum number of papers
        
        Returns:
            List of papers
        """
        return await self.search_relevant(
            query=domain,
            top_k=limit,
            filter_metadata={"type": "paper", "domain": domain}
        )
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get memory statistics
        
        Returns:
            Dict with statistics
        """
        try:
            # Get session count and long-term document count
            stats = {
                "session_id": self.session_id,
                "short_term_backend": "VeADK ShortTermMemory",
                "long_term_backend": "VeADK LongTermMemory",
                "framework": "VeADK Native"
            }
            
            # Try to get more detailed stats
            try:
                session = await self.short_term.get_session(self.session_id)
                if session and hasattr(session, 'events'):
                    stats["short_term_messages"] = len(session.events)
            except:
                pass
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {"error": str(e)}


# Singleton instance
_memory_instance: Optional[SciAgentMemory] = None


def get_sci_agent_memory(session_id: Optional[str] = None) -> SciAgentMemory:
    """
    Get or create the singleton memory instance
    
    Args:
        session_id: Optional session ID (only used on first call)
    
    Returns:
        SciAgentMemory instance
    """
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = SciAgentMemory(session_id=session_id)
    return _memory_instance
