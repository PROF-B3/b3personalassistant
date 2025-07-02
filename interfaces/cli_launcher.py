"""
CLI Launcher for B3PersonalAssistant

Provides a rich command-line interface with ASCII art, color-coded agents,
typewriter effects, and interactive menus for all agent modes.

Features:
- ASCII art banner with color
- Typewriter effect for responses
- Loading indicators and status display
- Color-coded agent names (Alpha=blue, Beta=green, Gamma=yellow, Delta=red)
- Interactive menu system
- Real-time status updates

Example:
    >>> from B3PersonalAssistant.interfaces.cli_launcher import launch_cli
    >>> launch_cli(user_profile, config)
    # Launches the CLI interface
"""

import time
import sys
from typing import Dict, Any, Optional
from pathlib import Path

# Rich for beautiful CLI
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.columns import Columns

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.agents import AlphaAgent, BetaAgent, GammaAgent, DeltaAgent, EpsilonAgent, ZetaAgent, EtaAgent

# Initialize Rich console
console = Console()

# ASCII Art Banner
BANNER = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    ██████╗ ██████╗ ██████╗ ██████╗ ██████╗ ██████╗ ██████╗ ██████╗       ║
║    ╚═════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚═════╝       ║
║                                                                              ║
║    B3PersonalAssistant - Multi-Agent AI System                              ║
║    Powered by Alpha (Α), Beta (Β), Gamma (Γ), Delta (Δ)                    ║
║    Epsilon (Ε), Zeta (Ζ), Eta (Η)                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

def typewriter_print(text: str, delay: float = 0.02, color: str = "white"):
    """
    Print text with typewriter effect.
    
    Args:
        text: Text to print
        delay: Delay between characters
        color: Text color
    """
    for char in text:
        console.print(char, style=color, end="", highlight=False)
        time.sleep(delay)
    console.print()  # New line

def show_banner():
    """Display the ASCII art banner with colors."""
    console.print(BANNER, style="bold blue")

def show_agent_status(agents: Dict[str, Any]) -> None:
    """
    Display status of all agents in a table.
    
    Args:
        agents: Dictionary of agent instances
    """
    table = Table(title="🤖 Agent Status")
    table.add_column("Agent", style="bold")
    table.add_column("Status", style="green")
    table.add_column("Model", style="cyan")
    table.add_column("Load", style="yellow")
    
    agent_colors = {
        'alpha': 'blue',
        'beta': 'green', 
        'gamma': 'yellow',
        'delta': 'red',
        'epsilon': 'magenta',
        'zeta': 'cyan',
        'eta': 'white'
    }
    
    for name, agent in agents.items():
        color = agent_colors.get(name, 'white')
        table.add_row(
            f"[{color}]{name.title()}[/{color}]",
            "🟢 Ready",
            "Ollama",
            "0%"
        )
    
    console.print(table)

