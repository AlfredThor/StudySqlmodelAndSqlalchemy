from sqlmodel import create_engine, SQLModel


PGSQL_URL = 'postgresql://username:password@host:port/databasename'
engine = create_engine(PGSQL_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)