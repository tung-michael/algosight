import streamlit as st
import psycopg2
import pandas as pd
from pandas import DataFrame


# Function to execute SQL query and fetch data
def execute_sql_query(query, params=None):
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
          dbname="streamlit_db",
          user="postgres",
          password="postgres",
          host="localhost",
          port=5432
        )



        # Create a cursor to execute the query
        cursor = connection.cursor()

        # Execute the query with optional parameters
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        # Fetch the result
        data = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        # Close the cursor and connection
        cursor.close()
        connection.close()
        result = pd.DataFrame(data=data,columns=col_names)
        result.index += 1
        return result

    except (Exception, psycopg2.Error) as error:
        st.error(f"Error executing query: {error}")
        return None

# Streamlit app
def main():
  st.title("Simple Algorand DeFi App")

  # User input
  user_choice = st.selectbox(
    "Select data",
    [
      "Most used applications",
      "Most often traded assets"
    ]
  )
  nr_of_rows = st.selectbox("No. of rows:", [10, 15, 20, "all"])


  # Execute the SQL query and display the result
  if st.button("Execute"):
    if user_choice == "Most used applications":
      with open("appl_usage.sql", "r") as query_file:
        query = query_file.read()
      result = execute_sql_query(query=query, params=(nr_of_rows,))
      # if result.empty:
      #   st.text("No data")
      # else:
        # st.table(result)
    elif user_choice == "Most often traded assets":
      with open("asset_usage.sql", "r") as query_file:
        query = query_file.read()
      result = execute_sql_query(query=query, params=(nr_of_rows,))
    display_interactive_table(data=result)

# [TODO] Improve front-end: make the tables more interactive?
def display_interactive_table(data: DataFrame):
  if data.empty:
    st.text("No data")
  else:
    st.dataframe(data)

def toggle_sort_order(order):
    return "asc" if order == "desc" else "desc"

if __name__ == "__main__":
  main()
  # nr_of_rows = 10
  # with open("appl_usage.sql", "r",newline='') as query_file:
  #   query = query_file.read()
  #   result = execute_sql_query(query=query, params=(nr_of_rows,))
  # print(result)
