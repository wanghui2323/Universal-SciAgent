"""
VeADK Native Cost Tracking for Universal-SciAgent

This module implements cost tracking using VeADK's native CostCallback system
for accurate token counting and cost calculation.

Reference: https://volcengine.github.io/veadk-python/
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

# VeADK Cost Callback
try:
    from veadk import CostCallback
    VEADK_COST_SUPPORT = True
except ImportError:
    VEADK_COST_SUPPORT = False
    # Fallback base class
    class CostCallback:
        pass

logger = logging.getLogger(__name__)


class VeADKCostTracker(CostCallback):
    """
    Cost tracking using VeADK's native callback system
    
    Automatically tracks:
    - Input/output tokens per call
    - Cost per model
    - Total cost per session
    - Cost per agent
    - Cost per workflow
    
    Supports multiple models with different pricing:
    - doubao-pro-32k: ¥0.0008/1K input, ¥0.002/1K output
    - doubao-pro-128k: ¥0.0015/1K input, ¥0.003/1K output
    - doubao-lite-32k: ¥0.0003/1K input, ¥0.0006/1K output
    """
    
    # Model pricing (USD per 1K tokens)
    MODEL_PRICING = {
        "doubao-pro-32k": {"input": 0.0008, "output": 0.002},
        "doubao-pro-128k": {"input": 0.0015, "output": 0.003},
        "doubao-lite-32k": {"input": 0.0003, "output": 0.0006},
        "doubao-embedding": {"input": 0.0002, "output": 0.0},
        # OpenAI models (fallback)
        "gpt-4o": {"input": 0.0025, "output": 0.010},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    }
    
    def __init__(self):
        """Initialize cost tracker"""
        super().__init__()
        self.total_cost = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.call_count = 0
        self.cost_by_agent = {}
        self.cost_by_model = {}
        self.call_history = []
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("VeADK Cost Tracker initialized")
    
    def on_llm_call(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str,
        agent_name: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Callback invoked by VeADK after each LLM call
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model name
            agent_name: Name of the calling agent
            **kwargs: Additional metadata
        """
        # Calculate cost
        cost = self.calculate_cost(input_tokens, output_tokens, model)
        
        # Update totals
        self.total_cost += cost
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.call_count += 1
        
        # Track by agent
        if agent_name:
            if agent_name not in self.cost_by_agent:
                self.cost_by_agent[agent_name] = {
                    "cost": 0.0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "calls": 0
                }
            self.cost_by_agent[agent_name]["cost"] += cost
            self.cost_by_agent[agent_name]["input_tokens"] += input_tokens
            self.cost_by_agent[agent_name]["output_tokens"] += output_tokens
            self.cost_by_agent[agent_name]["calls"] += 1
        
        # Track by model
        if model not in self.cost_by_model:
            self.cost_by_model[model] = {
                "cost": 0.0,
                "input_tokens": 0,
                "output_tokens": 0,
                "calls": 0
            }
        self.cost_by_model[model]["cost"] += cost
        self.cost_by_model[model]["input_tokens"] += input_tokens
        self.cost_by_model[model]["output_tokens"] += output_tokens
        self.cost_by_model[model]["calls"] += 1
        
        # Record call
        call_record = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "agent": agent_name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        }
        self.call_history.append(call_record)
        
        # Log
        self.logger.info(
            f"LLM Call #{self.call_count} | "
            f"Agent: {agent_name or 'unknown'} | "
            f"Model: {model} | "
            f"Tokens: {input_tokens}+{output_tokens} | "
            f"Cost: ${cost:.4f} | "
            f"Total: ${self.total_cost:.4f}"
        )
    
    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str
    ) -> float:
        """
        Calculate cost for a single LLM call
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model name
        
        Returns:
            Cost in USD
        """
        # Get pricing for model
        pricing = self.MODEL_PRICING.get(model)
        
        if not pricing:
            # Try to find similar model
            model_lower = model.lower()
            for model_key in self.MODEL_PRICING:
                if model_key in model_lower:
                    pricing = self.MODEL_PRICING[model_key]
                    break
        
        if not pricing:
            # Default pricing (conservative estimate)
            self.logger.warning(f"Unknown model: {model}, using default pricing")
            pricing = {"input": 0.001, "output": 0.002}
        
        # Calculate cost
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        return total_cost
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count from text
        
        Rule of thumb: 1 token ≈ 3-4 characters for English
        For Chinese: 1 token ≈ 1.5-2 characters
        
        Args:
            text: Input text
        
        Returns:
            Estimated token count
        """
        # Simple estimation
        # A more accurate method would use tiktoken or actual model tokenizer
        char_count = len(text)
        
        # Check if text is mostly Chinese
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        if chinese_chars > char_count * 0.3:
            # Mostly Chinese
            return int(char_count / 1.5)
        else:
            # Mostly English
            return int(char_count / 3.5)
    
    def estimate_cost(self, input_text: str, output_text: str, model: str) -> float:
        """
        Estimate cost from text (when actual tokens not available)
        
        Args:
            input_text: Input text
            output_text: Output text
            model: Model name
        
        Returns:
            Estimated cost in USD
        """
        input_tokens = self.estimate_tokens(input_text)
        output_tokens = self.estimate_tokens(output_text)
        return self.calculate_cost(input_tokens, output_tokens, model)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get cost tracking statistics
        
        Returns:
            Dict with statistics
        """
        return {
            "total_cost_usd": round(self.total_cost, 4),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_calls": self.call_count,
            "avg_cost_per_call": round(self.total_cost / max(self.call_count, 1), 4),
            "cost_by_agent": self.cost_by_agent,
            "cost_by_model": self.cost_by_model
        }
    
    def reset(self) -> None:
        """Reset all tracking data"""
        self.total_cost = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.call_count = 0
        self.cost_by_agent = {}
        self.cost_by_model = {}
        self.call_history = []
        self.logger.info("Cost tracker reset")
    
    def export_history(self, format: str = "json") -> Any:
        """
        Export call history
        
        Args:
            format: Export format ('json', 'csv', 'dict')
        
        Returns:
            Exported data
        """
        if format == "json":
            import json
            return json.dumps(self.call_history, indent=2)
        elif format == "csv":
            import csv
            import io
            output = io.StringIO()
            if self.call_history:
                writer = csv.DictWriter(output, fieldnames=self.call_history[0].keys())
                writer.writeheader()
                writer.writerows(self.call_history)
            return output.getvalue()
        else:  # dict
            return self.call_history


