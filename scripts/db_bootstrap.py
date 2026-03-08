import os
from urllib.parse import quote_plus
from sqlalchemy.engine import make_url
import psycopg2
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/gymdiet")
u = make_url(url)
db_name = u.database
admin_url = u.set(database="postgres")

conn = psycopg2.connect(str(admin_url).replace("+psycopg2", ""))
conn.autocommit = True
cur = conn.cursor()
cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (db_name,))
exists = cur.fetchone() is not None
if not exists:
    cur.execute(f'CREATE DATABASE "{db_name}"')
cur.close()
conn.close()

