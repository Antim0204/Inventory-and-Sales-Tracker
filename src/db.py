# src/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

def init_engine(db_url: str):
    # future=True is default in SA 2.x; echo can be toggled via env later
    engine = create_engine(db_url, pool_pre_ping=True)
    return engine

def init_session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def session_scope(session_factory):
    session = session_factory()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
