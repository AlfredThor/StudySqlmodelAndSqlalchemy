from sqlmodel import create_engine, SQLModel


PGSQL_URL = 'postgresql://postgres:Admin911$@47.106.35.207:5433/sqlmodel'
engine = create_engine(PGSQL_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)