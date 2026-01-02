"""
AgentKit Entry Point for Universal-SciAgent

This module provides the HTTP server entry point for AgentKit deployment.
"""
import os
import logging
import asyncio
import json
from typing import Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _normalize_env_vars():
    """Map lowercase env vars to uppercase for VeADK compatibility."""
    mappings = [
        ("model_agent_name", "MODEL_AGENT_NAME"),
        ("model_agent_api_key", "MODEL_AGENT_API_KEY"),
        ("model_agent_api_base", "MODEL_AGENT_API_BASE"),
        ("model_agent_provider", "MODEL_AGENT_PROVIDER"),
        ("model_embedding_name", "MODEL_EMBEDDING_NAME"),
        ("model_embedding_api_key", "MODEL_EMBEDDING_API_KEY"),
        ("model_embedding_api_base", "MODEL_EMBEDDING_API_BASE"),
    ]
    for lower_key, upper_key in mappings:
        lower_val = os.getenv(lower_key)
        if lower_val and not os.getenv(upper_key):
            os.environ[upper_key] = lower_val


# Normalize env vars before imports
_normalize_env_vars()

# Import VeADK and agent system
try:
    from veadk import Agent as VeADKAgent
    VEADK_AVAILABLE = True
except ImportError:
    VEADK_AVAILABLE = False

from backend.agents.sci_agent_system import get_sci_agent_system


# System prompt
SYSTEM_PROMPT = """You are Universal-SciAgent, a multi-agent scientific research assistant.
You help with literature review, hypothesis generation, experiment design, and report writing.
Supported domains: Computer Science, Materials Science, Biomedical, Physics, Chemistry."""


# Initialize VeADK Agent at module level (required for AgentKit)
if VEADK_AVAILABLE:
    agent = VeADKAgent(
        name="universal_sciagent",
        system_prompt=SYSTEM_PROMPT,
    )
    logger.info("VeADK Agent initialized at module level")
else:
    agent = None
    logger.warning("VeADK not available, agent is None")

# Global sci_system instance
sci_system = None


def init_agent():
    """Initialize the agent system."""
    global sci_system
    
    sci_system = get_sci_agent_system()
    logger.info("Universal-SciAgent initialized successfully")


async def process_request(user_input: str) -> str:
    """Process a user request."""
    input_lower = user_input.lower()
    
    # Detect domain
    domain = "computer_science"
    for d in ["physics", "chemistry", "biomedical", "materials_science"]:
        if d.replace("_", " ") in input_lower or d in input_lower:
            domain = d
            break
    
    try:
        result = await sci_system.literature_review(user_input, domain, max_papers=5)
        return result.output
    except Exception as e:
        logger.exception(f"Error: {e}")
        if VEADK_AVAILABLE and agent:
            return agent.run(user_input)
        return f"Error: {str(e)}"


def handle_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle incoming request."""
    # Extract input
    user_input = None
    if isinstance(event, dict):
        user_input = (
            event.get("input") or
            event.get("query") or
            event.get("message") or
            event.get("text") or
            event.get("prompt") or
            ""
        )
        # Check body
        body = event.get("body", {})
        if isinstance(body, dict) and not user_input:
            user_input = (
                body.get("input") or
                body.get("query") or
                body.get("message") or
                ""
            )
    elif isinstance(event, str):
        user_input = event
    
    if not user_input or not user_input.strip():
        return {
            "status": "success",
            "output": (
                "Welcome to Universal-SciAgent!\n\n"
                "I'm a scientific research assistant. Send me a research topic like:\n"
                "- 'transformer attention mechanism'\n"
                "- 'CRISPR gene editing'\n"
                "- 'quantum computing'"
            )
        }
    
    try:
        result = asyncio.run(process_request(user_input))
        return {"status": "success", "output": result}
    except Exception as e:
        return {"status": "error", "output": str(e)}


class RequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for AgentKit."""
    
    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")
    
    def _send_json_response(self, data: dict, status: int = 200):
        response = json.dumps(data, ensure_ascii=False)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(response.encode()))
        self.end_headers()
        self.wfile.write(response.encode())
    
    def do_GET(self):
        if self.path == "/health" or self.path == "/":
            self._send_json_response({
                "status": "ok",
                "message": "Universal-SciAgent is healthy"
            })
        elif self.path == "/domains":
            domains = sci_system.domain_manager.list_domains() if sci_system else []
            self._send_json_response({
                "status": "success",
                "domains": domains
            })
        else:
            self._send_json_response({"status": "error", "message": "Not found"}, 404)
    
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = {}
        
        if content_length > 0:
            raw_body = self.rfile.read(content_length)
            try:
                body = json.loads(raw_body.decode())
            except json.JSONDecodeError:
                body = {"input": raw_body.decode()}
        
        # Handle /invoke endpoint (AgentKit console)
        if self.path == "/invoke" or self.path == "/":
            result = handle_request(body)
            self._send_json_response(result)
        elif self.path == "/literature-review":
            topic = body.get("topic", body.get("input", ""))
            if topic:
                result = handle_request({"input": topic})
            else:
                result = {"status": "error", "output": "Missing topic"}
            self._send_json_response(result)
        else:
            # Default: treat as invoke
            result = handle_request(body)
            self._send_json_response(result)


def run_server(port: int = 8000):
    """Run the HTTP server."""
    server = HTTPServer(("0.0.0.0", port), RequestHandler)
    logger.info(f"Starting Universal-SciAgent server on port {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped")
        server.shutdown()


if __name__ == "__main__":
    # Initialize agent
    init_agent()
    
    # Run HTTP server (this will keep running)
    port = int(os.getenv("PORT", "8000"))
    run_server(port)
