from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def fetch_and_store_data():
    from scripts.fetch_stock_data import fetch_stock_data, store_data
    
    try:
        stock_data = fetch_stock_data()
        
        if stock_data:
            store_data(stock_data)
            print("Data successfully fetched and stored.")
        else:
            print("No data received from API.")
    except Exception as e:
        print(f"Error in fetch_and_store_data: {str(e)}")
        raise

with DAG(
    'stock_pipeline',
    default_args=default_args,
    description='A simple stock data pipeline',
    schedule_interval=timedelta(hours=1),
    catchup=False,
) as dag:

    run_pipeline = PythonOperator(
        task_id='fetch_and_store_stock_data',
        python_callable=fetch_and_store_data,
    )
    run_pipeline