def show_menu() -> str:
    """
    Display main menu and get user choice.
    
    Returns:
        User's menu choice
    """
    menu_text = """
🎯 Main Menu - Choose Your Agent:

[bold blue]1.[/bold blue] Alpha (Α) - Chief Assistant & Coordinator
[bold green]2.[/bold green] Beta (Β) - Analyst & Researcher  
[bold yellow]3.[/bold yellow] Gamma (Γ) - Knowledge Manager & Zettelkasten
[bold red]4.[/bold red] Delta (Δ) - Task Coordinator & Workflow Manager
[bold magenta]5.[/bold magenta] Epsilon (Ε) - Creative Director & Media Specialist
[bold cyan]6.[/bold cyan] Zeta (Ζ) - Code Architect & Technical Specialist
[bold white]7.[/bold white] Eta (Η) - Evolution Engineer & System Improvement
[bold white]8.[/bold white] All Agents - Multi-Agent Collaboration
[bold cyan]9.[/bold cyan] System Status & Information
[bold magenta]10.[/bold magenta] Help & Examples
[bold white]0.[/bold white] Exit

"""
    console.print(Panel(menu_text, title="🤖 B3PersonalAssistant", border_style="blue"))
    
    choice = Prompt.ask("Choose an option", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
    return choice

def chat_with_agent(agent_name: str, agent_instance: Any, user_profile: Dict[str, Any]) -> None:
    """
    Interactive chat session with a specific agent.
    
    Args:
        agent_name: Name of the agent
        agent_instance: Agent instance
        user_profile: User profile dictionary
    """
    agent_colors = {
        'alpha': 'blue',
        'beta': 'green',
        'gamma': 'yellow', 
        'delta': 'red',
        'epsilon': 'magenta',
        'zeta': 'cyan',
        'eta': 'white'
    }
    
    color = agent_colors.get(agent_name, 'white')
    agent_symbol = {
        'alpha': 'Α', 'beta': 'Β', 'gamma': 'Γ', 'delta': 'Δ',
        'epsilon': 'Ε', 'zeta': 'Ζ', 'eta': 'Η'
    }[agent_name]
    
    console.print(f"\n[bold {color}]🤖 {agent_name.title()} ({agent_symbol}) - Interactive Chat[/bold {color}]")
    console.print(f"[dim]Type 'quit' to return to menu, 'help' for commands[/dim]\n")
    
    while True:
        try:
            # Get user input
            user_input = Prompt.ask(f"[{color}]{agent_name.title()}[/{color}]")
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            elif user_input.lower() == 'help':
                show_chat_help()
                continue
            elif not user_input.strip():
                continue
            
            # Show loading spinner
            with console.status(f"[{color}]{agent_name.title()}[/{color}] is thinking...", spinner="dots"):
                # Get agent response
                response = agent_instance.act(user_input, {"user_profile": user_profile})
            
            # Display response with typewriter effect
            console.print(f"\n[{color}]{agent_name.title()}:[/{color}] ", end="")
            typewriter_print(response, delay=0.01, color=color)
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Chat interrupted. Returning to menu...[/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")

def show_chat_help():
    """Display help for chat commands."""
    help_text = """
💬 Chat Commands:
• [bold]quit[/bold] - Return to main menu
• [bold]help[/bold] - Show this help
• [bold]status[/bold] - Show agent status
• [bold]clear[/bold] - Clear screen
"""
    console.print(Panel(help_text, title="📖 Chat Help", border_style="green"))

def multi_agent_chat(agents: Dict[str, Any], user_profile: Dict[str, Any]) -> None:
    """
    Multi-agent collaboration chat.
    
    Args:
        agents: Dictionary of agent instances
        user_profile: User profile dictionary
    """
    console.print("\n[bold cyan]🤖 Multi-Agent Collaboration Mode[/bold cyan]")
    console.print("[dim]All agents will collaborate on your requests[/dim]\n")
    
    while True:
        try:
            user_input = Prompt.ask("[cyan]Multi-Agent[/cyan]")
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            elif user_input.lower() == 'help':
                show_multi_agent_help()
                continue
            elif not user_input.strip():
                continue
            
            # Show progress for multi-agent processing
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Coordinating agents...", total=len(agents))
                
                responses = []
                for name, agent in agents.items():
                    progress.update(task, description=f"Processing with {name.title()}...")
                    response = agent.act(user_input, {"user_profile": user_profile})
                    responses.append(f"[bold]{name.title()}:[/bold] {response}")
                    progress.advance(task)
            
            # Display all responses
            console.print("\n[bold cyan]Multi-Agent Response:[/bold cyan]")
            for response in responses:
                console.print(response)
                console.print()
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Multi-agent chat interrupted. Returning to menu...[/yellow]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")

def show_multi_agent_help():
    """Display help for multi-agent mode."""
    help_text = """
🤖 Multi-Agent Commands:
• [bold]quit[/bold] - Return to main menu
• [bold]help[/bold] - Show this help
• [bold]agents[/bold] - List available agents
• [bold]status[/bold] - Show all agent status
"""
    console.print(Panel(help_text, title="📖 Multi-Agent Help", border_style="cyan"))

def show_system_status(user_profile: Dict[str, Any], config: Any) -> None:
    """
    Display system status and information.
    
    Args:
        user_profile: User profile dictionary
        config: Configuration object
    """
    # User Profile Info
    profile_table = Table(title="👤 User Profile")
    profile_table.add_column("Setting", style="bold")
    profile_table.add_column("Value", style="green")
    
    profile_table.add_row("Name", user_profile.get('name', 'Not set'))
    profile_table.add_row("Role", user_profile.get('role', 'Not set'))
    profile_table.add_row("Communication Style", user_profile.get('communication_style', 'Not set'))
    profile_table.add_row("Work Style", user_profile.get('work_style', 'Not set'))
    profile_table.add_row("Task Preferences", user_profile.get('task_preferences', 'Not set'))
    profile_table.add_row("Knowledge Preferences", user_profile.get('knowledge_preferences', 'Not set'))
    
    console.print(profile_table)
    console.print()
    
    # System Info
    system_table = Table(title="⚙️ System Information")
    system_table.add_column("Component", style="bold")
    system_table.add_column("Status", style="green")
    system_table.add_column("Version", style="cyan")
    
    system_table.add_row("B3PersonalAssistant", "🟢 Running", "1.0.0")
    system_table.add_row("Ollama Integration", "🟢 Active", "Latest")
    system_table.add_row("Database", "🟢 Connected", "SQLite")
    system_table.add_row("GUI Support", "🟢 Available", "Tkinter")
    
    console.print(system_table)

def show_help_and_examples() -> None:
    """Display help and example workflows."""
    help_text = """
📚 B3PersonalAssistant Help & Examples

🎯 Agent Specializations:
• [bold blue]Alpha (Α)[/bold blue] - Chief Assistant, coordinates other agents
• [bold green]Beta (Β)[/bold green] - Research and analysis specialist  
• [bold yellow]Gamma (Γ)[/bold yellow] - Knowledge management and Zettelkasten
• [bold red]Delta (Δ)[/bold red] - Task management and workflow optimization
• [bold magenta]Epsilon (Ε)[/bold magenta] - Creative Director, handles media and creative tasks
• [bold cyan]Zeta (Ζ)[/bold cyan] - Code Architect, generates code and builds capabilities
• [bold white]Eta (Η)[/bold white] - Evolution Engineer, improves system performance

💡 Example Workflows:
1. [bold]Research Project:[/bold] "Research quantum computing and create tasks"
2. [bold]Daily Planning:[/bold] "Help me plan my day and organize my tasks"
3. [bold]Knowledge Organization:[/bold] "Create notes about AI trends and link them"
4. [bold]Creative Project:[/bold] "Create a video montage with creative effects"
5. [bold]Code Development:[/bold] "Generate a Python function for data processing"
6. [bold]System Improvement:[/bold] "Analyze system performance and suggest optimizations"
7. [bold]Multi-Agent Analysis:[/bold] "Analyze my productivity patterns and suggest improvements"

🔧 Commands:
• Use 'quit' to exit any mode
• Use 'help' for context-specific help
• Use 'status' to check system status

📖 For more information, see the documentation in the tutorial/ directory.
"""
    console.print(Panel(help_text, title="📖 Help & Examples", border_style="magenta"))

def launch_cli(user_profile: Dict[str, Any], config: Any) -> None:
    """
    Launch the CLI interface.
    
    Args:
        user_profile: User profile dictionary
        config: Configuration object
    """
    try:
        # Clear screen and show banner
        console.clear()
        show_banner()
        
        # Welcome message
        user_name = user_profile.get('name', 'User')
        console.print(f"\n[bold green]Welcome, {user_name}![/bold green]")
        console.print("[dim]B3PersonalAssistant CLI is ready. Choose your agent below.[/dim]\n")
        
        # Initialize agents
        agents = {
            'alpha': AlphaAgent(user_profile=user_profile),
            'beta': BetaAgent(user_profile=user_profile),
            'gamma': GammaAgent(user_profile=user_profile),
            'delta': DeltaAgent(user_profile=user_profile),
            'epsilon': EpsilonAgent(user_profile=user_profile),
            'zeta': ZetaAgent(user_profile=user_profile),
            'eta': EtaAgent(user_profile=user_profile)
        }
        
        # Main menu loop
        while True:
            try:
                choice = show_menu()
                
                if choice == "0":
                    console.print("\n[bold green]👋 Thank you for using B3PersonalAssistant![/bold green]")
                    break
                elif choice == "1":
                    chat_with_agent('alpha', agents['alpha'], user_profile)
                elif choice == "2":
                    chat_with_agent('beta', agents['beta'], user_profile)
                elif choice == "3":
                    chat_with_agent('gamma', agents['gamma'], user_profile)
                elif choice == "4":
                    chat_with_agent('delta', agents['delta'], user_profile)
                elif choice == "5":
                    chat_with_agent('epsilon', agents['epsilon'], user_profile)
                elif choice == "6":
                    chat_with_agent('zeta', agents['zeta'], user_profile)
                elif choice == "7":
                    chat_with_agent('eta', agents['eta'], user_profile)
                elif choice == "8":
                    multi_agent_chat(agents, user_profile)
                elif choice == "9":
                    show_system_status(user_profile, config)
                    input("\nPress Enter to continue...")
                elif choice == "10":
                    show_help_and_examples()
                    input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Returning to menu...[/yellow]")
                continue
            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]")
                console.print("[yellow]Press Enter to continue...[/yellow]")
                input()
                
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]")
        console.print("[yellow]Please check your installation and try again.[/yellow]")
    finally:
        console.print("\n[dim]B3PersonalAssistant CLI shutdown complete.[/dim]")

if __name__ == "__main__":
    # Test launch
    test_profile = {
        'name': 'Test User',
        'communication_style': 'friendly',
        'work_style': 'flexible',
        'interests': ['AI', 'productivity'],
        'task_preferences': 'simple',
        'knowledge_preferences': 'zettelkasten'
    }
    
    class MockConfig:
        pass
    
    launch_cli(test_profile, MockConfig()) 