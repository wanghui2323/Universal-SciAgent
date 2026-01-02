"""Agent modules"""
from .literature_agent import LiteratureAgent
from .hypothesis_agent import HypothesisAgent
from .experiment_design_agent import ExperimentDesignAgent
from .writing_agent import WritingAgent
from .master_agent import MasterAgent

__all__ = [
    "LiteratureAgent",
    "HypothesisAgent",
    "ExperimentDesignAgent",
    "WritingAgent",
    "MasterAgent"
]
