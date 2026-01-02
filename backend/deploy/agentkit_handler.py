"""
AgentKit Handler for Universal-SciAgent

This module provides the entry point for deploying Universal-SciAgent
to Volcengine AgentKit (VeFaaS).

Reference: https://github.com/volcengine/agentkit-sdk-python
"""

import asyncio
import json
import logging
from typing import Dict, Any

from ..agents.sci_agent_system import get_sci_agent_system

logger = logging.getLogger(__name__)

# Initialize the system (singleton)
_system = None


def get_system():
    """Get or create the system instance"""
    global _system
    if _system is None:
        _system = get_sci_agent_system()
    return _system


async def literature_review(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle literature review request
    
    Args:
        params: {
            "topic": str,
            "domain": str (default: "computer_science"),
            "max_papers": int (default: 20)
        }
    """
    system = get_system()
    
    topic = params.get("topic", "")
    domain = params.get("domain", "computer_science")
    max_papers = params.get("max_papers", 20)
    
    if not topic:
        return {"error": "topic is required"}
    
    result = await system.literature_review(
        topic=topic,
        domain=domain,
        max_papers=max_papers
    )
    
    return {
        "status": result.status,
        "agent": result.agent_name,
        "action": result.action,
        "output": str(result.output),
        "cost_usd": result.cost_usd
    }


async def generate_hypothesis(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle hypothesis generation request
    
    Args:
        params: {
            "literature_context": str,
            "domain": str (default: "computer_science")
        }
    """
    system = get_system()
    
    context = params.get("literature_context", "")
    domain = params.get("domain", "computer_science")
    
    if not context:
        return {"error": "literature_context is required"}
    
    result = await system.generate_hypothesis(
        literature_context=context,
        domain=domain
    )
    
    return {
        "status": result.status,
        "agent": result.agent_name,
        "action": result.action,
        "output": str(result.output),
        "cost_usd": result.cost_usd
    }


async def design_experiment(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle experiment design request
    
    Args:
        params: {
            "hypothesis": str,
            "domain": str (default: "computer_science")
        }
    """
    system = get_system()
    
    hypothesis = params.get("hypothesis", "")
    domain = params.get("domain", "computer_science")
    
    if not hypothesis:
        return {"error": "hypothesis is required"}
    
    result = await system.design_experiment(
        hypothesis=hypothesis,
        domain=domain
    )
    
    return {
        "status": result.status,
        "agent": result.agent_name,
        "action": result.action,
        "output": str(result.output),
        "cost_usd": result.cost_usd
    }


async def write_report(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle report writing request
    
    Args:
        params: {
            "research_context": str,
            "domain": str (default: "computer_science")
        }
    """
    system = get_system()
    
    context = params.get("research_context", "")
    domain = params.get("domain", "computer_science")
    
    if not context:
        return {"error": "research_context is required"}
    
    result = await system.write_report(
        research_context=context,
        domain=domain
    )
    
    return {
        "status": result.status,
        "agent": result.agent_name,
        "action": result.action,
        "output": str(result.output),
        "cost_usd": result.cost_usd
    }


def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "universal-sciagent",
        "version": "1.0.0"
    }


def get_domains() -> Dict[str, Any]:
    """List available research domains"""
    return {
        "domains": [
            {"id": "computer_science", "name": "计算机科学"},
            {"id": "biomedical", "name": "生物医学"},
            {"id": "materials_science", "name": "材料科学"},
            {"id": "physics", "name": "物理学"},
            {"id": "chemistry", "name": "化学"}
        ]
    }


# Main handler for AgentKit
def handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """
    Main handler function for AgentKit deployment
    
    Args:
        event: {
            "path": str,  # API path
            "method": str,  # HTTP method
            "body": dict,  # Request body
            "query": dict  # Query parameters
        }
        context: AgentKit context (optional)
    
    Returns:
        Response dictionary
    """
    path = event.get("path", "")
    method = event.get("method", "GET")
    body = event.get("body", {})
    
    # Parse body if it's a string
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            body = {}
    
    logger.info(f"Handling request: {method} {path}")
    
    try:
        # Route requests
        if path == "/health":
            return {"statusCode": 200, "body": health_check()}
        
        elif path == "/domains":
            return {"statusCode": 200, "body": get_domains()}
        
        elif path == "/literature-review" and method == "POST":
            result = asyncio.run(literature_review(body))
            return {"statusCode": 200, "body": result}
        
        elif path == "/hypothesis-generation" and method == "POST":
            result = asyncio.run(generate_hypothesis(body))
            return {"statusCode": 200, "body": result}
        
        elif path == "/experiment-design" and method == "POST":
            result = asyncio.run(design_experiment(body))
            return {"statusCode": 200, "body": result}
        
        elif path == "/write-report" and method == "POST":
            result = asyncio.run(write_report(body))
            return {"statusCode": 200, "body": result}
        
        else:
            return {
                "statusCode": 404,
                "body": {"error": f"Unknown path: {path}"}
            }
    
    except Exception as e:
        logger.error(f"Error handling request: {e}")
        return {
            "statusCode": 500,
            "body": {"error": str(e)}
        }

