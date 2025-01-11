import os
import re
from dotenv import load_dotenv
from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.utilities import SQLDatabase

class SpendWise:
    def __init__(self, db_path="sqlite:///expenses.db", model="tiiuae/falcon-180B-chat"):
        load_dotenv()
        self.api_key = os.getenv("AI71_API_KEY")
        self.db = SQLDatabase.from_uri(db_path)
        self.llm = ChatOpenAI(
            model=model,
            api_key=self.api_key,
            base_url="https://api.ai71.ai/v1/",
            temperature=0,
        )
        self.file_mapping = {
            "july": "bank_statement_july",
            "august": "bank_statement_august",
            "september": "bank_statement_sep",
            "uploaded_file": "new_file"
        }

    @staticmethod
    def clean_sql_query(query):
        """Cleans the SQL query by truncating everything after the first semicolon."""
        cleaned_query = re.split(r';\s*', query)[0] + ';'
        return cleaned_query.strip()

    def generate_sql_query(self, question, table_name):
        """Generates a SQL query using the LLM based on the user's question."""
        table = self.file_mapping.get(table_name)
        if not table:
            raise ValueError(f"Invalid table name: {table_name}")

        template = f"""
        You are an intelligent MySQL chatbot and your name is SpendWise who will talk about expense history. Help the following question with a brilliant answer. Get the expense data from SQL database named 'expenses'.
        Use the table "{table}" with these columns:
        Merchant, Location, Date, Amount, Category_freetext, Category. 
        Categories include: fitness, groceries, restaurants and cafes, healthcare, clothing, jewelry, transportation, phone and internet, miscellaneous, others, e-commerce, food delivery.
        - Provide SQL queries based only on the 'Category_freetext' column.
        - For summaries, provide the total expense for each category in descending order.
        - For totals, calculate the sum of all categories.
        - For comparisons, provide results for all mentioned categories in the order specified.
        - For specific items, group all relevant categories (e.g., 'food' includes food delivery, groceries, restaurants and cafes).
        Do not append any characters or explain the SQL query.
        Question:{{question}}
        Answer:"""

        prompt = PromptTemplate(template=template, input_variables=['question'])
        llm_chain = LLMChain(prompt=prompt, llm=self.llm)
        response = llm_chain.invoke(question)

        if isinstance(response["text"], str):
            return self.clean_sql_query(response["text"])
        else:
            raise ValueError("Invalid response from LLM.")

    def execute_query(self, query):
        """Executes a SQL query and returns the result."""
        try:
            result = self.db.run(query)
            return result if result else "No contents to share at the moment."
        except Exception as e:
            return f"Error executing query: {e}"

    def generate_answer(self, question, result):
        """Generates an answer using the LLM based on the SQL result."""
        system_message = SystemMessage(content="""
        You are an expense assistant and your name is SpendWise. Given the following user question and the corresponding SQL result, answer the user question based on the data present in SQL result and ignore what you are not provided with. If The result info appears to be an empty tuple, just say that the user has not made any expense. The currency used is AED. If you are asked to get the summary report, get the list of expenses corresponding to each category from SQL result and provide only that in the answer. You must not compute total sum at your end. If user is asking any other questions, give tricky and intelligent responses.""")

        human_message = HumanMessage(content=f"""
        Question: {question}
        SQL Result: {result}
        Answer:
        """)

        response = self.llm.invoke([system_message, human_message])
        return response.content

    def run(self, question, table_name):
        """Runs the complete chain to generate the final answer."""
        sql_query = self.generate_sql_query(question, table_name)
        result = self.execute_query(sql_query)
        final_answer = self.generate_answer(question, result)
        return final_answer

if __name__ == "__main__":
    spendwise_instance = SpendWise()  # Create an instance of SpendWise
    result = spendwise_instance.run("Total expenditure", "july")  # Call the `run` method
    print(result)  # Print the result
