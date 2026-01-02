"""Core data models for Universal-SciAgent"""
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class Task(BaseModel):
    """Structure for representing a research task"""
    task_type: Literal["literature_review", "hypothesis_generation", "experiment_design"]
    domain: List[str] = Field(description="Domain(s) of research, e.g., ['computer_science']")
    keywords: List[str] = Field(description="Research keywords")
    description: Optional[str] = Field(default=None, description="Natural language task description")
    time_range: Optional[tuple] = Field(default=None, description="Time range for literature search")
    max_papers: int = Field(default=20, description="Maximum number of papers to retrieve")
    num_hypotheses: int = Field(default=3, description="Number of hypotheses to generate")
    max_cost: float = Field(default=2.0, description="Maximum cost budget in USD")
    additional_constraints: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_type": "literature_review",
                "domain": ["computer_science"],
                "keywords": ["Transformer", "Computer Vision"],
                "time_range": (2023, 2025),
                "max_papers": 20
            }
        }


class ComplexityDimensions(BaseModel):
    """Breakdown of complexity evaluation dimensions"""
    domain_span: float = Field(ge=0, le=2, description="0-2: single domain to multi-domain")
    data_requirement: float = Field(ge=0, le=3, description="0-3: literature only to experimental data")
    innovation_level: float = Field(ge=0, le=3, description="0-3: review to novel direction")
    ambiguity: float = Field(ge=0, le=2, description="0-2: well-defined to highly ambiguous")


class Complexity(BaseModel):
    """Complexity evaluation result"""
    score: float = Field(ge=0, le=10, description="Overall complexity score (0-10)")
    dimensions: ComplexityDimensions
    reasoning: str = Field(description="Natural language explanation of the complexity")


class WorkflowStep(BaseModel):
    """Single step in execution workflow"""
    agent_name: str = Field(description="Name of the agent to execute")
    action: str = Field(description="Action to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[int] = Field(default_factory=list, description="Indices of dependent steps")


class ExecutionPlan(BaseModel):
    """Execution plan for a task"""
    agents: List[str] = Field(description="List of agent names to be invoked")
    workflow: List[WorkflowStep] = Field(description="Ordered workflow steps")
    estimated_time_minutes: float = Field(description="Estimated execution time in minutes")
    estimated_cost_usd: float = Field(description="Estimated cost in USD")
    reasoning: str = Field(description="Explanation of the plan")


class AgentOutput(BaseModel):
    """Output from an individual agent"""
    agent_name: str
    action: str
    timestamp: datetime = Field(default_factory=datetime.now)
    status: Literal["success", "failed", "partial"]
    output: Any = Field(description="Agent's output (can be dict, str, list)")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    cost_usd: float = Field(default=0.0)


class ExecutionLog(BaseModel):
    """Log entry for tracking execution"""
    timestamp: datetime = Field(default_factory=datetime.now)
    step_index: int
    agent_name: str
    action: str
    input_summary: str = Field(description="Brief summary of input")
    output_summary: str = Field(description="Brief summary of output")
    status: Literal["success", "failed", "partial"]
    cost_usd: float = Field(default=0.0)
    duration_seconds: float = Field(default=0.0)


class TaskResult(BaseModel):
    """Final result of task execution"""
    task: Task
    output_report: str = Field(description="Generated report in Markdown format")
    execution_logs: List[ExecutionLog] = Field(default_factory=list)
    agent_outputs: List[AgentOutput] = Field(default_factory=list)
    total_cost_usd: float = Field(default=0.0)
    total_duration_seconds: float = Field(default=0.0)
    quality_score: Optional[float] = Field(default=None, ge=0, le=10)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Paper(BaseModel):
    """Structure for representing a research paper"""
    id: str = Field(description="Unique identifier (e.g., arXiv ID or DOI)")
    title: str
    authors: List[str] = Field(default_factory=list)
    abstract: str = Field(default="")
    year: Optional[int] = None
    url: str = Field(default="")
    pdf_url: Optional[str] = None
    citations: int = Field(default=0)
    venue: Optional[str] = None
    full_text: Optional[str] = Field(default=None, description="Extracted full text from PDF")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "2010.11929",
                "title": "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
                "authors": ["Alexey Dosovitskiy", "Lucas Beyer"],
                "abstract": "While the Transformer architecture...",
                "year": 2021,
                "url": "https://arxiv.org/abs/2010.11929",
                "citations": 15000
            }
        }


class Hypothesis(BaseModel):
    """Structure for representing a research hypothesis"""
    statement: str = Field(description="One-sentence hypothesis statement")
    rationale: str = Field(description="Theoretical rationale with citations (200 words)")
    innovation: str = Field(description="Innovation points (100 words)")
    experiment_outline: str = Field(description="Initial experiment outline (300 words)")
    expected_impact: str = Field(description="Expected impact (100 words)")
    experiment_design: Optional[str] = Field(default=None, description="Detailed experiment design (800-1200 words)")
    feasibility_score: Optional[float] = Field(default=None, ge=0, le=10)
    feasibility_breakdown: Optional[Dict[str, float]] = Field(default=None)
    feasibility_reasoning: Optional[str] = Field(default=None)


class LiteratureContext(BaseModel):
    """Context extracted from literature"""
    paper_ids: List[str] = Field(default_factory=list)
    summary: str = Field(description="Overall trend summary")
    key_methods: List[str] = Field(default_factory=list)
    research_gaps: str = Field(description="Identified research gaps")
    technical_bottlenecks: List[str] = Field(default_factory=list)
