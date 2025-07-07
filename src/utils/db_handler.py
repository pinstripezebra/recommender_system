from dotenv import load_dotenv
import pandas as pd
import psycopg2
import os
from psycopg2.extras import execute_values
import uuid

# Load environment variables from .env2 file
load_dotenv(dotenv_path=".env2")

class DatabaseHandler:
    """Class to handle PostgreSQL database connection and operations"""

    def __init__(self, db_url:str=os.environ.get("POST_DB_LINK")):

        """Initialize the database connection."""
        self.conn = psycopg2.connect(db_url, sslmode='require')
        self.conn.autocommit = True  # Enable autocommit mode

    def close(self):
        """Close the database connection."""
        self.conn.close()

    def create_table(self,query:str):

        """ Connect to the PostgreSQL database and a table using a user
        specified query if it doesnt already exist."""

        # Create a cursor object
        cursor = self.conn.cursor()
        # Execute a query to create a table
        cursor.execute(query)

        self.conn.commit()
        # Close the cursor and connection
        cursor.close()


    def retrieve_all_from_table(self,table_name:str):

        """ Connect to the PostgreSQL database and retrieves all data from a user specified table"""

        try:
            # Create a cursor object
            cursor = self.conn.cursor()

            # Fetch column names dynamically
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            columns = [row[0] for row in cursor.fetchall()]
            print("Columns: ", columns)
            # Execute a query to retrieve data from the table
            cursor.execute("SELECT * FROM {table_name}".format(table_name=table_name))

            # Fetch all rows from the result of the query
            rows = cursor.fetchall()
        
            # Create a DataFrame from the rows
            df = pd.DataFrame(rows, columns=columns)
            return df
        
        except Exception as e:
            print("Error retrieving data from table: ", e)
            return None

    def delete_table(self,table_name:str):

        """ Connect to the PostgreSQL database and deletes hser provided table"""

        # Create a cursor object
        cursor = self.conn.cursor()
        # Execute a query to delete the table
        cursor.execute("DROP TABLE IF EXISTS {table_name}".format(table_name=table_name))
        self.conn.commit()


    def populate_table_dynamic(self, df, table_name):
        """
        More flexible function to populate any table dynamically.
        This function constructs the INSERT query based on the DataFrame columns.
        
        Args:
            df: DataFrame containing the data to insert
            table_name: Name of the target table
        """
        if df.empty:
            print(f"DataFrame is empty, no data to insert into {table_name}")
            return
        
        try:
            # Create a cursor object
            cursor = self.conn.cursor()
            
            # Get column names from the DataFrame
            columns = list(df.columns)
            
            # Create the INSERT query dynamically
            columns_str = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            # Prepare data for insertion
            data_tuples = []
            for _, row in df.iterrows():
                # Convert each row to a tuple, handling UUID conversion if needed
                row_data = []
                for col in columns:
                    value = row[col]
                    # Convert UUID objects to strings if needed
                    if col == 'id' and hasattr(value, 'hex'):
                        row_data.append(str(value))
                    else:
                        row_data.append(value)
                data_tuples.append(tuple(row_data))
            
            # Execute the insertion
            cursor.executemany(query, data_tuples)
            self.conn.commit()
            cursor.close()
            
            print(f"Successfully populated {table_name} table with {len(df)} records using dynamic method")
            
        except Exception as e:
            print(f"Error populating {table_name} table: {e}")
            if 'cursor' in locals():
                cursor.close()

    def test_table(self, table_name: str) -> dict:
        """
        Test if a table exists and whether it contains data.
        
        Args:
            table_name: Name of the table to test
            
        Returns:
            dict: Dictionary with keys 'table_exists' and 'table_has_data' (both Boolean)
        """
        result = {
            'table_exists': False,
            'table_has_data': False
        }
        
        try:
            cursor = self.conn.cursor()
            
            # Check if table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table_name,))
            
            table_exists = cursor.fetchone()[0]
            result['table_exists'] = table_exists
            
            # If table exists, check if it has data
            if table_exists:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                row_count = cursor.fetchone()[0]
                result['table_has_data'] = row_count > 0
                
                print(f"Table '{table_name}': Exists={table_exists}, Has data={result['table_has_data']} ({row_count} rows)")
            else:
                print(f"Table '{table_name}': Does not exist")
            
            cursor.close()
            return result
            
        except Exception as e:
            print(f"Error testing table '{table_name}': {e}")
            if 'cursor' in locals():
                cursor.close()
            return result

