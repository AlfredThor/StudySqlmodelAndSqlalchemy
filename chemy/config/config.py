from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,scoped_session, declarative_base


PGSQL_URL= 'postgresql://postgres:Admin911$@47.106.35.207:5433/chemy'

# 声明ORM基类（这个基类的子类会自动和数据库表进行关联）
Base = declarative_base()
# 引擎：也就是实体数据库连接. 生产环境为: SQLALCHEMY_MYSQL_URL, 开发环境为: CHECK_SQLALCHEMY_MYSQL_URL
engine = create_engine(PGSQL_URL,pool_recycle=3600,future=True,connect_args={'connect_timeout': 30})
DBSession = scoped_session(sessionmaker())
DBSession.configure(bind=engine, autoflush=False, expire_on_commit=False)
# 创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
