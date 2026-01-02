"""Tests for VeADK Native memory module"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestSciAgentMemory:
    """Test SciAgentMemory class with VeADK Native Memory"""
    
    def test_memory_import(self):
        """Test that memory module can be imported"""
        from backend.memory.veadk_memory import SciAgentMemory
        assert SciAgentMemory is not None
    
    @patch('backend.memory.veadk_memory.ShortTermMemory')
    @patch('backend.memory.veadk_memory.LongTermMemory')
    def test_memory_initialization(self, mock_ltm, mock_stm):
        """Test memory initialization with VeADK mocked"""
        from backend.memory.veadk_memory import SciAgentMemory
        
        mock_stm.return_value = MagicMock()
        mock_ltm.return_value = MagicMock()
        
        memory = SciAgentMemory()
        
        assert memory is not None
        assert memory.short_term is not None
        assert memory.long_term is not None
    
    @patch('backend.memory.veadk_memory.ShortTermMemory')
    @patch('backend.memory.veadk_memory.LongTermMemory')
    def test_memory_has_required_methods(self, mock_ltm, mock_stm):
        """Test that memory has required methods"""
        from backend.memory.veadk_memory import SciAgentMemory
        
        mock_stm.return_value = MagicMock()
        mock_ltm.return_value = MagicMock()
        
        memory = SciAgentMemory()
        
        assert hasattr(memory, 'add_message')
        assert hasattr(memory, 'get_conversation_history')
        assert hasattr(memory, 'store_paper')
        assert hasattr(memory, 'store_hypothesis')
        assert hasattr(memory, 'store_knowledge')
        assert hasattr(memory, 'search_relevant')
        assert hasattr(memory, 'get_papers_by_domain')
        assert hasattr(memory, 'get_statistics')
    
    @patch('backend.memory.veadk_memory.ShortTermMemory')
    @patch('backend.memory.veadk_memory.LongTermMemory')
    def test_memory_session_id(self, mock_ltm, mock_stm):
        """Test memory session ID"""
        from backend.memory.veadk_memory import SciAgentMemory
        
        mock_stm.return_value = MagicMock()
        mock_ltm.return_value = MagicMock()
        
        memory = SciAgentMemory(session_id="test_session")
        
        assert memory.session_id == "test_session"
    
    @pytest.mark.asyncio
    @patch('backend.memory.veadk_memory.ShortTermMemory')
    @patch('backend.memory.veadk_memory.LongTermMemory')
    async def test_add_message(self, mock_ltm, mock_stm):
        """Test adding a message to short-term memory"""
        from backend.memory.veadk_memory import SciAgentMemory
        
        # Setup mocks
        mock_session = MagicMock()
        mock_session.events = []
        mock_stm_instance = MagicMock()
        mock_stm_instance.get_session = AsyncMock(return_value=mock_session)
        mock_stm_instance.update_session = AsyncMock()
        mock_stm.return_value = mock_stm_instance
        mock_ltm.return_value = MagicMock()
        
        memory = SciAgentMemory()
        
        await memory.add_message(role="user", content="Test message")
        
        # Verify session was updated
        mock_stm_instance.update_session.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('backend.memory.veadk_memory.ShortTermMemory')
    @patch('backend.memory.veadk_memory.LongTermMemory')
    async def test_store_paper(self, mock_ltm, mock_stm):
        """Test storing a paper in long-term memory"""
        from backend.memory.veadk_memory import SciAgentMemory
        
        # Setup mocks
        mock_ltm_instance = MagicMock()
        mock_ltm_instance.add = AsyncMock(return_value="doc_123")
        mock_ltm.return_value = mock_ltm_instance
        mock_stm.return_value = MagicMock()
        
        memory = SciAgentMemory()
        
        paper = {
            "id": "arxiv:2301.00001",
            "title": "Test Paper",
            "abstract": "This is a test paper",
            "authors": ["Author One", "Author Two"],
            "year": 2023
        }
        
        doc_id = await memory.store_paper(paper, domain="computer_science")
        
        assert doc_id == "doc_123"
        mock_ltm_instance.add.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('backend.memory.veadk_memory.ShortTermMemory')
    @patch('backend.memory.veadk_memory.LongTermMemory')
    async def test_search_relevant(self, mock_ltm, mock_stm):
        """Test searching for relevant documents"""
        from backend.memory.veadk_memory import SciAgentMemory
        
        # Setup mocks
        mock_results = [
            {"content": "Test content", "metadata": {"type": "paper"}, "score": 0.9}
        ]
        mock_ltm_instance = MagicMock()
        mock_ltm_instance.search = AsyncMock(return_value=mock_results)
        mock_ltm.return_value = mock_ltm_instance
        mock_stm.return_value = MagicMock()
        
        memory = SciAgentMemory()
        
        results = await memory.search_relevant(query="machine learning", top_k=5)
        
        assert len(results) == 1
        assert results[0]["score"] == 0.9
