import streamlit as st
import psycopg2
from pandas import DataFrame
import plotly.express as px
import datetime
# from sql_templates import QUERY_TOP_DEXS, QUERY_TOP_TOKENS, \
#     QUERY_TRADING_VOLUME, QUERY_DEX_USAGE

DEX_LIST = ['AlgoFi', 'HumbleSwap', 'Pact', 'Tinyman AMM v.2']
TOKEN_LIST = [
  'PLANET','USDC','COOP','PEPE','USDT','OPUL','Yieldly', 'goETH','DEFLY'
  ]


pg_params = {
"dbname" : "streamlit_db",
"user" : "postgres",
"password" : "postgres",
"host" : "localhost",
"port" : 5432,
}
# pg_conn = psycopg2.connect(
#     dbname=pg_params["dbname"],
#     user=pg_params["user"],
#     password=pg_params["password"],
#     host=pg_params["host"],
#     port=pg_params["port"]
# )

def user_date_input(key):
  col1, col2 = st.columns(2)
  # Select boxes for start and end dates
  with col1:
    start_date = st.date_input(f'Start date', datetime.date(2023, 6, 1), key=key+"_start date")
  with col2:
    end_date = st.date_input(f'End date', datetime.date(2023, 6, 8), key=key+"_end date")

  # st.info("This app currently supports querying data between 01.06.2023 and 01.07.2023 only")

  if start_date > end_date:
      st.warning('End date must fall after start date.')

  return start_date , end_date

def execute_sql_query(query:str, params=None) -> DataFrame:
  try:
    # Connect to the PostgreSQL database
    # connection = pg_conn
    connection = psycopg2.connect(
        dbname=pg_params["dbname"],
        user=pg_params["user"],
        password=pg_params["password"],
        host=pg_params["host"],
        port=pg_params["port"]
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

def display_table(data: DataFrame):
  data.columns = [col.replace('_',' ').upper() for col in data.columns]
  styled_df = data.style.set_properties(
    **{'background-color': 'lightblue',
       'color': 'black',
       'border-color': 'white'}
    )
  st.write(styled_df)

@st.cache_data
def get_data_with_date_input(date_input, query: str):
  data = execute_sql_query(
    query=query.format(
      start_date=date_input[0],
      end_date=date_input[1]
    )
  )
  return data

def session_state_init(session_variable: str, init_value=None):
  if session_variable not in st.session_state:
    st.session_state[session_variable] = init_value