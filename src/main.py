"""
Main entry point for the AI Chatbot application.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from ui.chat_window import ChatbotGUI
from utils.logger import setup_logger

def main():
    """Initialize and run the chatbot application."""
    # Setup logging
    logger = setup_logger()
    logger.info("Starting AI Chatbot application")
    
    try:
        # Create and run GUI
        app = ChatbotGUI()
        app.run()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
