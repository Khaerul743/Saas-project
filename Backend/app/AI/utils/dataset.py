import duckdb
import pandas as pd
import os
import io

def get_dataset(file_path: str, db_path:str, query: str, table_name: str = None):
    # Support both CSV and Excel files
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")
    
    # Determine table name from file path if not provided
    if table_name is None:
        table_name = file_path.split('/')[-1].split('.')[0]  # Extract filename without extension
    
    # Create directory if it doesn't exist
    if not os.path.exists(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        print("Database created")
    else:
        print("Database already exists")
    
    # Always connect and register the table with dynamic name
    connection = duckdb.connect(database=db_path)
    connection.register(table_name, df)
    
    result = connection.execute(query).df()
    connection.close()
    return result


def get_dataset_info(file_path: str, db_name: str):
    # Support both CSV and Excel files
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")
    
    # Basic information
    num_rows = len(df)
    num_cols = len(df.columns)
    
    # Column information
    columns_info = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        non_null_count = df[col].count()
        null_count = num_rows - non_null_count
        
        # Get sample values for better understanding
        sample_values = df[col].dropna().head(3).tolist()
        sample_str = ", ".join([str(val) for val in sample_values])
        
        columns_info.append(f"- **{col}** ({dtype}): {non_null_count} non-null values, {null_count} null values. Sample values: {sample_str}")
    
    # Create comprehensive description
    description = f"""Database name: **{db_name}**
Total rows: **{num_rows}**
Total columns: **{num_cols}**

**Column Details:**
{chr(10).join(columns_info)}

**Data Summary:**
- File path: {file_path}
- Memory usage: {df.memory_usage(deep=True).sum() / 1024:.2f} KB
- Duplicate rows: {df.duplicated().sum()}"""
    
    return description
if __name__ == "__main__":
    # print(get_dataset("../products.csv", "dataset/products.db", "SELECT * FROM products"))
    print(get_dataset_info("../products.csv", "products"))