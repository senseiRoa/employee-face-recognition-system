import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "db.sqlite3")
engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
Base = declarative_base()
