"""
Universal-SciAgent Simple Examples

Demonstrates the core capabilities of Universal-SciAgent built on VeADK:
1. Literature Review
2. Hypothesis Generation
3. Experiment Design
4. Full Research Workflow

All powered by VeADK's native multi-agent, memory, and workflow features.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.agents.sci_agent_system import get_sci_agent_system
from backend.utils.cost_tracker import get_cost_tracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_literature_review():
    """
    Example 1: Literature Review
    
    Uses VeADK's:
    - Literature Agent with tool calling (arXiv, Semantic Scholar)
    - Memory system for storing papers
    - Cost tracking
    """
    print("\n" + "="*80)
    print("Example 1: Literature Review")
    print("="*80 + "\n")
    
    # Get the sci-agent system (VeADK-based)
    system = get_sci_agent_system()
    
    # Define research topic
    topic = "深度学习在计算机视觉中的最新进展"
    domain = "computer_science"
    
    print(f"Topic: {topic}")
    print(f"Domain: {domain}")
    print("\nExecuting literature review workflow...\n")
    
    # Execute literature review (VeADK handles agent coordination)
    result = await system.literature_review(
        topic=topic,
        domain=domain,
        max_papers=20
    )
    
    print("\n--- Results ---")
    print(f"Agent: {result.agent_name}")
    print(f"Action: {result.action}")
    print(f"Status: {result.status}")
    print(f"Cost: ${result.cost_usd:.4f}")
    print(f"\nOutput Preview:")
    output_str = str(result.output)
    print(output_str[:500] + "..." if len(output_str) > 500 else output_str)
    
    # Get cost statistics
    cost_tracker = get_cost_tracker()
    stats = cost_tracker.get_statistics()
    print(f"\n--- Cost Statistics ---")
    print(f"Total Cost: ${stats['total_cost_usd']:.4f}")
    print(f"Total Tokens: {stats['total_tokens']:,}")
    print(f"Total Calls: {stats['total_calls']}")


async def example_hypothesis_generation():
    """
    Example 2: Hypothesis Generation
    
    Uses VeADK's:
    - Hypothesis Agent
    - Memory retrieval for literature context
    - Multi-agent coordination
    """
    print("\n" + "="*80)
    print("Example 2: Hypothesis Generation")
    print("="*80 + "\n")
    
    system = get_sci_agent_system()
    
    # Simulated literature review context
    literature_context = """
    Recent advances in deep learning have shown remarkable progress in computer vision tasks.
    However, current models still struggle with:
    1. Out-of-distribution generalization
    2. Few-shot learning scenarios
    3. Adversarial robustness
    
    Key papers suggest that:
    - Self-supervised learning improves feature representations
    - Meta-learning enhances adaptation to new tasks
    - Attention mechanisms help model focus on relevant features
    """
    
    domain = "computer_science"
    
    print("Generating research hypotheses based on literature...\n")
    
    # Generate hypotheses (VeADK coordinates with Literature Agent's memory)
    result = await system.generate_hypothesis(
        literature_context=literature_context,
        domain=domain
    )
    
    print("\n--- Generated Hypotheses ---")
    print(result.output)
    print(f"\nCost: ${result.cost_usd:.4f}")


async def example_experiment_design():
    """
    Example 3: Experiment Design
    
    Uses VeADK's:
    - Experiment Design Agent
    - Workflow orchestration
    """
    print("\n" + "="*80)
    print("Example 3: Experiment Design")
    print("="*80 + "\n")
    
    system = get_sci_agent_system()
    
    # Hypothesis to validate
    hypothesis = """
    Hypothesis: Combining self-supervised pre-training with meta-learning
    can significantly improve few-shot image classification performance
    on out-of-distribution datasets.
    
    Expected Outcome: 10-15% accuracy improvement over baseline methods
    with only 5 examples per class.
    """
    
    domain = "computer_science"
    
    print("Designing experiments to validate hypothesis...\n")
    
    # Design experiment (VeADK manages the experiment design workflow)
    result = await system.design_experiment(
        hypothesis=hypothesis,
        domain=domain
    )
    
    print("\n--- Experiment Design ---")
    print(result.output)
    print(f"\nCost: ${result.cost_usd:.4f}")


async def example_full_research_workflow():
    """
    Example 4: Full Research Workflow
    
    Uses VeADK's:
    - Complete multi-agent workflow
    - Master Agent coordination
    - All specialist agents (Literature, Hypothesis, Experiment, Writing)
    - Automatic memory management
    - Cost tracking across all steps
    """
    print("\n" + "="*80)
    print("Example 4: Full Research Workflow")
    print("="*80 + "\n")
    
    system = get_sci_agent_system()
    cost_tracker = get_cost_tracker()
    
    # Reset cost tracker for this workflow
    cost_tracker.reset()
    
    # Define research task
    task = """
    研究任务：探索视觉Transformer在小样本图像分类中的应用
    
    要求：
    1. 调研相关文献（Vision Transformers, Few-shot Learning）
    2. 提出创新性研究假设
    3. 设计实验验证方案
    4. 撰写研究报告
    """
    
    domain = "computer_science"
    
    print(f"Task: {task[:100]}...")
    print(f"Domain: {domain}")
    print("\n" + "-"*80)
    print("Executing full research workflow with VeADK multi-agent system...")
    print("-"*80 + "\n")
    
    # Execute full workflow (VeADK orchestrates all agents)
    result = await system.run_task(
        task=task,
        domain=domain,
        task_type="full_research"
    )
    
    print("\n" + "="*80)
    print("WORKFLOW COMPLETED")
    print("="*80)
    
    print(f"\nStatus: {result.get('status')}")
    print(f"Total Cost: ${result.get('cost_usd', 0):.4f}")
    
    # Get detailed cost breakdown
    stats = cost_tracker.get_statistics()
    
    print("\n--- Cost Breakdown by Agent ---")
    for agent_name, agent_stats in stats['cost_by_agent'].items():
        print(f"  {agent_name}:")
        print(f"    Cost: ${agent_stats['cost']:.4f}")
        print(f"    Tokens: {agent_stats['input_tokens'] + agent_stats['output_tokens']:,}")
        print(f"    Calls: {agent_stats['calls']}")
    
    print("\n--- Cost Breakdown by Model ---")
    for model_name, model_stats in stats['cost_by_model'].items():
        print(f"  {model_name}:")
        print(f"    Cost: ${model_stats['cost']:.4f}")
        print(f"    Tokens: {model_stats['input_tokens'] + model_stats['output_tokens']:,}")
        print(f"    Calls: {model_stats['calls']}")
    
    print("\n--- Results Preview ---")
    if isinstance(result.get('result'), dict):
        for key, value in result['result'].items():
            print(f"\n{key}:")
            print(str(value)[:300] + "...")
    else:
        print(str(result.get('result', ''))[:500] + "...")


async def main():
    """Run all examples"""
    print("\n")
    print("="*80)
    print("Universal-SciAgent Examples (Powered by VeADK)")
    print("="*80)
    print("\nVeADK Features Used:")
    print("  ✓ Multi-Agent System (Master + 4 Specialists)")
    print("  ✓ Memory Management (Short-term + Long-term)")
    print("  ✓ Tool Integration (arXiv, Semantic Scholar, PubMed)")
    print("  ✓ Workflow Orchestration (Hierarchical)")
    print("  ✓ Cost Tracking & Observability")
    print("="*80)
    
    # Choose which example to run
    import sys
    if len(sys.argv) > 1:
        example_num = int(sys.argv[1])
    else:
        example_num = None
    
    try:
        if example_num == 1 or example_num is None:
            await example_literature_review()
        
        if example_num == 2 or example_num is None:
            await example_hypothesis_generation()
        
        if example_num == 3 or example_num is None:
            await example_experiment_design()
        
        if example_num == 4 or example_num is None:
            await example_full_research_workflow()
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise
    
    print("\n" + "="*80)
    print("All examples completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Usage:
    # python examples/simple_example.py        # Run all examples
    # python examples/simple_example.py 1      # Run example 1 only
    # python examples/simple_example.py 4      # Run example 4 only
    
    asyncio.run(main())
