import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(override=True)

DATABASE_NAME = os.getenv("DATABASE")
PASSWORD = os.getenv("PASSWORD")

def get_connection():
    return psycopg2.connect(
        dbname=DATABASE_NAME,
        user="postgres",
        password=PASSWORD,
        host="localhost",
        port="5432"
    )
