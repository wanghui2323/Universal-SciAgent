"""
Universal-SciAgent System - Based on VeADK Native Multi-Agent

This module implements the complete multi-agent system using VeADK's native
capabilities for agent coordination, memory, and tool integration.

VeADK Native Features Used:
- veadk.Agent: LLM Agent with automatic config reading
- veadk.Runner: Agent execution with session management
- veadk.agents.SequentialAgent: Sequential multi-agent coordination
- veadk.agents.ParallelAgent: Parallel multi-agent execution
- veadk.memory.ShortTermMemory: Conversation context
- veadk.memory.LongTermMemory: Knowledge persistence

Reference: https://github.com/volcengine/veadk-python
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from pathlib import Path

# VeADK Native Imports
from veadk import Agent, Runner
from veadk.agents.sequential_agent import SequentialAgent
from veadk.agents.parallel_agent import ParallelAgent
from veadk.memory.short_term_memory import ShortTermMemory
from veadk.memory.long_term_memory import LongTermMemory

# Google ADK Tools (used by VeADK)
from google.adk.tools import FunctionTool

from ..core.models import Task, AgentOutput
from ..core.config import settings
from ..utils.domain_manager import DomainManager
from ..tools.veadk_tools import (
    arxiv_search,
    semantic_scholar_search,
    pubmed_search,
    parse_pdf
)

logger = logging.getLogger(__name__)


async def run_agent_with_runner(agent: Agent, prompt: str, session_id: Optional[str] = None) -> str:
    """
    Run a VeADK Agent using Runner to get the complete response.
    
    VeADK's Agent.run_async returns an async generator, so we need to use
    Runner.run to get the final result as a string.
    
    Args:
        agent: VeADK Agent instance
        prompt: User prompt
        session_id: Optional session ID
    
    Returns:
        Complete response text
    """
    try:
        # Create a Runner for the agent
        runner = Runner(agent=agent)
        
        # Generate session ID if not provided
        if not session_id:
            session_id = f"session-{uuid.uuid4().hex[:8]}"
        
        # Runner.run is also async, need to await it
        result = await runner.run(
            messages=prompt,
            user_id="sci_agent_user",
            session_id=session_id
        )
        
        # Extract text from result
        if hasattr(result, 'content'):
            return str(result.content)
        elif isinstance(result, dict):
            return result.get('content', str(result))
        else:
            return str(result)
            
    except Exception as e:
        logger.error(f"Runner execution failed: {e}")
        raise


class UniversalSciAgentSystem:
    """
    Universal Scientific Research Agent System using VeADK Native Multi-Agent
    
    Architecture:
    - Master Agent (SequentialAgent): Coordinates research workflow
    - Literature Agent: Paper search and analysis with tool integration
    - Hypothesis Agent: Research hypothesis generation
    - Experiment Design Agent: Experiment planning
    - Writing Agent: Report generation
    
    VeADK Features:
    - Multi-agent coordination via SequentialAgent/ParallelAgent
    - Automatic memory management (short-term + long-term)
    - Tool integration via FunctionTool
    - Cost tracking and observability
    """
    
    def __init__(self):
        """Initialize the multi-agent system using VeADK native capabilities"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.domain_manager = DomainManager()
        
        self.logger.info("Initializing Universal-SciAgent with VeADK Native Multi-Agent...")
        
        # Initialize VeADK components
        self._init_memory()
        self._init_specialist_agents()
        self._init_coordinator()
        
        self.logger.info("Universal-SciAgent initialized successfully with VeADK")
    
    def _init_memory(self):
        """Initialize VeADK native memory system"""
        self.logger.info("Initializing VeADK memory system...")
        
        # Short-term memory for conversation context
        self.short_term_memory = ShortTermMemory()
        
        # Long-term memory for knowledge persistence
        self.long_term_memory = LongTermMemory()
        
        self.logger.info("VeADK memory system initialized")
    
    def _init_specialist_agents(self):
        """Initialize specialist agents using VeADK Agent"""
        self.logger.info("Initializing specialist agents...")
        
        # Literature Agent with search tools
        literature_tools = [
            FunctionTool(arxiv_search),
            FunctionTool(semantic_scholar_search),
            FunctionTool(pubmed_search),
            FunctionTool(parse_pdf)
        ]
        
        self.literature_agent = Agent(
            name="literature_agent",
            description="Specialist in paper search and literature analysis",
            instruction=self._load_prompt("literature_agent.txt"),
            tools=literature_tools
        )
        
        # Hypothesis Agent
        self.hypothesis_agent = Agent(
            name="hypothesis_agent",
            description="Specialist in generating research hypotheses",
            instruction=self._load_prompt("hypothesis_agent.txt")
        )
        
        # Experiment Design Agent
        self.experiment_agent = Agent(
            name="experiment_design_agent",
            description="Specialist in designing rigorous experiments",
            instruction=self._load_prompt("experiment_design_agent.txt")
        )
        
        # Writing Agent
        self.writing_agent = Agent(
            name="writing_agent",
            description="Specialist in scientific writing and report generation",
            instruction=self._load_prompt("writing_agent.txt")
        )
        
        self.logger.info("Specialist agents initialized with VeADK")
    
    def _init_coordinator(self):
        """Initialize coordinator using VeADK SequentialAgent"""
        self.logger.info("Initializing research coordinator...")
        
        # Master Agent for coordination
        self.master_agent = Agent(
            name="master_agent",
            description="Research coordinator and quality controller",
            instruction=self._load_prompt("master_agent.txt")
        )
        
        # Full research workflow using SequentialAgent
        # This chains: literature → hypothesis → experiment → writing
        self.research_workflow = SequentialAgent(
            name="research_workflow",
            description="Complete scientific research workflow",
            sub_agents=[
                self.literature_agent,
                self.hypothesis_agent,
                self.experiment_agent,
                self.writing_agent
            ]
        )
        
        # Parallel agent for simultaneous searches
        self.parallel_search = ParallelAgent(
            name="parallel_search",
            description="Parallel paper search across multiple sources",
            sub_agents=[
                Agent(
                    name="arxiv_searcher",
                    description="Search arXiv",
                    instruction="Search for papers on arXiv related to the query.",
                    tools=[FunctionTool(arxiv_search)]
                ),
                Agent(
                    name="semantic_scholar_searcher",
                    description="Search Semantic Scholar",
                    instruction="Search for papers on Semantic Scholar related to the query.",
                    tools=[FunctionTool(semantic_scholar_search)]
                )
            ]
        )
        
        self.logger.info("Research coordinator initialized with VeADK SequentialAgent")
    
    def _load_prompt(self, filename: str) -> str:
        """Load prompt template from file"""
        prompt_file = settings.prompts_dir / filename
        if prompt_file.exists():
            return prompt_file.read_text(encoding='utf-8')
        else:
            self.logger.warning(f"Prompt file not found: {filename}, using default")
            return self._get_default_prompt(filename)
    
    def _get_default_prompt(self, filename: str) -> str:
        """Get default prompt if file not found"""
        prompts = {
            "master_agent.txt": """You are the Master Agent coordinating scientific research tasks.
Your responsibilities:
1. Parse and understand research tasks
2. Plan execution strategy
3. Coordinate specialist agents
4. Ensure quality control
5. Synthesize final results

Always be systematic, thorough, and maintain high quality standards.""",
            
            "literature_agent.txt": """You are the Literature Agent specialized in paper search and analysis.
Your capabilities:
1. Search academic databases (arXiv, Semantic Scholar, PubMed)
2. Retrieve and parse papers
3. Analyze research trends
4. Identify key papers and citations

You have access to the following tools:
- arxiv_search: Search papers on arXiv
- semantic_scholar_search: Search papers on Semantic Scholar
- pubmed_search: Search biomedical papers
- parse_pdf: Extract text from PDF papers

Always provide comprehensive and well-organized literature reviews.""",
            
            "hypothesis_agent.txt": """You are the Hypothesis Agent specialized in generating research hypotheses.
Your capabilities:
1. Analyze literature to identify research gaps
2. Generate novel and feasible hypotheses
3. Assess novelty and significance
4. Provide theoretical foundations

Always ensure hypotheses are innovative, testable, and well-grounded.""",
            
            "experiment_design_agent.txt": """You are the Experiment Design Agent specialized in planning research methods.
Your capabilities:
1. Design rigorous experimental protocols
2. Select appropriate methodologies
3. Plan data collection and analysis
4. Assess feasibility and resources

Always design practical, rigorous, and reproducible experiments.""",
            
            "writing_agent.txt": """You are the Writing Agent specialized in creating research reports.
Your capabilities:
1. Structure and write comprehensive reports
2. Integrate findings from multiple sources
3. Format citations and references
4. Ensure clarity and academic rigor

Always produce well-structured, clear, and professional scientific writing."""
        }
        return prompts.get(filename, "You are a helpful research assistant.")
    
    async def run_task(
        self,
        task: str,
        domain: str = "computer_science",
        task_type: str = "literature_review"
    ) -> Dict[str, Any]:
        """
        Execute a scientific research task using VeADK
        
        Args:
            task: Task description
            domain: Research domain (computer_science, biomedical, etc.)
            task_type: Type of task (literature_review, hypothesis_generation, etc.)
        
        Returns:
            Dict containing results, cost, and metadata
        """
        self.logger.info(f"Running task: {task_type} in {domain}")
        self.logger.info(f"Task description: {task[:100]}...")
        
        # Load domain configuration
        domain_config = self.domain_manager.get_domain(domain)
        
        # Prepare context with domain info
        full_prompt = f"""Task: {task}
Domain: {domain}
Task Type: {task_type}

Domain Context:
{domain_config}

Please complete this task systematically and thoroughly."""
        
        # Execute using appropriate agent/workflow
        if task_type == "literature_review":
            result = await self._run_literature_review(full_prompt)
        elif task_type == "hypothesis_generation":
            result = await self._run_hypothesis_generation(full_prompt)
        elif task_type == "experiment_design":
            result = await self._run_experiment_design(full_prompt)
        elif task_type == "full_research":
            result = await self._run_full_research(full_prompt)
        else:
            # Default: use master agent
            result = await run_agent_with_runner(self.master_agent, full_prompt)
        
        return {
            "status": "success",
            "result": result,
            "domain": domain,
            "task_type": task_type,
            "framework": "VeADK Native"
        }
    
    async def _run_literature_review(self, prompt: str) -> str:
        """Run literature review using literature agent with tools"""
        return await run_agent_with_runner(self.literature_agent, prompt)
    
    async def _run_hypothesis_generation(self, prompt: str) -> str:
        """Run hypothesis generation"""
        return await run_agent_with_runner(self.hypothesis_agent, prompt)
    
    async def _run_experiment_design(self, prompt: str) -> str:
        """Run experiment design"""
        return await run_agent_with_runner(self.experiment_agent, prompt)
    
    async def _run_full_research(self, prompt: str) -> str:
        """Run full research workflow using SequentialAgent"""
        return await run_agent_with_runner(self.research_workflow, prompt)
    
    async def literature_review(
        self,
        topic: str,
        domain: str = "computer_science",
        max_papers: int = 20
    ) -> AgentOutput:
        """
        Conduct a literature review
        
        Args:
            topic: Research topic
            domain: Research domain
            max_papers: Maximum number of papers to retrieve
        
        Returns:
            AgentOutput with literature review
        """
        task = f"Conduct a comprehensive literature review on: {topic}. " \
               f"Retrieve and analyze up to {max_papers} relevant papers."
        
        result = await self.run_task(
            task=task,
            domain=domain,
            task_type="literature_review"
        )
        
        return AgentOutput(
            agent_name="literature_agent",
            action="literature_review",
            status="success",
            output=result["result"],
            metadata={"framework": "VeADK Native"},
            cost_usd=0.0
        )
    
    async def generate_hypothesis(
        self,
        literature_context: str,
        domain: str = "computer_science"
    ) -> AgentOutput:
        """
        Generate research hypotheses based on literature
        
        Args:
            literature_context: Literature review context
            domain: Research domain
        
        Returns:
            AgentOutput with hypotheses
        """
        task = f"Based on the following literature review, generate novel research hypotheses:\n\n{literature_context}"
        
        result = await self.run_task(
            task=task,
            domain=domain,
            task_type="hypothesis_generation"
        )
        
        return AgentOutput(
            agent_name="hypothesis_agent",
            action="hypothesis_generation",
            status="success",
            output=result["result"],
            metadata={"framework": "VeADK Native"},
            cost_usd=0.0
        )
    
    async def design_experiment(
        self,
        hypothesis: str,
        domain: str = "computer_science"
    ) -> AgentOutput:
        """
        Design experiments to validate hypotheses
        
        Args:
            hypothesis: Research hypothesis
            domain: Research domain
        
        Returns:
            AgentOutput with experiment design
        """
        task = f"Design rigorous experiments to validate the following hypothesis:\n\n{hypothesis}"
        
        result = await self.run_task(
            task=task,
            domain=domain,
            task_type="experiment_design"
        )
        
        return AgentOutput(
            agent_name="experiment_design_agent",
            action="experiment_design",
            status="success",
            output=result["result"],
            metadata={"framework": "VeADK Native"},
            cost_usd=0.0
        )
    
    async def write_report(
        self,
        research_context: str,
        domain: str = "computer_science"
    ) -> AgentOutput:
        """
        Write a research report
        
        Args:
            research_context: Complete research context
            domain: Research domain
        
        Returns:
            AgentOutput with research report
        """
        task = f"Write a comprehensive research report based on:\n\n{research_context}"
        
        result = await self.run_task(
            task=task,
            domain=domain,
            task_type="report_writing"
        )
        
        return AgentOutput(
            agent_name="writing_agent",
            action="report_writing",
            status="success",
            output=result["result"],
            metadata={"framework": "VeADK Native"},
            cost_usd=0.0
        )
    
    async def full_research_pipeline(
        self,
        topic: str,
        domain: str = "computer_science"
    ) -> Dict[str, Any]:
        """
        Execute full research pipeline using VeADK SequentialAgent
        
        This runs the complete workflow:
        Literature Review → Hypothesis → Experiment Design → Report
        
        Args:
            topic: Research topic
            domain: Research domain
        
        Returns:
            Complete research results
        """
        self.logger.info(f"Starting full research pipeline for: {topic}")
        
        task = f"""Conduct complete scientific research on: {topic}

Please perform the following steps:
1. Conduct a comprehensive literature review
2. Identify research gaps and generate hypotheses
3. Design experiments to test the hypotheses
4. Write a final research report

Domain: {domain}
"""
        
        # Use the SequentialAgent workflow
        result = await self.research_workflow.run_async(task)
        
        return {
            "status": "success",
            "topic": topic,
            "domain": domain,
            "result": result,
            "framework": "VeADK SequentialAgent",
            "agents_used": [
                "literature_agent",
                "hypothesis_agent",
                "experiment_design_agent",
                "writing_agent"
            ]
        }


# Singleton instance
_system_instance: Optional[UniversalSciAgentSystem] = None


def get_sci_agent_system() -> UniversalSciAgentSystem:
    """Get or create the singleton Universal-SciAgent system"""
    global _system_instance
    if _system_instance is None:
        _system_instance = UniversalSciAgentSystem()
    return _system_instance
