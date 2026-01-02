"""Pytest configuration and fixtures"""
import os
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables"""
    test_env = {
        'MODEL_AGENT_NAME': 'test-model',
        'MODEL_AGENT_API_KEY': 'test-api-key-12345',
        'MODEL_AGENT_API_BASE': 'https://test.example.com/api/v3/',
        'MODEL_AGENT_PROVIDER': 'openai',
        'CHROMA_PERSIST_DIR': '/tmp/test_chromadb',
        'LOG_DIR': '/tmp/test_logs',
    }
    with patch.dict(os.environ, test_env):
        yield


@pytest.fixture
def mock_veadk_agent():
    """Mock VeADK Agent for testing"""
    with patch('backend.agents.base_agent.VeADKAgent') as mock:
        mock_instance = MagicMock()
        mock_instance.run = MagicMock(return_value="Test response")
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def sample_paper():
    """Provide a sample paper for testing"""
    return {
        "id": "2301.12345",
        "title": "Test Paper Title",
        "authors": ["Author One", "Author Two"],
        "abstract": "This is a test abstract.",
        "year": 2025,
        "citations": 100,
        "venue": "arXiv",
        "source": "arxiv"
    }
