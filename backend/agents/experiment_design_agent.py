"""Experiment Design Agent for designing validation experiments"""
import logging
from typing import Dict, Any, List

from .base_agent import BaseAgent
from ..core.models import AgentOutput, Hypothesis
from ..utils.domain_manager import domain_manager

logger = logging.getLogger(__name__)


class ExperimentDesignAgent(BaseAgent):
    """
    Experiment Design Agent responsibilities:
    1. Design detailed experimental protocols for each hypothesis
    2. Evaluate feasibility (equipment, cost, time, difficulty)
    3. Rank hypotheses by feasibility score
    4. Select top N hypotheses
    """
    
    def __init__(self):
        super().__init__(name="ExperimentDesignAgent", description="Experimental protocol design and feasibility evaluation")
    
    async def execute(self, context: Dict[str, Any]) -> AgentOutput:
        """
        Execute experiment design and feasibility evaluation
        
        Expected context keys:
        - hypotheses: List[Dict] - From Hypothesis Agent
        - domains: List[str] - Research domains
        - num_final: int - Number of final hypotheses to select (default 3)
        """
        self.log_progress("Designing experiments and evaluating feasibility...")
        
        hypotheses_data = context.get("hypotheses", [])
        domains = context.get("domains", [])
        num_final = context.get("num_final", 3)
        
        # Convert to Hypothesis objects
        hypotheses = [Hypothesis(**h) for h in hypotheses_data]
        
        # Get domain-specific methodology
        methodology = self._get_domain_methodology(domains)
        
        # Design experiments for each hypothesis
        hypotheses_with_design = []
        for hyp in hypotheses:
            designed_hyp = await self._design_experiment(hyp, methodology, domains)
            hypotheses_with_design.append(designed_hyp)
        
        # Rank by feasibility score
        ranked_hypotheses = sorted(
            hypotheses_with_design,
            key=lambda h: h.feasibility_score or 0,
            reverse=True
        )
        
        # Select top N
        final_hypotheses = ranked_hypotheses[:num_final]
        
        output = {
            "hypotheses": [h.dict() for h in final_hypotheses],
            "all_scored": [h.dict() for h in ranked_hypotheses],
            "ranking_summary": self._create_ranking_summary(ranked_hypotheses)
        }
        
        self.log_progress(f"✅ Designed experiments for {len(hypotheses)} hypotheses, selected top {num_final}")
        
        return self.create_output(
            action="experiment_design",
            output=output,
            metadata={"domains": domains, "num_evaluated": len(hypotheses)}
        )
    
    def _get_domain_methodology(self, domains: List[str]) -> str:
        """Get domain-specific experimental methodology"""
        if len(domains) == 1:
            domain = domain_manager.get_domain(domains[0])
            if domain:
                return domain.methodology_template
        else:
            merged_config = domain_manager.get_merged_config(domains)
            return merged_config.get("methodology_template", "")
        
        return "Standard scientific methodology"
    
    async def _design_experiment(
        self,
        hypothesis: Hypothesis,
        methodology: str,
        domains: List[str]
    ) -> Hypothesis:
        """Design detailed experiment for a hypothesis and evaluate feasibility"""
        
        # Get domain-specific experiment design prompt
        design_prompt = self._get_design_prompt(domains)
        
        user_prompt = f"""{design_prompt}

标准方法论:
{methodology}

研究假设:
{hypothesis.statement}

理论依据:
{hypothesis.rationale}

初步方案:
{hypothesis.experiment_outline}

请设计详细实验方案（800-1200字），包含：

1. **实验步骤**（详细到可执行）
2. **所需设备与材料**（列出具体型号和供应商）
3. **预期数据格式**（具体测量指标）
4. **数据分析方法**（统计方法、软件工具）
5. **成功标准**（量化指标）

然后，评估可行性（0-10分）：
- 设备可得性（0-3分）
- 成本（0-2分）
- 时间（0-2分）
- 技术难度（0-3分）

输出格式：
[实验方案]: [详细方案内容]

[可行性评估]:
设备可得性: X/3 - [理由]
成本: X/2 - [理由]
时间: X/2 - [理由]
技术难度: X/3 - [理由]
总分: X/10
"""
        
        try:
            response = await self.call_llm(
                prompt=user_prompt,
                system_prompt="你是经验丰富的实验科学家，擅长设计严谨的实验方案。",
                max_tokens=2000
            )
            
            # Parse experiment design
            experiment_design = self._extract_section(response, "[实验方案]", "[可行性评估]")
            
            # Parse feasibility evaluation
            feasibility_text = self._extract_section(response, "[可行性评估]", "")
            feasibility_score, breakdown, reasoning = self._parse_feasibility(feasibility_text)
            
            # Update hypothesis
            hypothesis.experiment_design = experiment_design
            hypothesis.feasibility_score = feasibility_score
            hypothesis.feasibility_breakdown = breakdown
            hypothesis.feasibility_reasoning = reasoning
            
            return hypothesis
            
        except Exception as e:
            self.logger.error(f"Failed to design experiment: {e}")
            # Return hypothesis with default score
            hypothesis.feasibility_score = 5.0
            hypothesis.feasibility_reasoning = f"Failed to evaluate: {e}"
            return hypothesis
    
    def _get_design_prompt(self, domains: List[str]) -> str:
        """Get domain-specific experiment design prompt"""
        if len(domains) == 1:
            domain = domain_manager.get_domain(domains[0])
            if domain:
                return domain.get_prompt("experiment_design")
        else:
            merged_config = domain_manager.get_merged_config(domains)
            return merged_config["prompts"].get("experiment_design", "")
        
        return "Please design a detailed experimental protocol."
    
    def _extract_section(self, text: str, start_marker: str, end_marker: str) -> str:
        """Extract text between markers"""
        try:
            start_idx = text.find(start_marker)
            if start_idx == -1:
                return text  # Return full text if marker not found
            
            start_idx += len(start_marker)
            
            if end_marker:
                end_idx = text.find(end_marker, start_idx)
                if end_idx != -1:
                    return text[start_idx:end_idx].strip()
            
            return text[start_idx:].strip()
        except:
            return text
    
    def _parse_feasibility(self, text: str) -> tuple:
        """Parse feasibility evaluation from text"""
        try:
            lines = text.split("\n")
            scores = {}
            reasoning_lines = []
            
            for line in lines:
                if "设备可得性" in line or "Equipment" in line:
                    score = self._extract_score(line, max_score=3)
                    scores["equipment"] = score
                elif "成本" in line or "Cost" in line:
                    score = self._extract_score(line, max_score=2)
                    scores["cost"] = score
                elif "时间" in line or "Time" in line:
                    score = self._extract_score(line, max_score=2)
                    scores["time"] = score
                elif "技术难度" in line or "Difficulty" in line:
                    score = self._extract_score(line, max_score=3)
                    scores["difficulty"] = score
                elif "总分" in line or "Total" in line:
                    total_score = self._extract_score(line, max_score=10)
                
                reasoning_lines.append(line)
            
            # Calculate total if not provided
            if "total_score" not in locals():
                total_score = sum(scores.values())
            
            reasoning = "\n".join(reasoning_lines)
            
            return total_score, scores, reasoning
            
        except Exception as e:
            self.logger.warning(f"Failed to parse feasibility: {e}")
            return 5.0, {}, text
    
    def _extract_score(self, line: str, max_score: int) -> float:
        """Extract numeric score from a line"""
        import re
        # Try to find pattern like "X/Y"
        match = re.search(r'(\d+\.?\d*)/(\d+)', line)
        if match:
            return float(match.group(1))
        
        # Try to find standalone number
        match = re.search(r'(\d+\.?\d*)', line)
        if match:
            score = float(match.group(1))
            return min(score, max_score)
        
        return max_score / 2  # Default to middle value
    
    def _create_ranking_summary(self, hypotheses: List[Hypothesis]) -> str:
        """Create a summary of hypothesis ranking"""
        summary_lines = ["假设排名 (按可行性评分):"]
        
        for i, hyp in enumerate(hypotheses, 1):
            score = hyp.feasibility_score or 0
            summary_lines.append(f"{i}. {hyp.statement[:80]}... (评分: {score:.1f}/10)")
        
        return "\n".join(summary_lines)

