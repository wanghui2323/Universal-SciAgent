"""Tests for agent modules using VeADK Native"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime


class TestBaseAgent:
    """Test BaseAgent class"""
    
    def test_base_agent_import(self):
        """Test that BaseAgent can be imported"""
        from backend.agents.base_agent import BaseAgent
        assert BaseAgent is not None
    
    def test_base_agent_is_abstract(self):
        """Test that BaseAgent is abstract"""
        from backend.agents.base_agent import BaseAgent
        
        # BaseAgent requires VeADK to be mocked
        with patch('backend.agents.base_agent.VeADKAgent'):
            with patch('backend.agents.base_agent.FunctionTool'):
                with pytest.raises(TypeError):
                    BaseAgent("test_agent")
    
    def test_create_output_method(self):
        """Test create_output method"""
        from backend.agents.base_agent import BaseAgent
        from backend.core.models import AgentOutput
        
        class TestAgent(BaseAgent):
            async def execute(self, context):
                return self.create_output(action="test", output="test", status="success")
        
        with patch('backend.agents.base_agent.VeADKAgent') as mock_agent:
            with patch('backend.agents.base_agent.FunctionTool'):
                mock_agent.return_value = MagicMock()
                agent = TestAgent("test_agent", "Test description")
                output = agent.create_output(action="test", output={"data": "test"}, status="success")
                
                assert isinstance(output, AgentOutput)
                assert output.agent_name == "test_agent"


class TestAgentModels:
    """Test agent data models"""
    
    def test_agent_output_model(self):
        """Test AgentOutput model"""
        from backend.core.models import AgentOutput
        
        output = AgentOutput(
            agent_name="test_agent",
            action="test_action",
            timestamp=datetime.now(),
            status="success",
            output={"result": "test"},
            metadata={},
            cost_usd=0.01
        )
        
        assert output.agent_name == "test_agent"
        assert output.status == "success"


class TestSciAgentSystem:
    """Test SciAgentSystem with VeADK Native"""
    
    def test_sci_agent_system_import(self):
        """Test that UniversalSciAgentSystem can be imported"""
        from backend.agents.sci_agent_system import UniversalSciAgentSystem
        assert UniversalSciAgentSystem is not None
    
    @patch('backend.agents.sci_agent_system.Agent')
    @patch('backend.agents.sci_agent_system.SequentialAgent')
    @patch('backend.agents.sci_agent_system.ParallelAgent')
    @patch('backend.agents.sci_agent_system.ShortTermMemory')
    @patch('backend.agents.sci_agent_system.LongTermMemory')
    @patch('backend.agents.sci_agent_system.FunctionTool')
    def test_system_initialization(self, mock_ft, mock_ltm, mock_stm, mock_pa, mock_sa, mock_agent):
        """Test system initialization with VeADK mocked"""
        from backend.agents.sci_agent_system import UniversalSciAgentSystem
        
        mock_agent.return_value = MagicMock()
        mock_sa.return_value = MagicMock()
        mock_pa.return_value = MagicMock()
        mock_stm.return_value = MagicMock()
        mock_ltm.return_value = MagicMock()
        mock_ft.return_value = MagicMock()
        
        system = UniversalSciAgentSystem()
        
        assert system is not None
        assert hasattr(system, 'literature_agent')
        assert hasattr(system, 'hypothesis_agent')
        assert hasattr(system, 'experiment_agent')
        assert hasattr(system, 'writing_agent')
        assert hasattr(system, 'research_workflow')
    
    @patch('backend.agents.sci_agent_system.Agent')
    @patch('backend.agents.sci_agent_system.SequentialAgent')
    @patch('backend.agents.sci_agent_system.ParallelAgent')
    @patch('backend.agents.sci_agent_system.ShortTermMemory')
    @patch('backend.agents.sci_agent_system.LongTermMemory')
    @patch('backend.agents.sci_agent_system.FunctionTool')
    def test_system_has_required_methods(self, mock_ft, mock_ltm, mock_stm, mock_pa, mock_sa, mock_agent):
        """Test that system has required methods"""
        from backend.agents.sci_agent_system import UniversalSciAgentSystem
        
        mock_agent.return_value = MagicMock()
        mock_sa.return_value = MagicMock()
        mock_pa.return_value = MagicMock()
        mock_stm.return_value = MagicMock()
        mock_ltm.return_value = MagicMock()
        mock_ft.return_value = MagicMock()
        
        system = UniversalSciAgentSystem()
        
        assert hasattr(system, 'run_task')
        assert hasattr(system, 'literature_review')
        assert hasattr(system, 'generate_hypothesis')
        assert hasattr(system, 'design_experiment')
        assert hasattr(system, 'write_report')
        assert hasattr(system, 'full_research_pipeline')


class TestLiteratureAgent:
    """Test LiteratureAgent"""
    
    def test_literature_agent_import(self):
        """Test that LiteratureAgent can be imported"""
        from backend.agents.literature_agent import LiteratureAgent
        assert LiteratureAgent is not None


class TestHypothesisAgent:
    """Test HypothesisAgent"""
    
    def test_hypothesis_agent_import(self):
        """Test that HypothesisAgent can be imported"""
        from backend.agents.hypothesis_agent import HypothesisAgent
        assert HypothesisAgent is not None


class TestWritingAgent:
    """Test WritingAgent"""
    
    def test_writing_agent_import(self):
        """Test that WritingAgent can be imported"""
        from backend.agents.writing_agent import WritingAgent
        assert WritingAgent is not None


class TestResearchWorkflow:
    """Test ResearchWorkflow with VeADK Native"""
    
    def test_workflow_import(self):
        """Test that ResearchWorkflow can be imported"""
        from backend.workflows.research_workflow import ResearchWorkflow, WorkflowType
        assert ResearchWorkflow is not None
        assert WorkflowType is not None
    
    @patch('backend.workflows.research_workflow.Agent')
    @patch('backend.workflows.research_workflow.SequentialAgent')
    @patch('backend.workflows.research_workflow.ParallelAgent')
    @patch('backend.workflows.research_workflow.LoopAgent')
    @patch('backend.workflows.research_workflow.FunctionTool')
    def test_workflow_initialization(self, mock_ft, mock_loop, mock_pa, mock_sa, mock_agent):
        """Test workflow initialization"""
        from backend.workflows.research_workflow import ResearchWorkflow
        
        mock_agent.return_value = MagicMock()
        mock_sa.return_value = MagicMock()
        mock_pa.return_value = MagicMock()
        mock_loop.return_value = MagicMock()
        mock_ft.return_value = MagicMock()
        
        workflow = ResearchWorkflow()
        
        assert workflow is not None
        assert hasattr(workflow, 'literature_workflow')
        assert hasattr(workflow, 'full_research_workflow')
        assert hasattr(workflow, 'parallel_search_workflow')
