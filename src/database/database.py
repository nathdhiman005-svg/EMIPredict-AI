import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import streamlit as st

# We will load credentials from st.secrets if available, fallback to os.environ.
# For Streamlit cloud, secrets are available via st.secrets.
# We default to a placeholder POSTGRES_URI to ensure no real connection is made until configured.
def get_database_url():
    try:
        # Check if running within Streamlit and if secrets exist
        if hasattr(st, "secrets") and "POSTGRES_URI" in st.secrets:
            return st.secrets["POSTGRES_URI"]
    except Exception:
        pass
        
    return os.getenv("POSTGRES_URI", "postgresql://user:password@localhost/dbname")

DATABASE_URL = get_database_url()

# SQLAlchemy setup
Base = declarative_base()

def get_engine(db_url=None):
    url = db_url if db_url else DATABASE_URL
    if url == "sqlite:///:memory:":
        from sqlalchemy.pool import StaticPool
        return create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )
    return create_engine(url, echo=False, pool_pre_ping=True, pool_recycle=300)

def get_session_maker(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
