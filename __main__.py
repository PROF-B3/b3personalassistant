"""
Main entry point for B3PersonalAssistant

This module provides the main entry point when running the package directly.
"""

import sys
import argparse
import logging
from pathlib import Path

from core.config import ConfigManager
from .interfaces.gui_launcher import launch_gui
from .interfaces.cli_launcher import CLILauncher


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('b3personalassistant.log')
        ]
    )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="B3PersonalAssistant - Multi-Agent AI Personal Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m B3PersonalAssistant                    # Start GUI
  python -m B3PersonalAssistant --cli             # Start CLI
  python -m B3PersonalAssistant --cli chat        # Start CLI chat
  python -m B3PersonalAssistant --config path     # Use custom config
        """
    )
    
    parser.add_argument(
        '--cli', 
        action='store_true',
        help='Start command-line interface instead of GUI'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    # Parse arguments
    args, remaining_args = parser.parse_known_args()
    
    # Setup logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        setup_logging()
    
    logger = logging.getLogger(__name__)
    logger.info("Starting B3PersonalAssistant...")
    
    try:
        # Load configuration
        if args.config:
            config_path = Path(args.config)
            if not config_path.exists():
                logger.error(f"Configuration file not found: {config_path}")
                sys.exit(1)
            config_manager = ConfigManager(str(config_path))
            config = config_manager.config
        else:
            config_manager = ConfigManager()
            config = config_manager.config
        
        logger.info("Configuration loaded successfully")
        
        # Start appropriate interface
        if args.cli:
            # Pass remaining arguments to CLI
            sys.argv = [sys.argv[0]] + remaining_args
            cli = CLILauncher(config)
            cli.run()
        else:
            # Start GUI
            gui = launch_gui(config)
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting B3PersonalAssistant: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 