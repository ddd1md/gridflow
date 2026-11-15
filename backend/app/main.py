import os
from fastapi import FastAPI
import psycopg


app = FastAPI()

connection_params = {
    "host": os.environ.get("POSTGRES_HOST"),
    "port": os.environ.get("POSTGRES_PORT"),
    "dbname": os.environ.get("DB_NAME"),
    "user": os.environ.get("POSTGRES_USER"),
    "password": os.environ.get("POSTGRES_PASSWORD")
}


@app.get("/health")
def backend_health():
    return {"backend-service": "Success"}


@app.get("/health/db")
def check_database_health():
    with psycopg.connect(**connection_params) as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT current_database()""")
            database_info = cur.fetchone()

    return {"database": database_info[0]}