class SimpleCostTracker:
    """
    Simple fallback cost tracker (if VeADK CostCallback not available)
    """
    
    def __init__(self):
        """Initialize simple tracker"""
        self.tracker = VeADKCostTracker()
        logger.warning("Using simple cost tracker (VeADK CostCallback not available)")
    
    def track_call(
        self,
        input_text: str,
        output_text: str,
        model: str,
        agent_name: Optional[str] = None
    ) -> float:
        """
        Manually track a call
        
        Args:
            input_text: Input text
            output_text: Output text
            model: Model name
            agent_name: Agent name
        
        Returns:
            Estimated cost
        """
        input_tokens = self.tracker.estimate_tokens(input_text)
        output_tokens = self.tracker.estimate_tokens(output_text)
        
        # Call the callback manually
        self.tracker.on_llm_call(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model=model,
            agent_name=agent_name
        )
        
        return self.tracker.calculate_cost(input_tokens, output_tokens, model)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics"""
        return self.tracker.get_statistics()


# Singleton instance
_cost_tracker: Optional[VeADKCostTracker] = None


def get_cost_tracker() -> VeADKCostTracker:
    """Get or create the singleton cost tracker"""
    global _cost_tracker
    if _cost_tracker is None:
        if VEADK_COST_SUPPORT:
            _cost_tracker = VeADKCostTracker()
        else:
            _cost_tracker = SimpleCostTracker().tracker
    return _cost_tracker

