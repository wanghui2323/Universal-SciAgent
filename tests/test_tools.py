"""Tests for tool modules"""
import pytest


class TestVeadkTools:
    """Test VeADK tools"""
    
    def test_tools_module_import(self):
        """Test that tools module can be imported"""
        from backend.tools import veadk_tools
        assert veadk_tools is not None
    
    def test_get_all_tools(self):
        """Test get_all_tools function"""
        from backend.tools.veadk_tools import get_all_tools
        
        tools = get_all_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0
    
    def test_arxiv_search_exists(self):
        """Test that arxiv_search function exists"""
        from backend.tools.veadk_tools import arxiv_search
        assert callable(arxiv_search)
    
    def test_semantic_scholar_search_exists(self):
        """Test that semantic_scholar_search function exists"""
        from backend.tools.veadk_tools import semantic_scholar_search
        assert callable(semantic_scholar_search)


class TestToolRegistry:
    """Test tool registry functionality"""
    
    def test_registry_import(self):
        """Test that registry can be imported"""
        from backend.tools.registry import tool_registry
        assert tool_registry is not None
    
    def test_registry_has_tools(self):
        """Test that registry has registered tools"""
        from backend.tools.registry import tool_registry
        
        tools = tool_registry.list_tools()
        assert isinstance(tools, list)
