"""
Reusable UI components.
"""
import tkinter as tk
from tkinter import scrolledtext

class StatusBar:
    """Status bar component."""
    
    def __init__(self, parent):
        self.label = tk.Label(
            parent,
            text="",
            font=("Arial", 10),
            bg='#1e1e1e',
            fg='#ffaa00'
        )
        self.label.pack()
    
    def update(self, message):
        """Update status message."""
        self.label.config(text=message)

class ChatDisplay:
    """Chat message display component."""
    
    def __init__(self, parent):
        self.text_widget = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            width=90,
            height=25,
            font=("Arial", 11),
            bg='#2d2d2d',
            fg='#ffffff',
            state='disabled'
        )
        self.text_widget.pack(padx=10, pady=10)
        
        # Configure tags
        self.text_widget.tag_config("user", foreground="#00ff00", font=("Arial", 11, "bold"))
        self.text_widget.tag_config("bot", foreground="#00d9ff", font=("Arial", 11, "bold"))
        self.text_widget.tag_config("system", foreground="#ffaa00", font=("Arial", 10, "italic"))
    
    def add_user_message(self, message):
        """Add user message to display."""
        self._add_message("You", message, "user")
    
    def add_system_message(self, message):
        """Add system message to display."""
        self._add_message("System", message, "system")
    
    def start_bot_message(self):
        """Start bot message (for streaming)."""
        self.text_widget.config(state='normal')
        self.text_widget.insert(tk.END, "Bot: ", "bot")
        self.text_widget.see(tk.END)
    
    def add_token(self, token):
        """Add streaming token to display."""
        self.text_widget.insert(tk.END, token)
        self.text_widget.see(tk.END)
    
    def finish_bot_message(self):
        """Finish bot message."""
        self.text_widget.insert(tk.END, "\n\n")
        self.text_widget.config(state='disabled')
    
    def mark_interrupted(self):
        """Mark message as interrupted."""
        self.text_widget.insert(tk.END, " [INTERRUPTED]", "system")
        self.text_widget.insert(tk.END, "\n\n")
        self.text_widget.config(state='disabled')
    
    def clear(self):
        """Clear all messages."""
        self.text_widget.config(state='normal')
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.config(state='disabled')
    
    def _add_message(self, sender, message, tag):
        """Internal method to add message."""
        self.text_widget.config(state='normal')
        self.text_widget.insert(tk.END, f"{sender}: ", tag)
        self.text_widget.insert(tk.END, f"{message}\n\n")
        self.text_widget.see(tk.END)
        self.text_widget.config(state='disabled')

class InputArea:
    """Input area with buttons component."""
    
    def __init__(self, parent, on_send, on_stop, on_continue, on_clear):
        self.on_send = on_send
        self.on_stop = on_stop
        self.on_continue = on_continue
        self.on_clear = on_clear
        
        # Create frame
        self.frame = tk.Frame(parent, bg='#1e1e1e')
        self.frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Input box
        self.input_box = tk.Entry(
            self.frame,
            font=("Arial", 12),
            bg='#2d2d2d',
            fg='#ffffff',
            insertbackground='white'
        )
        self.input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_box.bind("<Return>", lambda e: self._handle_send())
        
        # Buttons
        self.send_button = self._create_button("Send", "#00d9ff", "#000000", self._handle_send)
        self.stop_button = self._create_button("⏹ Stop", "#ff5555", "#ffffff", on_stop)
        self.continue_button = self._create_button("▶ Continue", "#00ff00", "#000000", on_continue)
        
        clear_button = tk.Button(
            self.frame,
            text="Clear Memory",
            command=on_clear,
            font=("Arial", 10),
            bg='#ff5555',
            fg='#ffffff',
            width=12
        )
        clear_button.pack(side=tk.RIGHT, padx=5)
        
        # Show send button by default
        self.show_send_button()
    
    def _create_button(self, text, bg, fg, command):
        """Create a button."""
        return tk.Button(
            self.frame,
            text=text,
            command=command,
            font=("Arial", 12, "bold"),
            bg=bg,
            fg=fg,
            width=10
        )
    
    def _handle_send(self):
        """Handle send action."""
        message = self.input_box.get().strip()
        if message:
            self.input_box.delete(0, tk.END)
            self.on_send(message)
    
    def show_send_button(self):
        """Show send button, hide others."""
        self.stop_button.pack_forget()
        self.continue_button.pack_forget()
        self.send_button.pack(side=tk.RIGHT)
    
    def show_stop_button(self):
        """Show stop button, hide others."""
        self.send_button.pack_forget()
        self.continue_button.pack_forget()
        self.stop_button.pack(side=tk.RIGHT)
    
    def show_continue_button(self):
        """Show continue button, hide others."""
        self.send_button.pack_forget()
        self.stop_button.pack_forget()
        self.continue_button.pack(side=tk.RIGHT)
    
    def enable_send(self):
        """Enable send button."""
        self.send_button.config(state='normal')
    
    def disable_send(self):
        """Disable send button."""
        self.send_button.config(state='disabled')
