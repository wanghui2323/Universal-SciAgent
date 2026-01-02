"""Domain Manager for managing research domain configurations"""
import yaml
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..core.config import settings

logger = logging.getLogger(__name__)


class DomainConfig:
    """Configuration for a research domain"""
    
    def __init__(self, name: str, config_data: Dict[str, Any]):
        self.name = name
        self.display_name = config_data.get("name", name)
        self.description = config_data.get("description", "")
        self.tools = config_data.get("tools", [])
        self.prompts = config_data.get("prompts", {})
        self.methodology_template = config_data.get("methodology_template", "")
        self.keywords = config_data.get("keywords", [])
        
    def get_prompt(self, prompt_type: str) -> str:
        """Get prompt template for a specific type"""
        return self.prompts.get(prompt_type, "")
    
    def get_tools(self) -> List[str]:
        """Get list of tools for this domain"""
        return self.tools
    
    def __repr__(self):
        return f"DomainConfig(name={self.name}, display_name={self.display_name})"


class DomainManager:
    """
    Manager for research domain configurations
    
    Supports 5 domains:
    - computer_science
    - materials_science
    - biomedical
    - physics
    - chemistry
    """
    
    SUPPORTED_DOMAINS = [
        "computer_science",
        "materials_science",
        "biomedical",
        "physics",
        "chemistry"
    ]
    
    def __init__(self, domains_dir: Optional[Path] = None):
        self.domains_dir = domains_dir or settings.domains_dir
        self._domains: Dict[str, DomainConfig] = {}
        self._load_domains()
    
    def _load_domains(self):
        """Load all domain configurations from YAML files"""
        if not self.domains_dir.exists():
            logger.warning(f"Domains directory not found: {self.domains_dir}")
            return
        
        for domain_name in self.SUPPORTED_DOMAINS:
            config_file = self.domains_dir / f"{domain_name}.yaml"
            if config_file.exists():
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        config_data = yaml.safe_load(f)
                    
                    self._domains[domain_name] = DomainConfig(domain_name, config_data)
                    logger.info(f"Loaded domain configuration: {domain_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to load domain {domain_name}: {e}")
            else:
                logger.warning(f"Domain configuration file not found: {config_file}")
    
    def get_domain(self, domain_name: str) -> Optional[DomainConfig]:
        """Get configuration for a specific domain"""
        if domain_name not in self._domains:
            logger.warning(f"Domain '{domain_name}' not found. Available domains: {self.list_domains()}")
            return None
        return self._domains[domain_name]
    
    def get_merged_config(self, domain_names: List[str]) -> Dict[str, Any]:
        """
        Get merged configuration for multiple domains (for cross-disciplinary tasks)
        
        Args:
            domain_names: List of domain names
            
        Returns:
            Merged configuration with combined tools and prompts
        """
        if not domain_names:
            raise ValueError("At least one domain must be specified")
        
        # Collect all tools (deduplicate)
        all_tools = set()
        all_prompts = {}
        all_methodologies = []
        all_keywords = set()
        
        for domain_name in domain_names:
            domain = self.get_domain(domain_name)
            if not domain:
                continue
            
            all_tools.update(domain.tools)
            
            # Merge prompts by appending domain-specific content
            for prompt_type, prompt_content in domain.prompts.items():
                if prompt_type not in all_prompts:
                    all_prompts[prompt_type] = []
                all_prompts[prompt_type].append(f"[{domain.display_name}]\n{prompt_content}")
            
            if domain.methodology_template:
                all_methodologies.append(f"## {domain.display_name} Methodology\n{domain.methodology_template}")
            
            all_keywords.update(domain.keywords)
        
        # Combine prompts
        combined_prompts = {}
        for prompt_type, prompt_list in all_prompts.items():
            combined_prompts[prompt_type] = "\n\n".join(prompt_list)
        
        return {
            "domains": domain_names,
            "tools": list(all_tools),
            "prompts": combined_prompts,
            "methodology_template": "\n\n".join(all_methodologies),
            "keywords": list(all_keywords)
        }
    
    def list_domains(self) -> List[str]:
        """List all available domains"""
        return list(self._domains.keys())
    
    def is_cross_domain(self, domain_names: List[str]) -> bool:
        """Check if task involves multiple domains"""
        return len(domain_names) > 1
    
    def suggest_domains(self, keywords: List[str]) -> List[str]:
        """
        Suggest relevant domains based on keywords
        
        Args:
            keywords: List of research keywords
            
        Returns:
            List of suggested domain names (sorted by relevance)
        """
        keyword_set = set(kw.lower() for kw in keywords)
        domain_scores = {}
        
        for domain_name, domain in self._domains.items():
            domain_keywords = set(kw.lower() for kw in domain.keywords)
            overlap = keyword_set & domain_keywords
            domain_scores[domain_name] = len(overlap)
        
        # Sort by score (descending)
        suggested = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return domains with score > 0
        return [domain for domain, score in suggested if score > 0]


# Global domain manager instance
domain_manager = DomainManager()
