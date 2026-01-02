"""Writing Agent for generating structured reports"""
import logging
from typing import Dict, Any, List

from .base_agent import BaseAgent
from ..core.models import AgentOutput, Hypothesis, Paper

logger = logging.getLogger(__name__)


class WritingAgent(BaseAgent):
    """
    Writing Agent responsibilities:
    1. Generate literature review reports
    2. Format hypothesis comparison tables
    3. Write detailed hypothesis descriptions
    4. Generate cross-disciplinary fusion reports
    5. Ensure proper citations and academic formatting
    """
    
    def __init__(self):
        super().__init__(name="WritingAgent", description="Structured report generation")
    
    async def execute(self, context: Dict[str, Any]) -> AgentOutput:
        """
        Execute report generation
        
        Expected context keys:
        - task_type: str - Type of report to generate
        - papers: List[Dict] - Literature data (for literature review)
        - hypotheses: List[Dict] - Hypothesis data (for hypothesis generation)
        - literature_context: Dict - Literature context
        - domains: List[str] - Research domains
        """
        self.log_progress("Generating structured report...")
        
        task_type = context.get("task_type", "literature_review")
        
        if task_type == "literature_review":
            report = await self._generate_literature_review(context)
        elif task_type == "hypothesis_generation":
            report = await self._generate_hypothesis_report(context)
        else:
            report = "Unsupported task type"
        
        output = {
            "report": report,
            "word_count": len(report.split()),
            "task_type": task_type
        }
        
        self.log_progress(f"✅ Generated report ({len(report.split())} words)")
        
        return self.create_output(
            action="report_generation",
            output=output,
            metadata={"task_type": task_type}
        )
    
    async def _generate_literature_review(self, context: Dict[str, Any]) -> str:
        """Generate literature review report"""
        papers = context.get("papers", [])
        literature_context = context.get("literature_context", {})
        keywords = context.get("keywords", [])
        domains = context.get("domains", [])
        
        # Prepare paper summaries
        papers_text = self._format_papers_for_review(papers[:10])
        
        system_prompt = """你是资深科研写作专家，擅长撰写高质量的学术综述。

撰写要求：
1. 使用学术语言，避免口语化
2. 所有关键结论必须有文献支撑，使用[1][2]格式引用
3. 结构清晰，逻辑严谨
4. 客观中立，避免主观判断
5. Markdown格式美化"""
        
        user_prompt = f"""请撰写一篇3000-5000字的学术综述报告。

研究主题: {', '.join(keywords)}
研究领域: {', '.join(domains)}

文献趋势总结:
{literature_context.get('summary', '')}

重点文献:
{papers_text}

报告结构：

# [自动生成标题]

## 1. 研究背景与意义 (500字)
- 研究领域介绍
- 当前挑战与重要性

## 2. 研究方法分类 (1000字)
- 按技术路线分类
- 每类方法的核心思想

## 3. 代表性工作 (1000字)
- 重点论文逐一介绍（每篇200字）
- 包含方法、创新点、实验结果

## 4. 技术对比与分析 (500字)
- 表格形式对比关键指标
- 优缺点分析

## 5. 未来研究方向 (500字)
- 未解决的问题
- 潜在的研究机会

## 参考文献
[按论文列表生成]

请生成完整报告："""
        
        try:
            report = await self.call_llm(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=6000
            )
            
            # Add references section if not included
            if "## 参考文献" not in report and "## References" not in report:
                report += "\n\n" + self._format_references(papers)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate literature review: {e}")
            return f"Failed to generate literature review: {e}"
    
    async def _generate_hypothesis_report(self, context: Dict[str, Any]) -> str:
        """Generate hypothesis comparison and detailed description report"""
        hypotheses_data = context.get("hypotheses", [])
        papers = context.get("papers", [])
        domains = context.get("domains", [])
        keywords = context.get("keywords", [])
        
        hypotheses = [Hypothesis(**h) for h in hypotheses_data]
        
        # Generate comparison table
        comparison_table = self._create_comparison_table(hypotheses)
        
        # Generate detailed descriptions for each hypothesis
        detailed_descriptions = []
        for i, hyp in enumerate(hypotheses, 1):
            description = await self._generate_hypothesis_description(hyp, i, domains)
            detailed_descriptions.append(description)
        
        # Combine into final report
        report = f"""# 研究假设方案报告

## 研究主题
- **领域**: {', '.join(domains)}
- **关键词**: {', '.join(keywords)}

## 方案对比

{comparison_table}

## 详细方案说明

{''.join(detailed_descriptions)}

## 参考文献

{self._format_references(papers)}
"""
        
        return report
    
    def _create_comparison_table(self, hypotheses: List[Hypothesis]) -> str:
        """Create Markdown comparison table for hypotheses"""
        table = "| 排名 | 假设陈述 | 创新点 | 可行性评分 | 预期影响 |\n"
        table += "|------|---------|--------|-----------|----------|\n"
        
        for i, hyp in enumerate(hypotheses, 1):
            statement = hyp.statement[:60] + "..." if len(hyp.statement) > 60 else hyp.statement
            innovation = hyp.innovation[:50] + "..." if len(hyp.innovation) > 50 else hyp.innovation
            score = f"{hyp.feasibility_score:.1f}/10" if hyp.feasibility_score else "未评估"
            impact = hyp.expected_impact[:40] + "..." if len(hyp.expected_impact) > 40 else hyp.expected_impact
            
            table += f"| {i} | {statement} | {innovation} | {score} | {impact} |\n"
        
        return table
    
    async def _generate_hypothesis_description(
        self,
        hypothesis: Hypothesis,
        index: int,
        domains: List[str]
    ) -> str:
        """Generate detailed description for a single hypothesis"""
        
        description = f"""
### 假设 {index}: {hypothesis.statement}

#### 理论依据
{hypothesis.rationale}

#### 创新点
{hypothesis.innovation}

#### 详细实验方案
{hypothesis.experiment_design if hypothesis.experiment_design else hypothesis.experiment_outline}

#### 预期影响
{hypothesis.expected_impact}

#### 可行性评估
"""
        
        if hypothesis.feasibility_score:
            description += f"**总评分**: {hypothesis.feasibility_score:.1f}/10\n\n"
            
            if hypothesis.feasibility_breakdown:
                description += "**评分细节**:\n"
                breakdown = hypothesis.feasibility_breakdown
                description += f"- 设备可得性: {breakdown.get('equipment', 0)}/3\n"
                description += f"- 成本: {breakdown.get('cost', 0)}/2\n"
                description += f"- 时间: {breakdown.get('time', 0)}/2\n"
                description += f"- 技术难度: {breakdown.get('difficulty', 0)}/3\n\n"
            
            if hypothesis.feasibility_reasoning:
                description += f"**评估理由**:\n{hypothesis.feasibility_reasoning}\n"
        else:
            description += "未进行可行性评估\n"
        
        description += "\n---\n"
        
        return description
    
    def _format_papers_for_review(self, papers: List[Dict[str, Any]]) -> str:
        """Format papers for literature review"""
        formatted = []
        
        for i, paper in enumerate(papers, 1):
            title = paper.get("title", "Unknown")
            authors = paper.get("authors", [])
            year = paper.get("year", "")
            abstract = paper.get("abstract", "")[:500]
            citations = paper.get("citations", 0)
            
            formatted.append(f"""
[{i}] **{title}**
作者: {', '.join(authors[:3])}{'等' if len(authors) > 3 else ''}
年份: {year} | 引用数: {citations}
摘要: {abstract}...
""")
        
        return "\n".join(formatted)
    
    def _format_references(self, papers: List[Dict[str, Any]]) -> str:
        """Format reference list"""
        references = []
        
        for i, paper in enumerate(papers, 1):
            title = paper.get("title", "Unknown")
            authors = paper.get("authors", [])
            year = paper.get("year", "")
            url = paper.get("url", "")
            
            # Format authors (last name, first initial)
            author_str = ", ".join(authors[:3])
            if len(authors) > 3:
                author_str += " et al."
            
            ref = f"[{i}] {author_str}. {title}. {year}."
            if url:
                ref += f" {url}"
            
            references.append(ref)
        
        return "\n".join(references)

