"""Configuration management"""
import os
from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def _normalize_env_vars():
    """
    Normalize environment variables to support both lowercase and uppercase.
    AgentKit requires lowercase env keys, but VeADK expects uppercase.
    This function maps lowercase to uppercase for VeADK compatibility.
    """
    mappings = [
        ("model_agent_name", "MODEL_AGENT_NAME"),
        ("model_agent_api_key", "MODEL_AGENT_API_KEY"),
        ("model_agent_api_base", "MODEL_AGENT_API_BASE"),
        ("model_agent_provider", "MODEL_AGENT_PROVIDER"),
        ("model_embedding_name", "MODEL_EMBEDDING_NAME"),
        ("model_embedding_api_key", "MODEL_EMBEDDING_API_KEY"),
        ("model_embedding_api_base", "MODEL_EMBEDDING_API_BASE"),
    ]
    
    for lower_key, upper_key in mappings:
        # If lowercase exists but uppercase doesn't, copy to uppercase
        if os.getenv(lower_key) and not os.getenv(upper_key):
            os.environ[upper_key] = os.getenv(lower_key)


# Normalize env vars on module load
_normalize_env_vars()


class Settings(BaseSettings):
    """Global settings for Universal-SciAgent"""
    
    # VeADK Configuration (supports both lowercase and uppercase)
    veadk_api_key: str = os.getenv("MODEL_AGENT_API_KEY") or os.getenv("model_agent_api_key", "")
    veadk_api_base: str = os.getenv("MODEL_AGENT_API_BASE") or os.getenv("model_agent_api_base", "https://ark.cn-beijing.volces.com/api/v3/")
    veadk_model: str = os.getenv("MODEL_AGENT_NAME") or os.getenv("model_agent_name", "doubao-pro-32k")
    
    # Optional: OpenAI as fallback
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Optional: Semantic Scholar API
    semantic_scholar_api_key: Optional[str] = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    
    # Database
    chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "/tmp/chromadb")
    log_dir: str = os.getenv("LOG_DIR", "/tmp/logs")
    
    # Cost Control
    max_cost_per_task: float = float(os.getenv("MAX_COST_PER_TASK", "2.0"))
    max_papers_per_search: int = int(os.getenv("MAX_PAPERS_PER_SEARCH", "20"))
    
    # Paths
    project_root: Path = Path(__file__).parent.parent.parent
    config_dir: Path = project_root / "config"
    domains_dir: Path = config_dir / "domains"
    prompts_dir: Path = config_dir / "prompts"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra env vars
    
    def validate_config(self) -> bool:
        """Validate that essential configurations are set"""
        # Check for API key in both formats
        model_api_key = (
            os.getenv("MODEL_AGENT_API_KEY") or 
            os.getenv("model_agent_api_key") or 
            self.veadk_api_key
        )
        if not model_api_key:
            raise ValueError("model_agent_api_key is required. Please set it in environment.")
        return True


# Global settings instance
settings = Settings()

