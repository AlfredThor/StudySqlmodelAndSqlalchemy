import math
from sqlmodels.config.config import engine
from sqlmodel import Session, SQLModel

def get_db():
    return Session(engine)


def create_db_and_tables():
    '''创建数据表'''
    SQLModel.metadata.create_all(engine)


class Page:
    def Ipagination(self, data):
        total = int(data['total'])
        page_size = int(data['page_size'])
        current = int(data['current'])
        total_pages = int(math.ceil(total / page_size))
        total_pages = total_pages if total_pages > 0 else 1

        ret = {
            "start": (page_size * (current - 1)) + 1 if current > 1 else 1,
            "current": current,  # 当前页
            "total_pages": total_pages,  # 总页数
            "page_size": page_size,  # 每页多少数据
            "total": total  # 总数据数
        }
        return ret


pages = Page()