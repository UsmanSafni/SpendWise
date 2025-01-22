import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class PlotGenerator:
    def __init__(self, file_mapping=None):
        """
        Initializes the PlotGenerator with a file mapping.
        :param file_mapping: Dictionary mapping months to file paths.
        """
        self.file_mapping = file_mapping or {
            "july": "./data/bank_statement_july.csv",
            "august": "./data/bank_statement_august.csv",
            "uploaded_file": "./upload_data/new_file.csv"
        }

    def _read_csv(self, file_name):
        """
        Reads a CSV file and ensures the 'Date' column is in datetime format.
        :param file_name: Path to the CSV file.
        :return: DataFrame with processed data.
        """
        try:
            data = pd.read_csv(file_name)
            data['Date'] = pd.to_datetime(data['Date'])
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f"File {file_name} not found.")
        except Exception as e:
            raise ValueError(f"Error reading file: {e}")

    def generate_plot(self, month=None):
        """
        Generates a plot based on the selected month or uploaded file.
        :param month: The month selected from the dropdown (str).
        :return: Plotly figure object.
        """
        file_name = self.file_mapping.get(month)
        if not file_name:
            raise ValueError("Invalid month selected or no file uploaded.")

        data = self._read_csv(file_name)

        # Create a subplot figure with 2 rows and 3 columns
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=(
                "Date vs Amount",
                "Total Expenditure",
                "Category-wise Amount Spent",
                "Merchant-wise Amount Spent",
                "Average Daily Spending",
                "Location-wise Amount Spent"
            ),
            specs=[[{"type": "xy"}, {"type": "indicator"}, {"type": "domain"}],  # First row
                   [{"type": "xy"}, {"type": "indicator"}, {"type": "xy"}]]  # Second row
        )

        # Plot 1: Line Graph - Date vs Amount
        fig.add_trace(
            go.Scatter(x=data['Date'], y=data['Amount'], mode='lines+markers', name='Amount'),
            row=1, col=1
        )

        # Plot 2: Total Expenditure
        total_expenditure = data['Amount'].sum()
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=total_expenditure,
                title={"text": "Total Expenditure"},
                number={"prefix": "AED:"}
            ),
            row=1, col=2
        )

        # Plot 3: Pie Chart - Category-wise Amount Spent
        category_sum = data.groupby('Category_freetext')['Amount'].sum()
        fig.add_trace(
            go.Pie(labels=category_sum.index, values=category_sum.values, name="Categories"),
            row=1, col=3
        )

        # Plot 4: Bar Chart - Merchant-wise Amount Spent
        merchant_sum = data.groupby('Merchant')['Amount'].sum()
        top_merchants = merchant_sum.sort_values(ascending=False).head(10)
        fig.add_trace(
            go.Bar(x=top_merchants.values, y=top_merchants.index, orientation='h', name='Merchants'),
            row=2, col=1
        )

        # Plot 5: Average Daily Spending
        daily_totals = data.groupby('Date')['Amount'].sum()
        average_daily_spent = daily_totals.sum()/30
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=average_daily_spent,
                title={"text": "Average Daily Spending"},
                number={"prefix": "AED:"}
            ),
            row=2, col=2
        )

        # Plot 6: Bar Chart - Location-wise Amount Spent
        location_sum = data.groupby('Location')['Amount'].sum()
        top_locations = location_sum.sort_values(ascending=False).head(10)
        fig.add_trace(
            go.Bar(x=top_locations.values, y=top_locations.index, orientation='h', name='Locations'),
            row=2, col=3
        )

        # Update layout for better spacing and aesthetics
        fig.update_layout(
            height=800, width=1400,
            title_text=f"Analytics Dashboard ({month or 'Uploaded File'})",
            title_x=0.5,
            showlegend=True,
            margin=dict(t=100, b=50, l=150, r=50)
        )
        fig.update_annotations(font_size=14, font_family="Arial")
        fig.update_layout(
            title=dict(font=dict(size=20)),
            font=dict(size=12),
        )

        return fig


if __name__ == "__main__":
    # Example usage
    plot_generator = PlotGenerator()

    # Example usage for uploaded file
    fig_uploaded = plot_generator.generate_plot(month="uploaded_file")
    fig_uploaded.show()

    # Example usage for dropdown selection
    #fig_july = plot_generator.generate_plot(month="july")
    #fig_july.show()
