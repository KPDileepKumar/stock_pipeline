import os
import requests
import psycopg2
from datetime import datetime
from airflow.providers.postgres.hooks.postgres import PostgresHook

def fetch_stock_data():
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    symbol = os.getenv('STOCK_SYMBOL', 'IBM')
    
    if not api_key:
        raise ValueError("API key not found in environment variables")
    
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=60min&apikey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        time_series = data.get("Time Series (60min)", {})
        if not time_series:
            print("No time series data found in API response")
            return None
            
        latest_timestamp = sorted(time_series.keys())[-1]
        latest_data = time_series[latest_timestamp]
        
        return {
            'symbol': symbol,
            'timestamp': latest_timestamp,
            'open': float(latest_data['1. open']),
            'high': float(latest_data['2. high']),
            'low': float(latest_data['3. low']),
            'close': float(latest_data['4. close']),
            'volume': int(latest_data['5. volume']),
            'fetched_at': datetime.now().isoformat()
        }
        
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {str(e)}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {str(e)}")
        return None

def store_data(stock_data):
    conn = psycopg2.connect(
        dbname=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        host="postgres",
        port=5432)
    cursor = conn.cursor()
    
    try:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS stock_data (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            open DECIMAL(10, 4) NOT NULL,
            high DECIMAL(10, 4) NOT NULL,
            low DECIMAL(10, 4) NOT NULL,
            close DECIMAL(10, 4) NOT NULL,
            volume BIGINT NOT NULL,
            fetched_at TIMESTAMP NOT NULL,
            UNIQUE (symbol, timestamp)
        );
        """
        cursor.execute(create_table_query)
        
        insert_query = """
        INSERT INTO stock_data (symbol, timestamp, open, high, low, close, volume, fetched_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (symbol, timestamp) DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            volume = EXCLUDED.volume,
            fetched_at = EXCLUDED.fetched_at;
        """
        
        cursor.execute(insert_query, (
            stock_data['symbol'],
            stock_data['timestamp'],
            stock_data['open'],
            stock_data['high'],
            stock_data['low'],
            stock_data['close'],
            stock_data['volume'],
            stock_data['fetched_at']
        ))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Database operation failed: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()