import gradio as gr
import json
import os
from datetime import datetime
from PIL import Image
import requests
from io import BytesIO

class ModelHistory:
    def __init__(self):
        self.conversation = []
        self.current_preview = None
        self.adjustments = []
        
    def add_message(self, role, content):
        self.conversation.append({"role": role, "content": content, "timestamp": str(datetime.now())})
        
    def add_adjustment(self, adjustment):
        self.adjustments.append(adjustment)
        
    def get_full_context(self):
        return {
            "conversation": self.conversation,
            "adjustments": self.adjustments
        }

def initialize_chat():
    return ModelHistory()

def generate_preview_image(prompt):
    """
    Generate a preview image based on the text prompt.
    In production, replace this with your actual text-to-image model.
    This is a placeholder that creates a simple colored rectangle.
    """
    # Placeholder image generation
    # In production, replace this with your text-to-image model
    img = Image.new('RGB', (512, 512), 'white')
    return img

def handle_user_input(message, history):
    """
    Process user input and generate response/preview
    """
    history.add_message("user", message)
    
    # Generate preview image from the prompt
    preview_image = generate_preview_image(message)
    history.current_preview = preview_image
    
    # Generate response
    response = f"Generated preview based on: {message}\nYou can request adjustments or submit to HunYuan."
    history.add_message("assistant", response)
    
    # Update chat history
    chat_history = [[msg["content"], response] for msg in history.conversation if msg["role"] == "user"]
    
    return chat_history, preview_image, history

def handle_adjustment(adjustment, history):
    """
    Process adjustment requests and update the model
    """
    history.add_adjustment(adjustment)
    
    # Generate new preview based on adjustment
    updated_preview = generate_preview_image(adjustment)
    history.current_preview = updated_preview
    
    response = f"Applied adjustment: {adjustment}"
    history.add_message("assistant", response)
    
    return history, updated_preview

def submit_to_hunyuan(history):
    """
    Submit the final model to HunYuan for processing
    """
    context = history.get_full_context()
    
    submission_result = {
        "status": "success",
        "message": "Model submitted to HunYuan for processing",
        "tracking_id": "HY" + datetime.now().strftime("%Y%m%d%H%M%S"),
        "preview_included": True if history.current_preview else False
    }
    
    return submission_result

# Create the Gradio interface
with gr.Blocks() as app:
    gr.Markdown("# 3D Model Generation Interface")
    gr.Markdown("Enter your model description, and I'll generate a preview. You can then make adjustments or submit to HunYuan.")
    
    # Initialize state
    state = gr.State(initialize_chat)
    
    with gr.Row():
        with gr.Column(scale=1):
            # Chat interface
            chatbot = gr.Chatbot(label="Model Generation Chat")
            msg = gr.Textbox(
                label="Enter your model description or adjustment request",
                placeholder="Describe the 3D model you want to create..."
            )
            
            with gr.Row():
                clear = gr.Button("Clear Chat")
                submit_btn = gr.Button("Submit to HunYuan", variant="primary")
        
        with gr.Column(scale=1):
            # Preview area with larger size
            preview = gr.Image(label="Model Preview", height=512, width=512)
            result = gr.JSON(label="Submission Result")
    
    # Handle initial model generation
    msg.submit(
        fn=handle_user_input,
        inputs=[msg, state],
        outputs=[chatbot, preview, state]
    )
    
    # Clear chat history
    clear.click(
        lambda: ([], None, ModelHistory()),
        outputs=[chatbot, preview, state]
    )
    
    # Handle final submission
    submit_btn.click(
        fn=submit_to_hunyuan,
        inputs=[state],
        outputs=[result]
    )

# Launch the interface
if __name__ == "__main__":
    app.launch()
