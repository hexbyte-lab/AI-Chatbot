"""
Modern Gradio-based web UI for AI Chatbot.
Replaces tkinter with async streaming web interface.
"""

import gradio as gr
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional, Dict

# Import existing core components
from src.models.model_manager import ModelManager
from src.core.conversation import ConversationManager
from src.utils.logger import setup_logger


class GradioChat:
    """Gradio-based chat interface."""

    def __init__(self):
        """Initialize the Gradio chat interface."""
        self.logger = setup_logger()
        self.model_manager = ModelManager()
        self.conversation = ConversationManager()
        self.is_generating = False
        self.logger.info("Initializing Gradio Chat Interface")

    async def load_model_async(self, progress=gr.Progress()):
        """Load model asynchronously with progress updates."""
        try:
            progress(0, desc="Loading model...")

            def progress_callback(msg):
                self.logger.info(msg)
                progress(0.5, desc=msg)

            # Load model in thread to avoid blocking
            await asyncio.to_thread(
                self.model_manager.load_model, progress_callback=progress_callback
            )

            progress(1.0, desc="Model loaded successfully!")
            return "✅ Model loaded! Ready to chat."
        except Exception as e:
            self.logger.error(f"Model loading failed: {e}", exc_info=True)
            return f"❌ Error loading model: {str(e)}"

    def generate_response(
        self,
        message: str,
        history: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        top_p: float,
    ):
        """Generate streaming response.

        Args:
            message: User input message
            history: Chat history (list of dicts with role/content)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter

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

            # Generation config with dynamic parameters
            gen_config = {
                "max_new_tokens": max_tokens,
                "do_sample": True,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": 50,
            }

            # Generate with streaming
            full_response = ""

            # Use TextIteratorStreamer for streaming
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

            # Start generation in background thread
            thread = threading.Thread(
                target=self.model_manager.model.generate, kwargs=generation_kwargs
            )
            thread.start()

            # Stream tokens
            for token in streamer:
                if not self.is_generating:
                    break
                full_response += token
                # Yield incremental updates
                yield new_history + [{"role": "assistant", "content": full_response}]

            # Save complete response
            self.conversation.add_assistant_message(full_response)

            # Final yield with complete response
            yield new_history + [{"role": "assistant", "content": full_response}]

        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            yield new_history + [{"role": "assistant", "content": error_msg}]
        finally:
            self.is_generating = False

    def stop_generation(self):
        """Stop current generation."""
        self.is_generating = False
        return "⏹ Generation stopped"

    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation.clear_history()
        self.logger.info("Conversation cleared")
        return [], "Conversation cleared"

    def export_conversation(self, format_type: str):
        """Export conversation to file.

        Args:
            format_type: 'json' or 'markdown'

        Returns:
            File path for download or None if no conversation to export
        """
        if self.conversation.get_message_count() == 0:
            self.logger.warning("No messages to export")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = Path("exports")
        export_dir.mkdir(exist_ok=True)

        if format_type == "json":
            filepath = export_dir / f"conversation_{timestamp}.json"
            data = {
                "timestamp": timestamp,
                "message_count": self.conversation.get_message_count(),
                "messages": self.conversation.get_history(),
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:  # markdown
            filepath = export_dir / f"conversation_{timestamp}.md"
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# Conversation Export\n\n")
                f.write(f"**Date:** {timestamp}\n\n")
                f.write(f"**Messages:** {self.conversation.get_message_count()}\n\n")
                f.write("---\n\n")

                for msg in self.conversation.get_history():
                    role = msg["role"].title()
                    content = msg["content"]
                    f.write(f"### {role}\n\n{content}\n\n")

        return str(filepath)

    def get_stats(self):
        """Get conversation statistics."""
        msg_count = self.conversation.get_message_count()
        device = self.model_manager.device
        loaded = "✅" if self.model_manager.is_loaded else "❌"

        return f"""
        **Status:** {loaded} Model Loaded
        **Device:** {device.upper()}
        **Messages:** {msg_count}
        """

    def create_interface(self):
        """Create and configure Gradio interface."""

        with gr.Blocks(title="AI Chatbot - Mistral 7B") as demo:
            gr.Markdown(
                """
                # 🤖 AI Chatbot - Mistral 7B
                ### Powered by HuggingFace Transformers with streaming responses
                """
            )

            with gr.Row():
                with gr.Column(scale=3):
                    # Main chat interface
                    chatbot = gr.Chatbot(
                        label="Chat",
                        height=600,
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
                        clear_btn = gr.Button("🗑️ Clear", variant="secondary")
                        retry_btn = gr.Button("🔄 Retry")

                with gr.Column(scale=1):
                    # Settings panel
                    gr.Markdown("### ⚙️ Settings")

                    temperature = gr.Slider(
                        minimum=0.1,
                        maximum=2.0,
                        value=0.7,
                        step=0.1,
                        label="Temperature",
                        info="Higher = more creative",
                    )

                    max_tokens = gr.Slider(
                        minimum=50,
                        maximum=2048,
                        value=512,
                        step=50,
                        label="Max Tokens",
                        info="Response length",
                    )

                    top_p = gr.Slider(
                        minimum=0.1,
                        maximum=1.0,
                        value=0.9,
                        step=0.05,
                        label="Top P",
                        info="Nucleus sampling",
                    )

                    gr.Markdown("---")
                    gr.Markdown("### 📊 Status")

                    stats_display = gr.Markdown(self.get_stats())

                    refresh_stats = gr.Button("🔄 Refresh Stats", size="sm")

                    gr.Markdown("---")
                    gr.Markdown("### 💾 Export")

                    export_format = gr.Radio(
                        choices=["json", "markdown"], value="markdown", label="Format"
                    )

                    export_btn = gr.Button("📥 Export Conversation")
                    export_file = gr.File(label="Download", visible=False)

            # Status message at bottom
            status_msg = gr.Textbox(
                label="Status", value="Initializing...", interactive=False
            )

            # Load model on startup
            demo.load(fn=self.load_model_async, outputs=status_msg)

            # Event handlers
            def submit_message(message, history, temp, tokens, topp):
                if not message.strip():
                    return
                for updated_history in self.generate_response(
                    message, history, temp, tokens, topp
                ):
                    yield updated_history, ""

            # Send button / Enter key
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

            # Stop button
            stop_btn.click(fn=self.stop_generation, outputs=status_msg)

            # Clear button
            def clear_with_update():
                result = self.clear_conversation()
                return result[0], result[1], self.get_stats()

            clear_btn.click(
                fn=clear_with_update, outputs=[chatbot, status_msg, stats_display]
            )

            # Refresh stats
            refresh_stats.click(fn=self.get_stats, outputs=stats_display)

            # Export functionality
            def export_with_visibility(format_type):
                filepath = self.export_conversation(format_type)
                if filepath:
                    return gr.File(value=filepath, visible=True), "Export successful"
                return gr.File(visible=False), "Export failed: No messages to export"

            export_btn.click(
                fn=export_with_visibility,
                inputs=export_format,
                outputs=[export_file, status_msg],
            )

        return demo


def main():
    """Launch the Gradio interface."""
    chat = GradioChat()
    demo = chat.create_interface()

    # Launch with options
    demo.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,
        share=False,  # Set to True for public URL
        show_error=True,
        inbrowser=True,
    )


if __name__ == "__main__":
    main()
