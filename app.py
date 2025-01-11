import gradio as gr
from apps.run_chain import SpendWise
from apps.upload_file import PDFProcessor
from apps.generate_plot import PlotGenerator
import openai
from langchain_openai import ChatOpenAI
import os


class SpendWiseApp:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="tiiuae/falcon-180B-chat",
            api_key=os.getenv("AI71_API_KEY"),
            base_url="https://api.ai71.ai/v1/",
            temperature=0,
        )
        self.spendwise_instance = SpendWise()
        self.plot_generator = PlotGenerator()
        self.processor = PDFProcessor()
        self.title = "SpendWise"
        self.description = "Track Smart, Spend Wise!"
        self.demo = None

    def toggle_visibility(self, choice):
        if choice == "Upload a new file":
            return gr.update(visible=True), gr.update(visible=False)
        elif choice == "Choose from existing":
            return gr.update(visible=False), gr.update(visible=True)

    def display_sample(self, sample, dropdown):
        return sample, self.spendwise_instance.run(sample, dropdown)

    def build_interface(self):
        with gr.Blocks() as self.demo:
            gr.Markdown(f"""
            <div style="text-align: center;">  
                <h1>{self.title}</h1>
                <h2>{self.description}</h2>
            </div>
            """)

            with gr.Tabs():
                # Analytics Tab
                with gr.Tab("Dashboard"):
                    gr.Markdown("### Upload or Choose a File")
                    with gr.Row():
                        choice_button = gr.Radio(
                            choices=["Upload a new file", "Choose from existing"], label="Select Action"
                        )
                        upload_button = gr.UploadButton("Upload a new file", visible=False)
                        upload_button.upload(self.processor.upload_file, inputs=[upload_button])

                        dropdown = gr.Dropdown(
                            choices=["july", "august", "uploaded_file"],
                            label="Choose from existing",
                            visible=False,
                            interactive=True,
                        )
                        generate_plot_btn = gr.Button("Submit")

                        choice_button.change(
                            self.toggle_visibility, inputs=[choice_button], outputs=[upload_button, dropdown]
                        )

                    with gr.Row():
                        output_plot = gr.Plot(label="Analytics Dashboard")
                        generate_plot_btn.click(
                                fn=self.plot_generator.generate_plot,
                                inputs=[dropdown],  # Use the dropdown input for generating the plot
                                outputs=[output_plot],
                        )

                # Chatbot Tab
                with gr.Tab("Chat"):
                    gr.Markdown("### Ask SpendWise")
                    text_input = gr.Textbox(label="Enter text here")
                    text_output = gr.Textbox(label="Output")
                    text_button = gr.Button("Submit")
                    text_button.click(
                        fn=self.spendwise_instance.run, inputs=[text_input, dropdown], outputs=text_output
                    )

                    gr.Markdown("<h3>Sample Questions:</h3>")
                    samples = [
                        "How much did I spend on groceries?",
                        "What was my biggest purchase",
                        "Give me a summary report of my expenses",
                        "Total expenditure pls?",
                    ]

                    for sample in samples:
                        sample_button = gr.Button(sample)
                        sample_button.click(
                            fn=self.display_sample,
                            inputs=[gr.State(sample), dropdown],  # Pass sample as state and dropdown as input
                            outputs=[text_input, text_output],
                        )

    def launch(self):
        self.build_interface()
        self.demo.launch(share=True)


if __name__ == "__main__":
    app = SpendWiseApp()
    app.launch()
