"""
Advanced Gradio UI with SQLite persistence and session management.
"""

import gradio as gr
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Optional

# Import existing core components
from src.models.model_manager import ModelManager
from src.core.conversation import ConversationManager
from src.storage import Database, SessionManager
from src.utils.logger import setup_logger


class PersistentGradioChat:
    """Gradio chat interface with persistent storage."""

    def __init__(self):
        """Initialize the persistent Gradio chat interface."""
        self.logger = setup_logger()
        self.model_manager = ModelManager()
        self.conversation = ConversationManager()
        self.db = Database()
        self.session_manager = SessionManager(self.db)
        self.current_session_id = None
        self.is_generating = False
        self.logger.info("Initializing Persistent Gradio Chat Interface")

        # Create a new session on startup
        self.current_session_id = self.session_manager.create_session()

    async def load_model_async(self, progress=gr.Progress()):
        """Load model asynchronously with progress updates."""
        try:
            progress(0, desc="Loading model...")

            def progress_callback(msg):
                self.logger.info(msg)
                progress(0.5, desc=msg)

            await asyncio.to_thread(
                self.model_manager.load_model, progress_callback=progress_callback
            )

            progress(1.0, desc="Model loaded successfully!")
            return "✅ Model loaded! Ready to chat."
        except Exception as e:
            self.logger.error(f"Model loading failed: {e}", exc_info=True)
            return f"❌ Error loading model: {str(e)}"

    def load_session(self, session_id: int) -> Tuple[List[Dict[str, str]], str]:
        """Load a session from database.

        Args:
            session_id: Session ID to load

        Returns:
            (chat_history, status_message)
        """
        try:
            messages = self.session_manager.get_messages(session_id)

            # Clear current conversation
            self.conversation.clear_history()

            # Rebuild conversation history in new Gradio format
            chat_history = []
            for msg in messages:
                self.conversation.messages.append(msg)
                chat_history.append({"role": msg["role"], "content": msg["content"]})

            self.current_session_id = session_id
            session = self.session_manager.get_session(session_id)

            # Check if session exists
            if session is None:
                self.logger.error(f"Session {session_id} not found in database")
                return [], f"Error: Session {session_id} not found"

            return chat_history, f"Loaded: {session['title']}"

        except Exception as e:
            self.logger.error(f"Failed to load session: {e}", exc_info=True)
            return [], f"Error loading session: {str(e)}"

    def create_new_session(self, title: Optional[str] = None) -> Tuple[List, str]:
        """Create a new conversation session.

        Args:
            title: Optional session title

        Returns:
            (empty_history, status_message)
        """
        self.conversation.clear_history()
        self.current_session_id = self.session_manager.create_session(title)

        return [], f"New session created: {title or 'Untitled'}"

    def get_session_list(self):
        """Get list of sessions for dropdown.

        Returns:
            Dictionary mapping display labels to session IDs
        """
        sessions = self.session_manager.list_sessions(limit=100)
        # Return as dict: {label: value} where value is the session ID
        return {f"{s['title']} ({s['message_count']} msgs)": s["id"] for s in sessions}

    def generate_response(
        self,
        message: str,
        history: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        top_p: float,
        save_to_db: bool = True,
    ):
        """Generate streaming response with optional persistence.

        Args:
            message: User input message
            history: Chat history (list of dicts with role/content)
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            top_p: Nucleus sampling
            save_to_db: Whether to save to database

        Yields:
            Updated history with streaming response
        """
        if not self.model_manager.is_loaded:
            yield history + [
                {"role": "assistant", "content": "Model not loaded yet. Please wait..."}
            ]
            return

        if not message.strip():
            return

        self.is_generating = True

        # Add user message to conversation
        self.conversation.add_user_message(message)

        # Save to database
        if save_to_db and self.current_session_id:
            self.session_manager.add_message(self.current_session_id, "user", message)

        # Add user message to history
        new_history = history + [{"role": "user", "content": message}]

        # Prepare messages for model
        messages = self.conversation.get_history()

        try:
            # Prepare inputs
            device = self.model_manager.device
            tokenizer = self.model_manager.tokenizer

            inputs = tokenizer.apply_chat_template(
                messages, return_tensors="pt", add_generation_prompt=True
            ).to(device)

            # Create attention mask (fixes warning)
            attention_mask = inputs.ne(tokenizer.pad_token_id).long().to(device)

            # Generation config
            gen_config = {
                "max_new_tokens": max_tokens,
                "do_sample": True,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": 50,
            }

            # Generate with streaming
            full_response = ""

            from transformers import TextIteratorStreamer
            import threading

            streamer = TextIteratorStreamer(
                self.model_manager.tokenizer, skip_prompt=True, skip_special_tokens=True
            )

            generation_kwargs = {
                "inputs": inputs,
                "attention_mask": attention_mask,
                "streamer": streamer,
                "pad_token_id": tokenizer.pad_token_id,
                **gen_config,
            }

            thread = threading.Thread(
                target=self.model_manager.model.generate, kwargs=generation_kwargs
            )
            thread.start()

            # Stream tokens
            for token in streamer:
                if not self.is_generating:
                    break
                full_response += token
                yield new_history + [{"role": "assistant", "content": full_response}]

            # Save complete response
            self.conversation.add_assistant_message(full_response)

            if save_to_db and self.current_session_id:
                self.session_manager.add_message(
                    self.current_session_id, "assistant", full_response
                )

            yield new_history + [{"role": "assistant", "content": full_response}]

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            yield new_history + [{"role": "assistant", "content": error_msg}]
        finally:
            self.is_generating = False

    def export_current_session(self, format_type: str):
        """Export current session to file.

        Args:
            format_type: 'json' or 'markdown'

        Returns:
            File path for download
        """
        if not self.current_session_id:
            return None

        export_dir = Path("exports")
        export_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format_type == "json":
            filepath = (
                export_dir / f"session_{self.current_session_id}_{timestamp}.json"
            )
            data = self.session_manager.export_session_json(self.current_session_id)
            if data is None:
                self.logger.error(
                    f"Failed to export session {self.current_session_id}: session not found"
                )
                return None
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:  # markdown
            filepath = export_dir / f"session_{self.current_session_id}_{timestamp}.md"
            markdown = self.session_manager.export_session_markdown(
                self.current_session_id
            )
            if markdown is None:
                self.logger.error(
                    f"Failed to export session {self.current_session_id}: session not found"
                )
                return None
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(markdown)

        return str(filepath)

    def get_stats(self):
        """Get system and database statistics."""
        db_stats = self.session_manager.get_stats()
        msg_count = self.conversation.get_message_count()
        device = self.model_manager.device
        loaded = "✅" if self.model_manager.is_loaded else "❌"

        current_session = (
            f"Session #{self.current_session_id}"
            if self.current_session_id
            else "No session"
        )

        return f"""
        **Model Status:** {loaded} Loaded on {device.upper()}
        **Current Session:** {current_session}
        **Messages in Memory:** {msg_count}
        
        **Database Stats:**
        - Total Sessions: {db_stats["total_sessions"]}
        - Total Messages: {db_stats["total_messages"]}
        - DB Path: `{db_stats["database_path"]}`
        """

    def create_interface(self):
        """Create and configure Gradio interface."""

        with gr.Blocks(title="AI Chatbot - Persistent") as demo:
            gr.Markdown(
                """
                # 🤖 AI Chatbot - Mistral 7B (Persistent)
                ### With SQLite conversation storage and session management
                """
            )

            with gr.Row():
                with gr.Column(scale=3):
                    # Session management
                    with gr.Row():
                        session_dropdown = gr.Dropdown(
                            label="📂 Sessions",
                            choices=[],
                            value=None,
                            interactive=True,
                            scale=3,
                        )
                        refresh_sessions_btn = gr.Button("🔄", scale=1, size="sm")
                        new_session_btn = gr.Button(
                            "➕ New", scale=1, variant="primary"
                        )

                    # Chat interface
                    chatbot = gr.Chatbot(
                        label="Chat",
                        height=550,
                    )

                    with gr.Row():
                        msg_input = gr.Textbox(
                            label="Message",
                            placeholder="Type your message here...",
                            scale=4,
                            lines=2,
                        )
                        send_btn = gr.Button("Send 📤", variant="primary", scale=1)

                    with gr.Row():
                        stop_btn = gr.Button("⏹ Stop", variant="stop")
                        clear_btn = gr.Button("🗑️ Clear Chat")
                        delete_session_btn = gr.Button(
                            "🗑️ Delete Session", variant="stop"
                        )

                with gr.Column(scale=1):
                    # Settings panel
                    gr.Markdown("### ⚙️ Generation Settings")

                    temperature = gr.Slider(
                        minimum=0.1,
                        maximum=2.0,
                        value=0.7,
                        step=0.1,
                        label="Temperature",
                    )

                    max_tokens = gr.Slider(
                        minimum=50, maximum=2048, value=512, step=50, label="Max Tokens"
                    )

                    top_p = gr.Slider(
                        minimum=0.1, maximum=1.0, value=0.9, step=0.05, label="Top P"
                    )

                    gr.Markdown("---")
                    gr.Markdown("### 📊 Status")

                    stats_display = gr.Markdown(self.get_stats())
                    refresh_stats_btn = gr.Button("🔄 Refresh", size="sm")

                    gr.Markdown("---")
                    gr.Markdown("### 💾 Export")

                    export_format = gr.Radio(
                        choices=["json", "markdown"], value="markdown", label="Format"
                    )

                    export_btn = gr.Button("📥 Export Session")
                    export_file = gr.File(label="Download", visible=False)

            status_msg = gr.Textbox(
                label="Status", value="Initializing...", interactive=False
            )

            # Load model and populate sessions on startup
            def on_load():
                """Initialize UI on page load."""
                sessions = self.get_session_list()
                # Return updated dropdown with choices
                return gr.update(choices=list(sessions.items()), value=None)

            demo.load(fn=self.load_model_async, outputs=status_msg)
            demo.load(fn=on_load, outputs=session_dropdown)

            # Event handlers
            def submit_message(message, history, temp, tokens, topp):
                if not message.strip():
                    return
                for updated_history in self.generate_response(
                    message, history, temp, tokens, topp, save_to_db=True
                ):
                    yield updated_history, ""

            send_btn.click(
                fn=submit_message,
                inputs=[msg_input, chatbot, temperature, max_tokens, top_p],
                outputs=[chatbot, msg_input],
            )

            msg_input.submit(
                fn=submit_message,
                inputs=[msg_input, chatbot, temperature, max_tokens, top_p],
                outputs=[chatbot, msg_input],
            )

            # Stop generation
            def stop_generation():
                self.is_generating = False
                return "Stopped"

            stop_btn.click(
                fn=stop_generation,
                outputs=status_msg,
            )

            # Session management
            def refresh_session_list():
                """Refresh the session dropdown list."""
                sessions = self.get_session_list()
                # Return updated dropdown with choices as list of (label, value) tuples
                return gr.update(choices=list(sessions.items()), value=None)

            refresh_sessions_btn.click(
                fn=refresh_session_list, outputs=session_dropdown
            )

            def load_selected_session(session_id):
                """Load a session when selected from dropdown."""
                if session_id is None:
                    return [], "No session selected"

                try:
                    # Ensure session_id is an integer
                    session_id = int(session_id)
                    return self.load_session(session_id)
                except (ValueError, TypeError) as e:
                    self.logger.error(f"Invalid session_id: {session_id}, error: {e}")
                    return [], "Error: Invalid session ID"

            session_dropdown.change(
                fn=load_selected_session,
                inputs=session_dropdown,
                outputs=[chatbot, status_msg],
            )

            new_session_btn.click(
                fn=self.create_new_session, outputs=[chatbot, status_msg]
            ).then(fn=refresh_session_list, outputs=session_dropdown)

            # Clear and delete
            def clear_chat():
                self.conversation.clear_history()
                return [], "Chat cleared (session preserved)"

            clear_btn.click(fn=clear_chat, outputs=[chatbot, status_msg])

            def delete_current_session():
                if self.current_session_id:
                    self.session_manager.delete_session(self.current_session_id)
                    return self.create_new_session()
                return [], "No session to delete"

            delete_session_btn.click(
                fn=delete_current_session, outputs=[chatbot, status_msg]
            ).then(fn=refresh_session_list, outputs=session_dropdown)

            # Stats refresh
            refresh_stats_btn.click(fn=self.get_stats, outputs=stats_display)

            # Export
            def export_with_visibility(format_type):
                filepath = self.export_current_session(format_type)
                if filepath:
                    return gr.File(value=filepath, visible=True), "Export successful"
                return gr.File(visible=False), "Export failed: Session not found"

            export_btn.click(
                fn=export_with_visibility,
                inputs=export_format,
                outputs=[export_file, status_msg],
            )

        return demo


def main():
    """Launch the persistent Gradio interface."""
    chat = PersistentGradioChat()
    demo = chat.create_interface()

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        inbrowser=True,
    )


if __name__ == "__main__":
    main()
