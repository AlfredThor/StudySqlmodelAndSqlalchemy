import math
from contextlib import contextmanager
from chemy.config.config import SessionLocal
from sqlalchemy import Integer, String, func


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



class Condition:
    '''
        如果数据表中有Integet字段,将其转换为String字段,主要针对postgres数据库
    '''
    def __init__(self, model):
        self.model = model

    def process_condition(self, attr, value):
        if isinstance(value, str):
            return getattr(self.model, attr).ilike(f"%{value}%")
        elif isinstance(value, int) and isinstance(getattr(self.model, attr).type, Integer):
            return func.cast(getattr(self.model, attr), String).ilike(f"%{str(value)}%")
        else:
            return getattr(self.model, attr) == value


class Page:
    def iPagination(self, data):
        total = int(data['total'])
        page_size = int(data['page_size'])
        current = int(data['current'])
        total_pages = int(math.ceil(total / page_size))
        total_pages = total_pages if total_pages > 0 else 1

        ret = {
            "start": page_size * (current - 1) if current > 1 else 1,
            "current": current,  # 当前页
            "total_pages": total_pages,  # 总页数
            "page_size": page_size,  # 每页多少数据
            "total": total  # 总数据数
        }
        return ret


pages = Page()