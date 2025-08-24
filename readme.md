# stock_pipeline

Airflow pipeline that fetches intraday stock data (Alpha Vantage) and stores it in a Postgres database running in Docker.

## Repo layout

- dags/
  - stock_pipeline.py — DAG definition
- scripts/
  - fetch_stock_data.py — API fetch + DB insert/upsert logic
- logs/ — Airflow logs (bind mount)
- docker-compose.yml — contains Postgres + Airflow services
- .env — environment variables used by docker-compose
- requirements.txt

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Docker (Desktop)
- Alpha Vantage API key.

## .env

Required variables:

- POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
- AIRFLOW_USERNAME, AIRFLOW_PASSWORD
- ALPHA_VANTAGE_API_KEY
- STOCK_SYMBOL

Include the DB URL in .env so all Airflow services receive it:  
`AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://<POSTGRES_USER>:<POSTGRES_PASSWORD>@postgres/<POSTGRES_DB>`

## Open the terminal

1. Clone the repository:

```bash
git clone https://github.com/KPDileepKumar/stock_pipeline.git
cd stock_pipeline
```

2. Create and activate virtual environment:

```bash
python -m venv envname
# On Windows:
envname\Scripts\activate
# On macOS/Linux:
source envname/bin/activate
```

## Install-dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Bring the services:

   `docker-compose up -d`

   - airflow-init performs DB migrations and creates the admin user. It exits after success.
   - airflow-webserver and airflow-scheduler will run.

4. Access Airflow UI

   - URL: http://localhost:8080
   - Login: use AIRFLOW_USERNAME / AIRFLOW_PASSWORD from .env (default in examples: admin / admin)
   - If DAGs don't appear or scheduler not scheduling:

   Ensure airflow-init completed successfully.  
   Check logs:  
   `docker-compose logs -f airflow-init`  
   `docker-compose logs -f airflow-scheduler`  
   `docker-compose logs -f airflow-webserver`  
   `docker-compose logs -f postgres`

5.

- Verify containers and port mapping  
  `docker-compose ps`
- Confirm the DB and tables exist inside the postgres container (run these — replace stock_data with your actual table name)  
  `docker-compose exec postgres psql -U admin -d postgres -c "SELECT datname FROM pg_database;"`  
  `docker-compose exec postgres psql -U admin -d stock_pipeline -c "SELECT tablename FROM pg_tables WHERE schemaname='public';"`  
  `docker-compose exec postgres psql -U admin -d stock_pipeline -c "SELECT * FROM stock_data;"`

Using pgAdmin (Desktop):

- If Docker maps Postgres host port to host (check docker-compose ps for published port), connect pgAdmin to the Docker Postgres with:

  Host: localhost
  Port: the host-mapped port (usually 5432 or 5433 depending on your compose)
  Maintenance DB: postgres
  Username: <POSTGRES_USER> (e.g. admin)
  Password: <POSTGRES_PASSWORD>
  Then expand: Servers → server → Databases → stock_pipeline → Schemas → public → Tables → stock_data → right-click → View/Edit Data → All Rows

If pgAdmin has a server with port already in use (e.g., local PostgreSQL 17), create a new server entry pointing to the Docker port.
