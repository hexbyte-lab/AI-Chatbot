"""
Text generation with streaming support.
"""

from transformers import TextIteratorStreamer
import threading


class ResponseGenerator:
    """Handles text generation with streaming."""

    def __init__(self, model_manager):
        """Initialize generator.

        Args:
            model_manager: ModelManager instance
        """
        self.model_manager = model_manager
        self.stop_flag = False

    def generate_streaming(self, messages, token_callback, complete_callback):
        """Generate response with streaming tokens.

        Args:
            messages: Conversation history
            token_callback: Function called for each token
            complete_callback: Function called when complete
        """
        self.stop_flag = False

        try:
            # Prepare inputs
            device = self.model_manager.device
            inputs = self.model_manager.tokenizer.apply_chat_template(
                messages, return_tensors="pt"
            ).to(device)

            # Create streamer
            streamer = TextIteratorStreamer(
                self.model_manager.tokenizer, skip_prompt=True, skip_special_tokens=True
            )

            # Get generation config
            gen_config = self.model_manager.get_generation_config()

            # Generation parameters
            generation_kwargs = {"inputs": inputs, "streamer": streamer, **gen_config}

            # Start generation thread
            thread = threading.Thread(
                target=self.model_manager.model.generate, kwargs=generation_kwargs
            )
            thread.start()

            # Stream tokens
            full_response = ""
            for token in streamer:
                if self.stop_flag:
                    break
                full_response += token
                token_callback(token)

            # Extract assistant response
            if "[/INST]" in full_response:
                assistant_response = full_response.split("[/INST]")[-1].strip()
            else:
                assistant_response = full_response.strip()

            # Call completion callback
            complete_callback(assistant_response, self.stop_flag)

        except Exception as e:
            complete_callback(f"Error: {str(e)}", True)

    def stop(self):
        """Stop current generation."""
        self.stop_flag = True
