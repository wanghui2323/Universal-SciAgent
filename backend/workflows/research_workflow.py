"""
VeADK Native Research Workflow for Universal-SciAgent

This module implements scientific research workflows using VeADK's native
agent coordination capabilities:
- SequentialAgent: Chain agents for sequential execution
- ParallelAgent: Run agents in parallel for efficiency
- LoopAgent: Iterative refinement workflows

VeADK handles:
- Agent coordination and message passing
- Step dependencies
- Error handling and retries
- Progress tracking
- Result aggregation

Reference: https://github.com/volcengine/veadk-python
"""

import logging
from typing import Dict, Any, List, Optional
from enum import Enum

# VeADK Native Imports
from veadk import Agent, Runner
from veadk.agents.sequential_agent import SequentialAgent
from veadk.agents.parallel_agent import ParallelAgent
from veadk.agents.loop_agent import LoopAgent

# Google ADK Tools
from google.adk.tools import FunctionTool

from ..core.models import Task, AgentOutput
from ..tools.veadk_tools import (
    arxiv_search,
    semantic_scholar_search,
    pubmed_search,
    parse_pdf
)

logger = logging.getLogger(__name__)


class WorkflowType(Enum):
    """Workflow types"""
    LITERATURE_REVIEW = "literature_review"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    EXPERIMENT_DESIGN = "experiment_design"
    FULL_RESEARCH = "full_research"
    PARALLEL_SEARCH = "parallel_search"
    ITERATIVE_REFINEMENT = "iterative_refinement"
    CUSTOM = "custom"


