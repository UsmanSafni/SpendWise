
# SpendWise App

SpendWise is an interactive application designed to help users analyze and track their financial transactions. With SpendWise, you can upload financial data, generate visual insights, and interact with a chatbot for expense-related queries.

## Features

1. **Dashboard**:
   - Upload a new file or choose from existing files.
   - Generate and visualize analytics based on uploaded data.
   
2. **Chatbot**:
   - Ask SpendWise specific questions about your expenses.
   - Examples of supported questions:
     - "How much did I spend on groceries?"
     - "What was my biggest purchase?"
     - "Give me a summary report of my expenses."
     - "Total expenditure pls?"

3. **Custom LLM Integration**:
   - Utilizes the `tiiuae/falcon-180B-chat` model for enhanced conversational capabilities.
   - Powered by `LangChain` and `ChatOpenAI` for seamless NLP operations.

## Installation

### Prerequisites
- Python 3.8 or higher.
- Required Python libraries: `gradio`, `openai`, `langchain_openai`, and others.

### Setup
1. Clone this repository:
   ```bash
   git clone https://github.com/your-repo/spendwise.git
   cd spendwise
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the environment variables:
   - Add your API key to the environment:
     ```bash
     export AI71_API_KEY=your_api_key_here
     ```
   - On Windows, use:
     ```cmd
     set AI71_API_KEY=your_api_key_here
     ```

5. Run the app:
   ```bash
   python app.py
   ```

## Usage

1. **Launch the application**:
   Once the app is running, a Gradio interface will open in your browser.

2. **Dashboard Tab**:
   - Choose between uploading a new file or selecting an existing file.
   - Click "Submit" to generate analytics and visualize your financial data.

3. **Chat Tab**:
   - Type your questions in the input box or use one of the pre-defined sample questions.
   - Receive insights and answers from the SpendWise chatbot.

## Project Structure

```
.
├── app.py                # Main application entry point
├── apps/
│   ├── run_chain.py      # Logic for SpendWise chatbot
│   ├── upload_file.py    # File upload handling
│   └── generate_plot.py  # Plot generation logic
├── requirements.txt      # Required Python dependencies
└── README.md             # Project documentation
```

## Requirements

- `gradio`
- `openai`
- `langchain_openai`
- `os`

## Future Enhancements

- Support for additional file types.
- Advanced analytics and reporting.
- Voice-based chatbot interactions.

## License

This project is licensed under the [MIT License](LICENSE).

---

### Developed By
[Your Name](https://github.com/your-profile) - SpendWise Team
