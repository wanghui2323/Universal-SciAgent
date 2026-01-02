"""Hypothesis Agent for generating research hypotheses"""
import logging
from typing import Dict, Any, List

from .base_agent import BaseAgent
from ..core.models import AgentOutput, Hypothesis
from ..utils.domain_manager import domain_manager

logger = logging.getLogger(__name__)


class HypothesisAgent(BaseAgent):
    """
    Hypothesis Agent responsibilities:
    1. Deep understanding of literature context
    2. Generate diverse hypotheses (5 candidates)
    3. Emphasize innovation and novelty
    4. Initial ranking based on innovation
    """
    
    def __init__(self):
        super().__init__(name="HypothesisAgent", description="Research hypothesis generation")
    
    async def execute(self, context: Dict[str, Any]) -> AgentOutput:
        """
        Execute hypothesis generation
        
        Expected context keys:
        - literature_context: LiteratureContext - From Literature Agent
        - domains: List[str] - Research domains
        - num_hypotheses: int - Number of hypotheses to generate (default 5)
        - keywords: List[str] - Research keywords
        """
        self.log_progress("Generating research hypotheses...")
        
        literature_context = context.get("literature_context", {})
        domains = context.get("domains", [])
        num_hypotheses = context.get("num_hypotheses", 5)
        keywords = context.get("keywords", [])
        
        # Get domain-specific prompt
        prompt_template = self._get_domain_prompt(domains)
        
        # Generate hypotheses
        hypotheses = await self._generate_hypotheses(
            literature_context,
            prompt_template,
            num_hypotheses,
            keywords
        )
        
        # Initial ranking based on innovation keywords
        ranked_hypotheses = self._rank_by_innovation(hypotheses)
        
        output = {
            "hypotheses": [h.dict() for h in ranked_hypotheses],
            "count": len(ranked_hypotheses)
        }
        
        self.log_progress(f"✅ Generated {len(ranked_hypotheses)} hypotheses")
        
        return self.create_output(
            action="hypothesis_generation",
            output=output,
            metadata={"domains": domains, "num_hypotheses": num_hypotheses}
        )
    
    def _get_domain_prompt(self, domains: List[str]) -> str:
        """Get domain-specific hypothesis generation prompt"""
        if len(domains) == 1:
            # Single domain
            domain = domain_manager.get_domain(domains[0])
            if domain:
                return domain.get_prompt("hypothesis_generation")
        else:
            # Cross-domain
            merged_config = domain_manager.get_merged_config(domains)
            return merged_config["prompts"].get("hypothesis_generation", "")
        
        # Fallback generic prompt
        return """你是资深科研人员。请基于文献生成创新性研究假设。
        
每个假设包含：
1. 假设陈述（一句话）
2. 理论依据（引用文献）
3. 创新点
4. 初步实验方案
5. 预期影响"""
    
    async def _generate_hypotheses(
        self,
        literature_context: Dict[str, Any],
        prompt_template: str,
        num_hypotheses: int,
        keywords: List[str]
    ) -> List[Hypothesis]:
        """Generate multiple hypothesis candidates"""
        
        # Prepare literature summary
        literature_summary = literature_context.get("summary", "")
        research_gaps = literature_context.get("research_gaps", "")
        key_methods = literature_context.get("key_methods", [])
        
        user_prompt = f"""{prompt_template}

研究主题关键词: {', '.join(keywords)}

文献趋势总结:
{literature_summary}

研究空白:
{research_gaps}

当前主要方法: {', '.join(key_methods) if key_methods else '未提取'}

请生成 {num_hypotheses} 个创新性研究假设。每个假设必须包含以下结构：

---
**假设 1:**
[假设陈述]：[一句话清晰陈述]

[理论依据]：[200字，引用3-5篇文献，说明理论基础和现有方法的局限性]

[创新点]：[100字，说明与现有研究的差异和创新之处]

[初步实验方案]：[300字，概述验证思路、实验步骤、预期数据]

[预期影响]：[100字，说明成功后的科学意义和应用价值]

---
[重复以上结构，生成剩余假设]
"""
        
        try:
            response = await self.call_llm(
                prompt=user_prompt,
                system_prompt="你是资深科研专家，擅长提出创新性研究假设。",
                max_tokens=4000,
                temperature=0.8  # Higher temperature for creativity
            )
            
            # Parse response into Hypothesis objects
            hypotheses = self._parse_hypotheses(response)
            
            return hypotheses
            
        except Exception as e:
            self.logger.error(f"Failed to generate hypotheses: {e}")
            return []
    
    def _parse_hypotheses(self, response: str) -> List[Hypothesis]:
        """Parse LLM response into Hypothesis objects"""
        hypotheses = []
        
        # Split by hypothesis markers
        parts = response.split("**假设")
        
        for part in parts[1:]:  # Skip first empty part
            try:
                # Extract sections
                statement = self._extract_section(part, "[假设陈述]", "[理论依据]")
                rationale = self._extract_section(part, "[理论依据]", "[创新点]")
                innovation = self._extract_section(part, "[创新点]", "[初步实验方案]")
                experiment_outline = self._extract_section(part, "[初步实验方案]", "[预期影响]")
                expected_impact = self._extract_section(part, "[预期影响]", "---")
                
                if statement:
                    hypothesis = Hypothesis(
                        statement=statement.strip(),
                        rationale=rationale.strip() if rationale else "",
                        innovation=innovation.strip() if innovation else "",
                        experiment_outline=experiment_outline.strip() if experiment_outline else "",
                        expected_impact=expected_impact.strip() if expected_impact else ""
                    )
                    hypotheses.append(hypothesis)
                    
            except Exception as e:
                self.logger.warning(f"Failed to parse hypothesis: {e}")
                continue
        
        # If parsing fails, create a fallback hypothesis
        if not hypotheses:
            self.logger.warning("Failed to parse hypotheses, using raw response")
            hypotheses.append(Hypothesis(
                statement="Generated hypothesis (parsing failed)",
                rationale=response[:500],
                innovation="",
                experiment_outline="",
                expected_impact=""
            ))
        
        return hypotheses
    
    def _extract_section(self, text: str, start_marker: str, end_marker: str) -> str:
        """Extract text between two markers"""
        try:
            start_idx = text.find(start_marker)
            if start_idx == -1:
                return ""
            
            start_idx += len(start_marker)
            
            end_idx = text.find(end_marker, start_idx)
            if end_idx == -1:
                # Take rest of text
                return text[start_idx:].strip()
            
            return text[start_idx:end_idx].strip()
        except:
            return ""
    
    def _rank_by_innovation(self, hypotheses: List[Hypothesis]) -> List[Hypothesis]:
        """Rank hypotheses by innovation keywords"""
        innovation_keywords = [
            "novel", "breakthrough", "unprecedented", "first time", "创新", "首次",
            "突破", "前所未有", "new", "innovative", "pioneering", "革命性"
        ]
        
        scored_hypotheses = []
        for hyp in hypotheses:
            # Count innovation keywords in statement and innovation sections
            text = (hyp.statement + " " + hyp.innovation).lower()
            score = sum(1 for kw in innovation_keywords if kw in text)
            scored_hypotheses.append((score, hyp))
        
        # Sort by score (descending)
        scored_hypotheses.sort(key=lambda x: x[0], reverse=True)
        
        return [hyp for score, hyp in scored_hypotheses]