class ResearchWorkflow:
    """
    Scientific Research Workflow using VeADK Native Agent Coordination
    
    Supports multiple workflow types using VeADK's agent orchestration:
    - SequentialAgent: Literature → Hypothesis → Experiment → Report
    - ParallelAgent: Simultaneous search across multiple sources
    - LoopAgent: Iterative refinement until quality threshold
    
    VeADK automatically handles:
    - Agent-to-agent message passing
    - State management
    - Error handling and retries
    - Progress tracking
    - Cost aggregation
    """
    
    def __init__(self):
        """Initialize research workflow with VeADK agents"""
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.logger.info("Initializing VeADK Research Workflow...")
        
        # Initialize all workflow agents
        self._init_specialist_agents()
        self._init_workflow_agents()
        
        self.logger.info("VeADK Research Workflow initialized")
    
    def _init_specialist_agents(self):
        """Initialize specialist agents for different tasks"""
        self.logger.info("Initializing specialist agents...")
        
        # Literature Agent with search tools
        self.literature_agent = Agent(
            name="literature_agent",
            description="Expert in academic literature search and analysis",
            instruction="""You are a literature research expert. Your task is to:
1. Search academic databases for relevant papers
2. Analyze and summarize research findings
3. Identify key themes and trends
4. Highlight important citations

Use the available tools to search arXiv, Semantic Scholar, and PubMed.
Provide comprehensive and well-organized literature reviews.""",
            tools=[
                FunctionTool(arxiv_search),
                FunctionTool(semantic_scholar_search),
                FunctionTool(pubmed_search)
            ]
        )
        
        # Hypothesis Agent
        self.hypothesis_agent = Agent(
            name="hypothesis_agent",
            description="Expert in generating research hypotheses",
            instruction="""You are a research hypothesis expert. Based on literature reviews, you:
1. Identify research gaps and opportunities
2. Generate novel and testable hypotheses
3. Assess novelty, significance, and feasibility
4. Provide theoretical foundations

Ensure hypotheses are innovative, specific, and well-grounded in existing research."""
        )
        
        # Experiment Design Agent
        self.experiment_agent = Agent(
            name="experiment_design_agent",
            description="Expert in designing rigorous experiments",
            instruction="""You are an experiment design expert. You:
1. Design rigorous experimental protocols
2. Select appropriate methodologies and controls
3. Plan data collection and analysis strategies
4. Assess feasibility and resource requirements

Ensure experiments are reproducible, statistically valid, and practically feasible."""
        )
        
        # Writing Agent
        self.writing_agent = Agent(
            name="writing_agent",
            description="Expert in scientific writing",
            instruction="""You are a scientific writing expert. You:
1. Structure comprehensive research reports
2. Synthesize findings from multiple sources
3. Format citations and references properly
4. Ensure clarity, accuracy, and academic rigor

Produce well-organized, professional scientific documents."""
        )
        
        # Quality Review Agent (for iterative refinement)
        self.review_agent = Agent(
            name="review_agent",
            description="Expert in quality review and feedback",
            instruction="""You are a research quality reviewer. You:
1. Evaluate research quality and rigor
2. Identify weaknesses and gaps
3. Provide constructive feedback
4. Determine if quality threshold is met

Be thorough and constructive in your reviews."""
        )
    
    def _init_workflow_agents(self):
        """Initialize workflow orchestration agents"""
        self.logger.info("Initializing workflow agents...")
        
        # Literature Review Workflow (Sequential)
        self.literature_workflow = SequentialAgent(
            name="literature_review_workflow",
            description="Complete literature review workflow",
            sub_agents=[
                self.literature_agent,
                self.writing_agent
            ]
        )
        
        # Full Research Workflow (Sequential)
        self.full_research_workflow = SequentialAgent(
            name="full_research_workflow",
            description="Complete scientific research workflow",
            sub_agents=[
                self.literature_agent,
                self.hypothesis_agent,
                self.experiment_agent,
                self.writing_agent
            ]
        )
        
        # Parallel Search Workflow
        # Create dedicated search agents for parallel execution
        arxiv_agent = Agent(
            name="arxiv_searcher",
            description="arXiv paper searcher",
            instruction="Search arXiv for papers matching the query. Return detailed results.",
            tools=[FunctionTool(arxiv_search)]
        )
        
        ss_agent = Agent(
            name="semantic_scholar_searcher",
            description="Semantic Scholar paper searcher",
            instruction="Search Semantic Scholar for papers matching the query. Return results with citation metrics.",
            tools=[FunctionTool(semantic_scholar_search)]
        )
        
        pubmed_agent = Agent(
            name="pubmed_searcher",
            description="PubMed paper searcher",
            instruction="Search PubMed for biomedical papers matching the query.",
            tools=[FunctionTool(pubmed_search)]
        )
        
        self.parallel_search_workflow = ParallelAgent(
            name="parallel_search_workflow",
            description="Search multiple academic databases in parallel",
            sub_agents=[arxiv_agent, ss_agent, pubmed_agent]
        )
        
        # Iterative Refinement Workflow
        self.iterative_workflow = LoopAgent(
            name="iterative_refinement_workflow",
            description="Iteratively refine research until quality threshold",
            sub_agents=[
                self.writing_agent,
                self.review_agent
            ],
            max_iterations=3  # Maximum refinement cycles
        )
        
        self.logger.info("Workflow agents initialized")
    
    async def execute_literature_review(
        self,
        topic: str,
        domain: str = "computer_science",
        max_papers: int = 20
    ) -> Dict[str, Any]:
        """
        Execute literature review workflow using VeADK SequentialAgent
        
        Args:
            topic: Research topic
            domain: Research domain
            max_papers: Maximum number of papers
        
        Returns:
            Workflow results
        """
        self.logger.info(f"Executing literature review workflow: {topic}")
        
        prompt = f"""Conduct a comprehensive literature review on: {topic}

Domain: {domain}
Maximum papers to retrieve: {max_papers}

Please:
1. Search relevant academic databases
2. Analyze and synthesize the findings
3. Identify key themes and research gaps
4. Write a comprehensive literature review
"""
        
        # Execute using VeADK SequentialAgent
        result = await self.literature_workflow.run_async(prompt)
        
        self.logger.info("Literature review workflow completed")
        
        return {
            "status": "completed",
            "topic": topic,
            "domain": domain,
            "result": result,
            "workflow_type": "literature_review",
            "framework": "VeADK SequentialAgent"
        }
    
    async def execute_parallel_search(
        self,
        query: str,
        max_results_per_source: int = 10
    ) -> Dict[str, Any]:
        """
        Execute parallel search across multiple databases using VeADK ParallelAgent
        
        Args:
            query: Search query
            max_results_per_source: Max results per database
        
        Returns:
            Combined search results
        """
        self.logger.info(f"Executing parallel search: {query}")
        
        prompt = f"""Search for academic papers on: {query}

Maximum results per source: {max_results_per_source}

Search all available databases and return the results."""
        
        # Execute using VeADK ParallelAgent
        result = await self.parallel_search_workflow.run_async(prompt)
        
        self.logger.info("Parallel search workflow completed")
        
        return {
            "status": "completed",
            "query": query,
            "result": result,
            "workflow_type": "parallel_search",
            "framework": "VeADK ParallelAgent"
        }
    
    async def execute_full_research(
        self,
        task: str,
        domain: str = "computer_science"
    ) -> Dict[str, Any]:
        """
        Execute full research workflow using VeADK SequentialAgent
        
        This runs: Literature → Hypothesis → Experiment → Report
        
        Args:
            task: Research task description
            domain: Research domain
        
        Returns:
            Complete research results
        """
        self.logger.info(f"Executing full research workflow")
        
        prompt = f"""Conduct comprehensive scientific research on: {task}

Domain: {domain}

Complete the following steps:
1. Literature Review: Search and analyze relevant papers
2. Hypothesis Generation: Identify gaps and generate hypotheses
3. Experiment Design: Design experiments to test hypotheses
4. Report Writing: Write a comprehensive research report
"""
        
        # Execute using VeADK SequentialAgent
        result = await self.full_research_workflow.run_async(prompt)
        
        self.logger.info("Full research workflow completed")
        
        return {
            "status": "completed",
            "task": task,
            "domain": domain,
            "result": result,
            "workflow_type": "full_research",
            "framework": "VeADK SequentialAgent",
            "agents_used": [
                "literature_agent",
                "hypothesis_agent",
                "experiment_design_agent",
                "writing_agent"
            ]
        }
    
    async def execute_iterative_refinement(
        self,
        draft: str,
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """
        Execute iterative refinement workflow using VeADK LoopAgent
        
        Args:
            draft: Initial draft to refine
            max_iterations: Maximum refinement cycles
        
        Returns:
            Refined result
        """
        self.logger.info(f"Executing iterative refinement workflow")
        
        prompt = f"""Refine the following research draft through iterative review and improvement:

{draft}

For each iteration:
1. Writing Agent: Improve the draft based on feedback
2. Review Agent: Evaluate quality and provide feedback

Continue until quality threshold is met or max iterations reached.
"""
        
        # Execute using VeADK LoopAgent
        result = await self.iterative_workflow.run_async(prompt)
        
        self.logger.info("Iterative refinement workflow completed")
        
        return {
            "status": "completed",
            "result": result,
            "workflow_type": "iterative_refinement",
            "framework": "VeADK LoopAgent",
            "max_iterations": max_iterations
        }
    
    async def execute_custom_workflow(
        self,
        agents: List[str],
        prompt: str,
        parallel: bool = False
    ) -> Dict[str, Any]:
        """
        Execute custom workflow with specified agents
        
        Args:
            agents: List of agent names to use
            prompt: Task prompt
            parallel: Whether to run agents in parallel
        
        Returns:
            Workflow results
        """
        self.logger.info(f"Executing custom workflow with {len(agents)} agents")
        
        # Map agent names to agent instances
        agent_map = {
            "literature": self.literature_agent,
            "hypothesis": self.hypothesis_agent,
            "experiment": self.experiment_agent,
            "writing": self.writing_agent,
            "review": self.review_agent
        }
        
        selected_agents = [
            agent_map[name] for name in agents
            if name in agent_map
        ]
        
        if not selected_agents:
            return {"error": "No valid agents specified"}
        
        # Create appropriate workflow
        if parallel:
            workflow = ParallelAgent(
                name="custom_parallel_workflow",
                description="Custom parallel workflow",
                sub_agents=selected_agents
            )
        else:
            workflow = SequentialAgent(
                name="custom_sequential_workflow",
                description="Custom sequential workflow",
                sub_agents=selected_agents
            )
        
        # Execute
        result = await workflow.run_async(prompt)
        
        self.logger.info("Custom workflow completed")
        
        return {
            "status": "completed",
            "result": result,
            "workflow_type": "custom",
            "agents": agents,
            "parallel": parallel,
            "framework": f"VeADK {'ParallelAgent' if parallel else 'SequentialAgent'}"
        }


def create_research_workflow() -> ResearchWorkflow:
    """
    Factory function to create research workflow
    
    Returns:
        Configured ResearchWorkflow using VeADK
    """
    return ResearchWorkflow()
