"""
Main chat window GUI.
"""
import tkinter as tk
from tkinter import scrolledtext
import threading

from models.model_manager import ModelManager
from core.conversation import ConversationManager
from core.generator import ResponseGenerator
from ui.components import StatusBar, ChatDisplay, InputArea

class ChatbotGUI:
    """Main chatbot GUI application."""
    
    def __init__(self):
        """Initialize the GUI application."""
        # Initialize components
        self.model_manager = ModelManager()
        self.conversation = ConversationManager()
        self.generator = ResponseGenerator(self.model_manager)
        
        # GUI setup
        self.window = tk.Tk()
        self._setup_window()
        self._create_widgets()
        
        # Load model in background
        threading.Thread(target=self._load_model_async, daemon=True).start()
    
    def _setup_window(self):
        """Setup main window configuration."""
        ui_config = self.model_manager.get_ui_config()
        self.window.title(ui_config['title'])
        self.window.geometry(f"{ui_config['width']}x{ui_config['height']}")
        self.window.configure(bg=ui_config['theme']['bg_color'])
    
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Title
        title = tk.Label(
            self.window,
            text="🤖 AI Chatbot",
            font=("Arial", 20, "bold"),
            bg='#1e1e1e',
            fg='#00d9ff'
        )
        title.pack(pady=10)
        
        # Status bar
        self.status_bar = StatusBar(self.window)
        self.status_bar.update("⏳ Loading model...")
        
        # Chat display
        self.chat_display = ChatDisplay(self.window)
        
        # Input area with buttons
        self.input_area = InputArea(
            self.window,
            on_send=self._handle_send,
            on_stop=self._handle_stop,
            on_continue=self._handle_continue,
            on_clear=self._handle_clear
        )
        self.input_area.disable_send()
    
    def _load_model_async(self):
        """Load model asynchronously."""
        try:
            self.model_manager.load_model(
                progress_callback=self.status_bar.update
            )
            self.status_bar.update("✅ Ready! Start chatting...")
            self.input_area.enable_send()
            self.chat_display.add_system_message(
                "Bot is ready! I remember our entire conversation."
            )
        except Exception as e:
            self.status_bar.update(f"❌ Error: {str(e)}")
    
    def _handle_send(self, message):
        """Handle send button click."""
        if not message:
            return
        
        # Display user message
        self.chat_display.add_user_message(message)
        
        # Add to conversation
        self.conversation.add_user_message(message)
        
        # Switch to stop button
        self.input_area.show_stop_button()
        self.status_bar.update("🤔 Thinking...")
        
        # Generate response
        threading.Thread(
            target=self._generate_response,
            daemon=True
        ).start()
    
    def _handle_stop(self):
        """Handle stop button click."""
        self.generator.stop()
        self.status_bar.update("⏸ Generation stopped")
        self.input_area.show_continue_button()
        self.chat_display.mark_interrupted()
    
    def _handle_continue(self):
        """Handle continue button click."""
        self.conversation.continue_conversation()
        self.input_area.show_stop_button()
        self.status_bar.update("▶ Continuing...")
        
        threading.Thread(
            target=self._generate_response,
            daemon=True
        ).start()
    
    def _handle_clear(self):
        """Handle clear memory button click."""
        self.conversation.clear_history()
        self.chat_display.clear()
        self.chat_display.add_system_message("Memory cleared! Starting fresh.")
        self.status_bar.update("✅ Ready! (Memory cleared)")
        self.input_area.show_send_button()
    
    def _generate_response(self):
        """Generate AI response with streaming."""
        self.chat_display.start_bot_message()
        
        def on_token(token):
            self.chat_display.add_token(token)
        
        def on_complete(response, was_stopped):
            self.chat_display.finish_bot_message()
            
            if not was_stopped:
                self.conversation.add_assistant_message(response)
                self.input_area.show_send_button()
                status = f"✅ Ready! (Memory: {self.conversation.get_message_count()} messages)"
            else:
                self.conversation.mark_interrupted(response)
                self.input_area.show_continue_button()
                status = f"⏸ Interrupted (Memory: {self.conversation.get_message_count()} messages)"
            
            self.status_bar.update(status)
        
        # Generate with streaming
        self.generator.generate_streaming(
            self.conversation.get_history(),
            on_token,
            on_complete
        )
    
    def run(self):
        """Start the GUI main loop."""
        self.window.mainloop()
