"""Tests for configuration module"""
import os
import pytest
from unittest.mock import patch


class TestSettings:
    """Test Settings class"""
    
    def test_settings_import(self):
        """Test that settings can be imported"""
        from backend.core.config import settings
        assert settings is not None
    
    def test_settings_has_required_attributes(self):
        """Test that settings has required attributes"""
        from backend.core.config import settings
        
        assert hasattr(settings, 'veadk_api_key')
        assert hasattr(settings, 'veadk_api_base')
        assert hasattr(settings, 'veadk_model')
        assert hasattr(settings, 'chroma_persist_dir')
        assert hasattr(settings, 'max_cost_per_task')
        assert hasattr(settings, 'max_papers_per_search')
    
    def test_default_values(self):
        """Test default values are set correctly"""
        from backend.core.config import settings
        
        assert isinstance(settings.max_cost_per_task, float)
        assert isinstance(settings.max_papers_per_search, int)


class TestEnvNormalization:
    """Test environment variable normalization"""
    
    def test_normalize_function_exists(self):
        """Test that normalization function exists"""
        from backend.core.config import _normalize_env_vars
        assert callable(_normalize_env_vars)
