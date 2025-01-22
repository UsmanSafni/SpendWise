import requests
import json
import pandas as pd
from dotenv import load_dotenv
import os
import sqlite3
import shutil
import pdfplumber
import logging
import re

class PDFProcessor:
    def __init__(self, db_path='expenses.db'):
        """
        Initialize the PDFProcessor.

        Args:
            db_path (str): Path to the SQLite database.
        """
        self.db_path = db_path
        load_dotenv()

    @staticmethod
    def extract_table_from_pdf(pdf_path):
        """
        Extract tables from a PDF file and save them as a CSV file.

        Args:
            pdf_path (str): The path to the PDF file.

        Returns:
            str: The path to the saved CSV file.
        """
        try:
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            directory = os.path.dirname(pdf_path)
            csv_file_path = os.path.join(directory, f"{base_name}.csv")

            with pdfplumber.open(pdf_path) as pdf:
                all_tables = []
                for page in pdf.pages:
                    tables = page.extract_tables()
                    if tables:
                        all_tables.extend(tables)

            if not all_tables:
                logging.warning(f"No tables found in the PDF file: {pdf_path}")
                return ""

            df_list = [pd.DataFrame(table[1:], columns=table[0]) for table in all_tables if table]
            final_df = pd.concat(df_list, ignore_index=True)
            final_df.to_csv(csv_file_path, index=False)
            logging.info(f"Tables extracted and saved to '{csv_file_path}'.")
            return csv_file_path

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return ""

    @staticmethod
    def parse_transactions(df):
        """
        Parse and clean transaction data from a DataFrame.

        Args:
            df (pd.DataFrame): DataFrame containing transaction data.

        Returns:
            pd.DataFrame: Cleaned and parsed DataFrame.
        """
        df = df.rename(columns={'Date': 'Date0'})
        df = df.dropna(how='all')
        df['Description'] = df['Description'].str.replace('\n', ' ')
        uae_cities = ['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 'Ras Al Khaimah', 'Fujairah', 'Umm Al Quwain', 'Al Ain']

        def extract_city_name(name):
            for city in uae_cities:
                if city.lower() in name.lower():
                    return city
            return ''

        def replace_ignore_case(original_str, old_substr, new_substr):
            pattern = re.compile(re.escape(old_substr), re.IGNORECASE)
            return pattern.sub(new_substr, original_str)

        def parse_transaction(transaction):
            pattern_card = re.compile(r'CARD NO\.(\d+\*{8}\d{4}) (.+):([A-Z]{2}) (\d+) (\d{2}-\d{2}-\d{4}) ([\d\.]+),([A-Z]+)')
            pattern_ipi = re.compile(r'IPI TT REF: (\w+) ([^\d\s]+ [^\d\s]+ [^\d\s]+) (.+)$')

            card_match = pattern_card.search(transaction)
            ipi_match = pattern_ipi.search(transaction)

            if card_match:
                merchant_and_city = card_match.group(2).strip()
                city = extract_city_name(merchant_and_city)
                merchant = replace_ignore_case(merchant_and_city, city, "")
                return {
                    "Card Number": card_match.group(1),
                    "Merchant": merchant,
                    "Location": city,
                    "Country Code": card_match.group(3).strip(),
                    "Transaction ID": card_match.group(4),
                    "Date": card_match.group(5),
                    "Amount": card_match.group(6),
                    "Currency": card_match.group(7)
                }
            elif ipi_match:
                return {
                    'Card Number': None,
                    'Merchant': None,
                    "Location": None,
                    "Country Code": None,
                    "Transaction ID": None,
                    'Date': None,
                    'Amount': None,
                    'Currency': None,
                    'Reference': ipi_match.group(1),
                    'Details': ipi_match.group(2)
                }
            return {
                'Card Number': None,
                'Merchant': None,
                "Location": None,
                "Country Code": None,
                "Transaction ID": None,
                'Date': None,
                'Amount': None,
                'Currency': None,
                'Reference': None,
                'Details': None
            }

        df_parsed = df['Description'].apply(parse_transaction).apply(pd.Series)
        df_final = pd.concat([df, df_parsed], axis=1)
        df_final['Date'] = pd.to_datetime(df_final['Date'], dayfirst=True)
        df_final['Amount'] = pd.to_numeric(df_final['Amount'])
        df_final.fillna({'Debits': 0, 'Credits': 0, 'Balance': 0, 'Amount': 0}, inplace=True)
        df_final.dropna(how='all', inplace=True)
        df_final.dropna(subset=['Merchant'], inplace=True)

        return df_final[['Merchant', 'Location', 'Date', 'Amount']]

    @staticmethod
    def find_first_match(text, categories):
        """
        Find the first category match in text.

        Args:
            text (str): Input text.
            categories (list): List of categories.

        Returns:
            str: Matched category or None.
        """
        for category in categories:
            if category in text.lower():
                return category
        return None

    def classify_company(self, user_content):
        """
        Classify company names using an AI API.

        Args:
            user_content (str): Company names as input.

        Returns:
            dict: Mapping of company names to categories.
        """
        url = "https://api.ai71.ai/v1/chat/completions"
        AI71_TOKEN = os.getenv("AI71_API_KEY")

        categories = [
            'fitness', 'groceries', 'restaurants and cafes', 'healthcare', 'clothing', 'jewelry',
            'transportation', 'phone and internet', 'miscellaneous', 'others', 'e-commerce', 'food delivery'
        ]
        categories_str = ', '.join(categories)

        role_content = (
            f"You will be provided with company names, and your task is to classify them to one of the following "
            f"{categories_str}. Return them formatted as JSON where the field is the company name and the value is the category."
        )

        payload = json.dumps({
            "model": "tiiuae/falcon-180b-chat",
            "messages": [
                {"role": "system", "content": role_content},
                {"role": "user", "content": user_content}
            ]
        })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {AI71_TOKEN}'
        }

        response = requests.post(url, headers=headers, data=payload)
        try:
            response_json = response.json()
            choices = response_json.get('choices', [])
            if choices:
                return json.loads(choices[0].get('message', {}).get('content', '{}'))
        except ValueError:
            pass
        return {}

    def generate_sqldb(self, file_path):
        """
        Process a PDF file and store the data in an SQLite database.

        Args:
            file_path (str): Path to the PDF file.
        """
        csv_path = self.extract_table_from_pdf(file_path)
        if not csv_path:
            logging.error("No CSV generated from the PDF file.")
            return

        df = pd.read_csv(csv_path)
        df = self.parse_transactions(df)
        merchants = df.Merchant.drop_duplicates()
        merchants_str = ', '.join(merchants)
        category_map = self.classify_company(merchants_str)
        categories = [
            'fitness', 'groceries', 'restaurants and cafes', 'healthcare', 'clothing', 'jewelry',
            'transportation', 'phone and internet', 'miscellaneous', 'others', 'e-commerce', 'food delivery'
        ]

        df['Merchant'] = df['Merchant'].str.strip().str.lower()
        category_map = {k.lower(): v for k, v in category_map.items()}
        df['Category_freetext'] = df['Merchant'].map(category_map)
        df['Category'] = df['Category_freetext'].apply(lambda x: self.find_first_match(x, categories))

        cols = df.columns.to_list() + ['Category']
        df.to_csv(csv_path)

        conn = sqlite3.connect(self.db_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        df.to_sql(base_name, conn, if_exists='replace', index=False)
        conn.commit()
        conn.close()

    def upload_file(self, file_path, new_file_name="new_file.pdf"):
        """
        Upload a file, rename it, and process it.

        Args:
            file_path (str): Path to the file.
            new_file_name (str): New file name.
        """
        save_dir = "./upload_data"
        os.makedirs(save_dir, exist_ok=True)
        target_path = os.path.join(save_dir, new_file_name)
        shutil.copy(file_path, target_path)
        self.generate_sqldb(target_path)

# Example usage:
if __name__ == "__main__":
    processor = PDFProcessor()
    processor.upload_file("./data/bank_statement_july.pdf")
    
