"""
Base Agent class using VeADK Native Implementation

This module provides the base class for all agents, using VeADK's native
Agent and Runner capabilities.

Reference: https://github.com/volcengine/veadk-python
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

# VeADK Native Imports
from veadk import Agent as VeADKAgent, Runner as VeADKRunner

# Google ADK Tools (used by VeADK internally)
from google.adk.tools import FunctionTool

from ..core.models import AgentOutput
from ..core.config import settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all agents using VeADK Native Implementation
    
    VeADK provides:
    - LLM Agent with automatic config.yaml reading
    - Tool integration via FunctionTool
    - Tracing and observability
    - Cost tracking
    
    Reference: https://github.com/volcengine/veadk-python
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        instruction: Optional[str] = None,
        tools: Optional[List[Callable]] = None
    ):
        """
        Initialize agent with VeADK
        
        Args:
            name: Agent name
            description: Agent description
            instruction: System instruction for the agent
            tools: List of tool functions to register
        """
        self.name = name
        self.description = description
        self.instruction = instruction
        self.tools = tools or []
        self.logger = logging.getLogger(f"agent.{name}")
        
        # Initialize VeADK Agent
        # VeADK reads configuration from config.yaml automatically
        self.veadk_agent = None
        self._init_veadk_agent()
    
    def _init_veadk_agent(self):
        """Initialize VeADK Agent with proper configuration"""
        try:
            # Convert tool functions to FunctionTool if provided
            veadk_tools = []
            for tool_func in self.tools:
                if callable(tool_func):
                    veadk_tools.append(FunctionTool(tool_func))
            
            # Create VeADK Agent
            # VeADK Agent automatically reads model config from config.yaml
            self.veadk_agent = VeADKAgent(
                name=self.name,
                description=self.description,
                instruction=self.instruction or self._get_default_instruction(),
                tools=veadk_tools if veadk_tools else None
            )
            
            self.logger.info(f"Initialized {self.name} with VeADK Agent (native)")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize VeADK Agent: {e}")
            raise RuntimeError(f"VeADK Agent initialization failed: {e}")
    
    def _get_default_instruction(self) -> str:
        """Get default instruction based on agent name"""
        return f"You are {self.name}, a helpful research assistant. {self.description}"
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> AgentOutput:
        """
        Execute agent's main task
        
        Args:
            context: Input context dictionary containing task parameters and upstream outputs
            
        Returns:
            AgentOutput containing execution results
        """
        pass
    
    async def run(self, prompt: str) -> str:
        """
        Run the agent with a prompt using VeADK's native run method
        
        Args:
            prompt: User prompt
            
        Returns:
            Generated response text
        """
        try:
            if not self.veadk_agent:
                raise ValueError("VeADK Agent not initialized. Please check config.yaml")
            
            # Use VeADK Agent's native run_async method
            response = await self.veadk_agent.run_async(prompt)
            
            # Extract text from response
            if hasattr(response, 'content'):
                return response.content
            elif isinstance(response, dict):
                return response.get("content", str(response))
            else:
                return str(response)
                
        except Exception as e:
            self.logger.error(f"VeADK Agent run failed: {e}")
            raise
    
    async def call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> str:
        """
        Call LLM through VeADK Agent (compatibility method)
        
        Note: max_tokens and temperature are configured in config.yaml
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (will be prepended to prompt)
            max_tokens: Maximum tokens (configured in config.yaml)
            temperature: Temperature (configured in config.yaml)
            
        Returns:
            Generated text
        """
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        return await self.run(full_prompt)
    
    def create_output(
        self,
        action: str,
        output: Any,
        status: str = "success",
        metadata: Optional[Dict[str, Any]] = None,
        cost_usd: float = 0.0
    ) -> AgentOutput:
        """Create AgentOutput object"""
        return AgentOutput(
            agent_name=self.name,
            action=action,
            timestamp=datetime.now(),
            status=status,
            output=output,
            metadata=metadata or {},
            cost_usd=cost_usd
        )
    
    def log_progress(self, message: str):
        """Log progress message"""
        self.logger.info(message)
        print(f"[{self.name}] {message}")
