"""
Conversation memory and management.
"""

class ConversationManager:
    """Manages conversation history and memory."""
    
    def __init__(self):
        """Initialize conversation manager."""
        self.messages = []
        self.is_interrupted = False
        self.partial_response = ""
    
    def add_user_message(self, content):
        """Add a user message to history.
        
        Args:
            content: Message content
        """
        self.messages.append({
            "role": "user",
            "content": content
        })
    
    def add_assistant_message(self, content):
        """Add an assistant message to history.
        
        Args:
            content: Message content
        """
        self.messages.append({
            "role": "assistant",
            "content": content
        })
    
    def get_history(self):
        """Get full conversation history.
        
        Returns:
            List of message dictionaries
        """
        return self.messages
    
    def clear_history(self):
        """Clear all conversation history."""
        self.messages = []
        self.is_interrupted = False
        self.partial_response = ""
    
    def mark_interrupted(self, partial_content):
        """Mark conversation as interrupted.
        
        Args:
            partial_content: Partially generated content
        """
        self.is_interrupted = True
        self.partial_response = partial_content
    
    def continue_conversation(self):
        """Add continuation prompt to conversation."""
        if self.is_interrupted:
            self.add_user_message("Please continue from where you left off.")
            self.is_interrupted = False
    
    def get_message_count(self):
        """Get total message count.
        
        Returns:
            Integer count of messages
        """
        return len(self.messages)
