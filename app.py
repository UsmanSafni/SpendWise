import gradio as gr
from apps.run_chain import run_chain
from apps.upload_file import upload_file
from apps.upload_file import generate_sqldb
import openai
from langchain_openai import ChatOpenAI
import os


#initialise OpenAI client
openai.api_key =os.getenv("OPENAI_API_KEY")
llm=ChatOpenAI( model="tiiuae/falcon-180B-chat",
    api_key= os.getenv("AI71_API_KEY"),
    base_url="https://api.ai71.ai/v1/",
    temperature=0,
    )


# Define a function to handle uploaded files
# Define a function to handle uploaded files
# Define a function to handle uploaded files and save them to './data'

generate_sqldb()
        
# Define your Gradio interface
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

    with gr.Tab("File Upload"):
        upload_button =gr.UploadButton("click to upload")
        upload_button.upload(upload_file,upload_button)
    demo.launch(share=True)
