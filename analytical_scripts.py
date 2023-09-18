import streamlit as st
import psycopg2
from pandas import DataFrame
import plotly.express as px
import datetime

def user_date_input(
  key
  ):
  col1, col2 = st.columns(2)
  # Select boxes for start and end dates
  with col1:
    start_date = st.date_input(f'Start date', datetime.date(2023, 6, 1), key=key+"_start date")
  with col2:
    end_date = st.date_input(f'End date', datetime.date(2023, 7, 1), key=key+"_end date")

  st.info("Currently this app supports querying data between 01.06.2023 and 01.07.2023 only")

  if start_date > end_date:
      st.warning('End date must fall after start date.')

  return start_date , end_date

def execute_button(key, query, output_form:str='table'):
  if st.button("Execute", key=key):
    top_dexs_df = execute_sql_query(query=query)
    if output_form == 'table':
      display_interactive_table(data=top_dexs_df)
    elif output_form == 'line_chart':
      plot_line_chart()

def execute_sql_query(query:str, params=None) -> DataFrame:
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
    if params:
      cursor.execute(query, params)
    else:
      cursor.execute(query)

    data = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]
    cursor.close()
    connection.close()

    result = DataFrame(data=data,columns=col_names)
    result.index += 1
    return result

  except (Exception, psycopg2.Error) as error:
    st.error(f"Error executing query: {error}")
    return DataFrame()

def display_interactive_table(data: DataFrame):
  if data.empty:
    st.text("No data")
  else:
    st.dataframe(data)

def plot_line_chart(
  data:DataFrame,
  x_axis: str,
  y_axis: str,
  plot_title: str
):
  df = DataFrame(data)
  fig = px.line(df, x=x_axis, y=y_axis, title=plot_title)
  st.plotly_chart(fig)

def plot_bar_chart():
  pass