"""
Tests for core B3PersonalAssistant modules.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from core.orchestrator import Orchestrator
from core.agents import AlphaAgent, BetaAgent, GammaAgent, DeltaAgent, EpsilonAgent, ZetaAgent, EtaAgent
from core.config import ConfigManager, SystemConfig


class TestOrchestrator:
    """Test the Orchestrator class."""
    
    def test_orchestrator_initialization(self, mock_user_profile, mock_resource_monitor):
        """Test orchestrator initialization."""
        with patch('core.orchestrator.ResourceMonitor', return_value=mock_resource_monitor):
            orchestrator = Orchestrator(mock_user_profile)
            
        assert orchestrator.user_profile == mock_user_profile
        assert len(orchestrator.agents) == 7
        assert 'alpha' in orchestrator.agents
        assert 'beta' in orchestrator.agents
        assert 'gamma' in orchestrator.agents
        assert 'delta' in orchestrator.agents
        assert 'epsilon' in orchestrator.agents
        assert 'zeta' in orchestrator.agents
        assert 'eta' in orchestrator.agents
    
    def test_process_request_simple(self, mock_orchestrator):
        """Test simple request processing."""
        with patch.object(mock_orchestrator.agents['alpha'], 'act') as mock_act:
            mock_act.return_value = "Hello! How can I help you?"
            
            result = mock_orchestrator.process_request("Hello")
            
            assert "Hello! How can I help you?" in result
            mock_act.assert_called_once()
    
    def test_process_request_research(self, mock_orchestrator):
        """Test research request routing to Beta."""
        with patch.object(mock_orchestrator.agents['beta'], 'act') as mock_act:
            mock_act.return_value = "Research completed on AI trends."
            
            result = mock_orchestrator.process_request("Research AI trends")
            
            assert "Research completed" in result
            mock_act.assert_called_once()
    
    def test_process_request_task_management(self, mock_orchestrator):
        """Test task management request routing to Delta."""
        with patch.object(mock_orchestrator.agents['delta'], 'act') as mock_act:
            mock_act.return_value = "Task created and scheduled."
            
            result = mock_orchestrator.process_request("Create a task")
            
            assert "Task created" in result
            mock_act.assert_called_once()
    
    def test_agent_communication(self, mock_orchestrator):
        """Test inter-agent communication."""
        with patch.object(mock_orchestrator.agents['beta'], 'communicate') as mock_comm:
            mock_comm.return_value = "Research data shared."
            
            result = mock_orchestrator.agent_communicate('alpha', 'beta', 'Share research data')
            
            assert result == "Research data shared."
            mock_comm.assert_called_once_with('Share research data', None)
    
    def test_get_agent_status(self, mock_orchestrator):
        """Test agent status retrieval."""
        status = mock_orchestrator.get_agent_status()
        
        assert 'agents' in status
        assert 'system_health' in status
        assert 'resources' in status
        assert len(status['agents']) == 7


class TestAgents:
    """Test individual agent classes."""
    
    def test_alpha_agent(self, mock_user_profile, mock_resource_monitor):
        """Test Alpha agent functionality."""
        with patch('core.agents.ResourceMonitor', return_value=mock_resource_monitor):
            agent = AlphaAgent(None, mock_user_profile, mock_resource_monitor)
            
        assert agent.name == "Alpha"
        assert agent.user_profile == mock_user_profile
    
    def test_beta_agent(self, mock_user_profile, mock_resource_monitor):
        """Test Beta agent functionality."""
        with patch('core.agents.ResourceMonitor', return_value=mock_resource_monitor):
            agent = BetaAgent(None, mock_user_profile, mock_resource_monitor)
            
        assert agent.name == "Beta"
        assert agent.user_profile == mock_user_profile
    
    def test_gamma_agent(self, mock_user_profile, mock_resource_monitor):
        """Test Gamma agent functionality."""
        with patch('core.agents.ResourceMonitor', return_value=mock_resource_monitor):
            agent = GammaAgent(None, mock_user_profile, mock_resource_monitor)
            
        assert agent.name == "Gamma"
        assert agent.user_profile == mock_user_profile
    
    def test_delta_agent(self, mock_user_profile, mock_resource_monitor):
        """Test Delta agent functionality."""
        with patch('core.agents.ResourceMonitor', return_value=mock_resource_monitor):
            agent = DeltaAgent(None, mock_user_profile, mock_resource_monitor)
            
        assert agent.name == "Delta"
        assert agent.user_profile == mock_user_profile
    
    def test_epsilon_agent(self, mock_user_profile, mock_resource_monitor):
        """Test Epsilon agent functionality."""
        with patch('core.agents.ResourceMonitor', return_value=mock_resource_monitor):
            agent = EpsilonAgent(None, mock_user_profile, mock_resource_monitor)
            
        assert agent.name == "Epsilon"
        assert agent.user_profile == mock_user_profile
    
    def test_zeta_agent(self, mock_user_profile, mock_resource_monitor):
        """Test Zeta agent functionality."""
        with patch('core.agents.ResourceMonitor', return_value=mock_resource_monitor):
            agent = ZetaAgent(None, mock_user_profile, mock_resource_monitor)
            
        assert agent.name == "Zeta"
        assert agent.user_profile == mock_user_profile
    
    def test_eta_agent(self, mock_user_profile, mock_resource_monitor):
        """Test Eta agent functionality."""
        with patch('core.agents.ResourceMonitor', return_value=mock_resource_monitor):
            agent = EtaAgent(None, mock_user_profile, mock_resource_monitor)
            
        assert agent.name == "Eta"
        assert agent.user_profile == mock_user_profile
    
    def test_agent_adapt_to_user(self, mock_user_profile, mock_resource_monitor):
        """Test agent adaptation to user preferences."""
        with patch('core.agents.ResourceMonitor', return_value=mock_resource_monitor):
            agent = AlphaAgent(None, mock_user_profile, mock_resource_monitor)
            
        # Test friendly communication style
        result = agent.adapt_to_user("Hello there!")
        assert "Hello there!" in result
        
        # Test with emojis for friendly style
        if mock_user_profile['communication_style'] == 'friendly':
            assert any(char in result for char in ['😊', '👋', '✨'])


class TestConfig:
    """Test configuration management."""
    
    def test_config_manager_initialization(self, temp_dir):
        """Test ConfigManager initialization."""
        config_file = temp_dir / "test_config.json"
        config_manager = ConfigManager(str(config_file))
        
        assert isinstance(config_manager.config, SystemConfig)
        assert config_manager.config_file == config_file
    
    def test_load_default_config(self, temp_dir):
        """Test loading default configuration."""
        config_file = temp_dir / "test_config.json"
        config_manager = ConfigManager(str(config_file))
        
        # Should load defaults when no config file exists
        assert config_manager.config.debug_mode is False
        assert config_manager.config.log_level == "INFO"
        assert len(config_manager.config.ai_models) > 0
    
    def test_save_and_load_config(self, temp_dir):
        """Test saving and loading configuration."""
        config_file = temp_dir / "test_config.json"
        config_manager = ConfigManager(str(config_file))
        
        # Modify config
        config_manager.config.debug_mode = True
        config_manager.config.log_level = "DEBUG"
        
        # Save config
        config_manager.save_config()
        
        # Create new instance and load
        new_config_manager = ConfigManager(str(config_file))
        assert new_config_manager.config.debug_mode is True
        assert new_config_manager.config.log_level == "DEBUG"
    
    def test_get_agent_config(self, temp_dir):
        """Test getting agent configuration."""
        config_file = temp_dir / "test_config.json"
        config_manager = ConfigManager(str(config_file))
        
        alpha_config = config_manager.get_agent_config("Alpha")
        assert alpha_config is not None
        assert alpha_config.name == "Alpha"
        assert alpha_config.role == "Chief Assistant"
    
    def test_get_model_config(self, temp_dir):
        """Test getting model configuration."""
        config_file = temp_dir / "test_config.json"
        config_manager = ConfigManager(str(config_file))
        
        model_config = config_manager.get_model_config("default")
        assert model_config is not None
        assert model_config.model_type.value == "ollama"
        assert model_config.model_name == "llama2"


class TestErrorHandling:
    """Test error handling in core modules."""
    
    def test_orchestrator_error_handling(self, mock_user_profile, mock_resource_monitor):
        """Test orchestrator error handling."""
        with patch('core.orchestrator.ResourceMonitor', return_value=mock_resource_monitor):
            orchestrator = Orchestrator(mock_user_profile)
        
        # Test with agent that raises exception
        with patch.object(orchestrator.agents['alpha'], 'act', side_effect=Exception("Test error")):
            result = orchestrator.process_request("This will cause an error")
            
            assert "Error processing with alpha" in result
            assert "Test error" in result
    
    def test_agent_error_handling(self, mock_user_profile, mock_resource_monitor):
        """Test agent error handling."""
        with patch('core.agents.ResourceMonitor', return_value=mock_resource_monitor):
            agent = AlphaAgent(None, mock_user_profile, mock_resource_monitor)
        
        # Test error handling method
        error = Exception("Test error")
        result = agent.handle_error(error, {"context": "test"})
        
        assert "error" in result.lower()
        assert "Test error" in result
    
    def test_fallback_response(self, mock_user_profile, mock_resource_monitor):
        """Test agent fallback responses."""
        with patch('core.agents.ResourceMonitor', return_value=mock_resource_monitor):
            agent = AlphaAgent(None, mock_user_profile, mock_resource_monitor)
        
        result = agent.fallback_response("Test prompt")
        
        assert len(result) > 0
        assert "Alpha" in result or "assist" in result.lower() 