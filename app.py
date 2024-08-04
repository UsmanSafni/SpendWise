import gradio as gr
from apps.run_chain import run_chain
from apps.upload_file import upload_file
from apps.upload_file import generate_sqldb
import openai
from langchain_openai import ChatOpenAI
import os

#initilise llm
llm = ChatOpenAI(
    model="tiiuae/falcon-180B-chat",
    api_key=os.getenv("AI71_API_KEY"),
    base_url="https://api.ai71.ai/v1/",
    temperature=0,
)

# Generate SQLite database
generate_sqldb()

# Define Gradio interface
title = "SpendWise"
description = "Ask me anything about your spendings!"

with gr.Blocks() as demo:
    gr.Markdown(f"""
    <div style="text-align: center;">
        <h1>{title}</h1>
        <p>{description}</p>
    </div>
    """)

    with gr.Tab("Text Input"):
        text_input = gr.Textbox(label="Enter text here")
        text_output = gr.Textbox(label="Output")
        text_button = gr.Button("Submit")
        text_button.click(fn=run_chain, inputs=text_input, outputs=text_output)

        gr.Markdown("<h3>Sample Questions:</h3>")
        samples = [
        "How much did I spend on groceries?",
        "What was my biggest purchase",
        "Give me a summary report of my expenses",
        "Total expenditure pls?"
    ]

        def display_sample(sample):
            return sample, run_chain(sample)

        for sample in samples:
            sample_button = gr.Button(sample)
            sample_button.click(fn=lambda x=sample: display_sample(x), inputs=[], outputs=[text_input, text_output])

    with gr.Tab("File Upload"):
        upload_button = gr.UploadButton("Click to upload")
        upload_button.upload(upload_file, upload_button)



demo.launch(share=True)

