import pdfplumber
import pandas as pd


# Function to extract table from PDF
def extract_table_from_pdf(pdf_path):
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract table data
            table = page.extract_table()
            if table:
                tables.append(table)
    return tables

# Function to clean and convert extracted data to DataFrame
def tables_to_dataframe(tables):
    # Assuming the first row of the first table contains the header
    headers = tables[0][0]
    data = []

    for table in tables:
        for row in table[1:]:  # Skip the header row
            data.append(row)

    # Create DataFrame
    df = pd.DataFrame(data, columns=headers)
    return df

# Function to save DataFrame to CSV
def save_to_csv(df, output_csv_path):
    df.to_csv(output_csv_path, index=False)

# Main function
def main(pdf_path, output_csv_path):
    tables = extract_table_from_pdf(pdf_path)
    df = tables_to_dataframe(tables)
    save_to_csv(df, output_csv_path)
