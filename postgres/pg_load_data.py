
import psycopg2
import configparser

PG_CONFIG = 'setup/database.ini'

def pg_parameters_extract (filename: str) -> dict:
  config = configparser.ConfigParser()
  config.read(filename)
  pg_params = {}
  if config.has_section(section='postgresql'):
    config_pg = config['postgresql']
    try:
      pg_params["dbname"] = config_pg["dbname"]
      pg_params["user"] = config_pg["user"]
      pg_params["password"] = config_pg["password"]
      pg_params["host"] = config_pg["host"]
      pg_params["port"] = config_pg["port"]
    except KeyError as e:
      print(e)
  else:
    raise ValueError(f'Section postgresql not found in the {filename} file.')
  return pg_params


def populate_new_table(data_file: str, table_name: str, db_cursor):
  with open(data_file,"r", newline="") as f:
    next(f) # Skip the header row
    db_cursor.copy_from(file=f, table=table_name,sep=',')

def load_data_to_pg(data_table_dict: dict):
  pass

if __name__ == '__main__':
  # load_data_to_pg()
  pg_params = pg_parameters_extract(PG_CONFIG)
  conn = psycopg2.connect(
      dbname=pg_params["dbname"],
      user=pg_params["user"],
      password=pg_params["password"],
      host=pg_params["host"],
      port=pg_params["port"]
  )
  cursor = conn.cursor()

# Example of populate table token_prices on PostgreSQL
  populate_new_table(
    data_file="tokens_prices.csv",
    table_name="token_prices",
    db_cursor=cursor
    )


  conn.commit()
  conn.close()
