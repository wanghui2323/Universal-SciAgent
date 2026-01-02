"""Master Agent for task orchestration and agent coordination"""
import asyncio
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_agent import BaseAgent
from .literature_agent import LiteratureAgent
from .hypothesis_agent import HypothesisAgent
from .experiment_design_agent import ExperimentDesignAgent
from .writing_agent import WritingAgent

from ..core.models import (
    Task, TaskResult, ExecutionPlan, WorkflowStep,
    Complexity, ComplexityDimensions, ExecutionLog
)
from ..utils.domain_manager import domain_manager

logger = logging.getLogger(__name__)


class MasterAgent(BaseAgent):
    """
    Master Agent responsibilities:
    1. Task understanding and parsing
    2. Complexity evaluation
    3. Execution plan generation
    4. User interaction (confirmation)
    5. Agent orchestration
    6. Result aggregation and quality control
    7. Progress feedback
    """
    
    def __init__(self):
        super().__init__(name="MasterAgent", description="Task orchestration and coordination")
        
        # Initialize sub-agents
        self.literature_agent = LiteratureAgent()
        self.hypothesis_agent = HypothesisAgent()
        self.experiment_design_agent = ExperimentDesignAgent()
        self.writing_agent = WritingAgent()
        
        self.logger.info("Initialized all sub-agents")
    
    async def run(self, task_input: Any, auto_confirm: bool = False) -> TaskResult:
        """
        Main entry point for running a task
        
        Args:
            task_input: Either a natural language string or a Task object
            auto_confirm: If True, skip user confirmation
            
        Returns:
            TaskResult with complete execution results
        """
        start_time = time.time()
        
        # 1. Parse task
        task = self._parse_task(task_input)
        self.log_progress(f"📋 Task parsed: {task.task_type} in {', '.join(task.domain)}")
        
        # 2. Evaluate complexity
        complexity = await self._evaluate_complexity(task)
        self.log_progress(f"📊 Complexity: {complexity.score:.1f}/10 - {complexity.reasoning}")
        
        # 3. Generate execution plan
        plan = await self._generate_execution_plan(task, complexity)
        self.log_progress(f"📝 Plan: {len(plan.agents)} agents, ~{plan.estimated_time_minutes:.1f}min, ~${plan.estimated_cost_usd:.2f}")
        
        # 4. User confirmation
        if not auto_confirm:
            confirmed = self._request_confirmation(plan)
            if not confirmed:
                return TaskResult(
                    task=task,
                    output_report="Task cancelled by user",
                    execution_logs=[],
                    agent_outputs=[],
                    total_cost_usd=0.0,
                    total_duration_seconds=0.0
                )
        
        # 5. Execute workflow
        self.log_progress("🚀 Starting execution...")
        execution_logs, agent_outputs, total_cost = await self._execute_workflow(plan, task)
        
        # 6. Generate final report (from Writing Agent output)
        final_report = self._extract_final_report(agent_outputs)
        
        # 7. Quality control
        quality_score = self._evaluate_quality(final_report, execution_logs)
        
        # Calculate total duration
        total_duration = time.time() - start_time
        
        # Create result
        result = TaskResult(
            task=task,
            output_report=final_report,
            execution_logs=execution_logs,
            agent_outputs=agent_outputs,
            total_cost_usd=total_cost,
            total_duration_seconds=total_duration,
            quality_score=quality_score,
            metadata={
                "complexity": complexity.dict(),
                "plan": plan.dict()
            }
        )
        
        self.log_progress(f"✅ Task completed in {total_duration:.1f}s, cost ${total_cost:.2f}")
        
        return result
    
    def _parse_task(self, task_input: Any) -> Task:
        """Parse natural language or structured input into Task object"""
        if isinstance(task_input, Task):
            return task_input
        
        if isinstance(task_input, dict):
            return Task(**task_input)
        
        if isinstance(task_input, str):
            # Natural language parsing (simplified)
            # In production, use more sophisticated NLP
            keywords = self._extract_keywords(task_input)
            
            # Infer task type
            if "综述" in task_input or "review" in task_input.lower():
                task_type = "literature_review"
            elif "假设" in task_input or "hypothesis" in task_input.lower():
                task_type = "hypothesis_generation"
            elif "实验" in task_input or "experiment" in task_input.lower():
                task_type = "experiment_design"
            else:
                task_type = "literature_review"  # Default
            
            # Suggest domains based on keywords
            suggested_domains = domain_manager.suggest_domains(keywords)
            if not suggested_domains:
                suggested_domains = ["computer_science"]  # Default domain
            
            return Task(
                task_type=task_type,
                domain=suggested_domains[:1],  # Use primary domain
                keywords=keywords,
                description=task_input
            )
        
        raise ValueError(f"Unsupported task input type: {type(task_input)}")
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from natural language (simplified)"""
        # Simple keyword extraction
        # In production, use NLP techniques (TF-IDF, KeyBERT, etc.)
        import re
        
        # Remove common words
        common_words = {"的", "在", "和", "与", "对", "为", "是", "等", "中", "了", "有"}
        
        # Split and clean
        words = re.findall(r'[\w]+', text)
        keywords = [w for w in words if len(w) > 1 and w not in common_words]
        
        # Take first 5-10 words as keywords
        return keywords[:10]
    
    async def _evaluate_complexity(self, task: Task) -> Complexity:
        """Evaluate task complexity"""
        
        # Calculate dimension scores
        domain_span = min(len(task.domain) * 0.5, 2.0)  # 0-2
        
        if task.task_type == "literature_review":
            data_requirement = 1.0
            innovation_level = 0.0
        elif task.task_type == "hypothesis_generation":
            data_requirement = 2.0
            innovation_level = 3.0
        else:  # experiment_design
            data_requirement = 3.0
            innovation_level = 1.0
        
        # Ambiguity based on description clarity
        ambiguity = 0.0 if task.description and len(task.description) > 50 else 1.5
        
        dimensions = ComplexityDimensions(
            domain_span=domain_span,
            data_requirement=data_requirement,
            innovation_level=innovation_level,
            ambiguity=ambiguity
        )
        
        # Calculate overall score
        total_score = domain_span + data_requirement + innovation_level + ambiguity
        
        # Generate reasoning
        reasoning = f"领域跨度: {domain_span}/2, 数据需求: {data_requirement}/3, 创新程度: {innovation_level}/3, 模糊度: {ambiguity}/2"
        
        if len(task.domain) > 1:
            reasoning += f" (跨领域任务增加复杂度)"
        if task.task_type == "hypothesis_generation":
            reasoning += f" (假设生成需要深度推理)"
        
        return Complexity(
            score=round(total_score, 1),
            dimensions=dimensions,
            reasoning=reasoning
        )
    
    async def _generate_execution_plan(self, task: Task, complexity: Complexity) -> ExecutionPlan:
        """Generate execution plan based on task and complexity"""
        
        workflow = []
        agents = []
        
        if task.task_type == "literature_review":
            # Literature Review workflow
            agents = ["LiteratureAgent", "WritingAgent"]
            workflow = [
                WorkflowStep(
                    agent_name="LiteratureAgent",
                    action="search_and_analyze",
                    parameters={
                        "keywords": task.keywords,
                        "domains": task.domain,
                        "max_papers": task.max_papers,
                        "time_range": task.time_range
                    }
                ),
                WorkflowStep(
                    agent_name="WritingAgent",
                    action="generate_literature_review",
                    parameters={"task_type": "literature_review"},
                    dependencies=[0]
                )
            ]
            estimated_time = 8.0
            estimated_cost = 1.2
            
        elif task.task_type == "hypothesis_generation":
            # Hypothesis Generation workflow
            agents = ["LiteratureAgent", "HypothesisAgent", "ExperimentDesignAgent", "WritingAgent"]
            workflow = [
                WorkflowStep(
                    agent_name="LiteratureAgent",
                    action="search_and_analyze",
                    parameters={
                        "keywords": task.keywords,
                        "domains": task.domain,
                        "max_papers": task.max_papers
                    }
                ),
                WorkflowStep(
                    agent_name="HypothesisAgent",
                    action="generate_hypotheses",
                    parameters={
                        "num_hypotheses": 5,
                        "domains": task.domain,
                        "keywords": task.keywords
                    },
                    dependencies=[0]
                ),
                WorkflowStep(
                    agent_name="ExperimentDesignAgent",
                    action="design_experiments",
                    parameters={
                        "num_final": task.num_hypotheses,
                        "domains": task.domain
                    },
                    dependencies=[1]
                ),
                WorkflowStep(
                    agent_name="WritingAgent",
                    action="generate_hypothesis_report",
                    parameters={"task_type": "hypothesis_generation"},
                    dependencies=[2]
                )
            ]
            estimated_time = 12.0
            estimated_cost = 1.8
            
        else:
            raise ValueError(f"Unsupported task type: {task.task_type}")
        
        # Adjust for complexity
        if complexity.score > 8:
            estimated_time *= 1.3
            estimated_cost *= 1.2
        
        # Adjust for cross-domain
        if len(task.domain) > 1:
            estimated_time *= 1.2
            estimated_cost *= 1.15
        
        reasoning = f"任务类型: {task.task_type}, 复杂度: {complexity.score:.1f}/10"
        if len(task.domain) > 1:
            reasoning += ", 跨领域任务"
        
        return ExecutionPlan(
            agents=agents,
            workflow=workflow,
            estimated_time_minutes=estimated_time,
            estimated_cost_usd=estimated_cost,
            reasoning=reasoning
        )
    
    def _request_confirmation(self, plan: ExecutionPlan) -> bool:
        """Request user confirmation for execution plan"""
        print("\n" + "="*60)
        print("📋 执行计划")
        print("="*60)
        print(f"需要的Agent: {', '.join(plan.agents)}")
        print(f"预计时间: {plan.estimated_time_minutes:.1f} 分钟")
        print(f"预计成本: ${plan.estimated_cost_usd:.2f}")
        print(f"\n执行步骤:")
        for i, step in enumerate(plan.workflow, 1):
            print(f"  {i}. {step.agent_name} - {step.action}")
        print("="*60)
        
        response = input("\n确认执行? (y/n): ").strip().lower()
        return response in ["y", "yes", "是", "确认"]
    
    async def _execute_workflow(
        self,
        plan: ExecutionPlan,
        task: Task
    ) -> tuple[List[ExecutionLog], List, float]:
        """Execute workflow by calling agents in order"""
        
        execution_logs = []
        agent_outputs = []
        total_cost = 0.0
        
        # Shared context across agents
        context = {
            "keywords": task.keywords,
            "domains": task.domain,
            "max_papers": task.max_papers,
            "task_type": task.task_type,
            "num_hypotheses": task.num_hypotheses
        }
        
        # Execute each step
        for step_index, step in enumerate(plan.workflow):
            step_start = time.time()
            
            self.log_progress(f"Executing: {step.agent_name} - {step.action}")
            
            # Merge step parameters into context
            step_context = {**context, **step.parameters}
            
            try:
                # Call appropriate agent
                if step.agent_name == "LiteratureAgent":
                    output = await self.literature_agent.execute(step_context)
                elif step.agent_name == "HypothesisAgent":
                    output = await self.hypothesis_agent.execute(step_context)
                elif step.agent_name == "ExperimentDesignAgent":
                    output = await self.experiment_design_agent.execute(step_context)
                elif step.agent_name == "WritingAgent":
                    output = await self.writing_agent.execute(step_context)
                else:
                    raise ValueError(f"Unknown agent: {step.agent_name}")
                
                # Update context with output
                if output.status == "success" and isinstance(output.output, dict):
                    context.update(output.output)
                
                # Record output
                agent_outputs.append(output)
                total_cost += output.cost_usd
                
                # Create execution log
                log = ExecutionLog(
                    step_index=step_index,
                    agent_name=step.agent_name,
                    action=step.action,
                    input_summary=str(step.parameters)[:200],
                    output_summary=str(output.output)[:200],
                    status=output.status,
                    cost_usd=output.cost_usd,
                    duration_seconds=time.time() - step_start
                )
                execution_logs.append(log)
                
            except Exception as e:
                self.logger.error(f"Step {step_index} failed: {e}")
                
                # Create error log
                log = ExecutionLog(
                    step_index=step_index,
                    agent_name=step.agent_name,
                    action=step.action,
                    input_summary=str(step.parameters)[:200],
                    output_summary=f"Error: {e}",
                    status="failed",
                    cost_usd=0.0,
                    duration_seconds=time.time() - step_start
                )
                execution_logs.append(log)
                raise
        
        return execution_logs, agent_outputs, total_cost
    
    def _extract_final_report(self, agent_outputs: List) -> str:
        """Extract final report from Writing Agent output"""
        for output in reversed(agent_outputs):
            if output.agent_name == "WritingAgent" and output.status == "success":
                if isinstance(output.output, dict):
                    return output.output.get("report", "No report generated")
                else:
                    return str(output.output)
        
        return "No report generated"
    
    def _evaluate_quality(self, report: str, logs: List[ExecutionLog]) -> float:
        """Evaluate output quality"""
        score = 5.0  # Base score
        
        # Check report length
        word_count = len(report.split())
        if word_count > 500:
            score += 1.0
        if word_count > 2000:
            score += 1.0
        
        # Check for citations
        if "[1]" in report or "[2]" in report:
            score += 1.0
        
        # Check execution success
        failed_steps = sum(1 for log in logs if log.status == "failed")
        if failed_steps == 0:
            score += 1.0
        
        # Check for references section
        if "参考文献" in report or "References" in report:
            score += 1.0
        
        return min(score, 10.0)

