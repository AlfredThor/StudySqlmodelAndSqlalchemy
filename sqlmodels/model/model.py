from datetime import datetime
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func


class Basemodel(SQLModel):
    create_time: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now()))
    update_time: datetime = Field(sa_column=Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now()))

    def to_dict(self, exclude=[], reverse=True, time_=True):
        '''
        reverse=True: not in exclude：输出去除该列表里面的字段
        reverse=False: in exclude：输出只有该列表里面的字段
        '''
        if reverse:
            data = {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in exclude}
        else:
            if time_:
                exclude = exclude + ['create_time', 'update_time']
            data = {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name in exclude}

        if time_:
            data['create_time'] = data['create_time'].strftime('%Y-%m-%d %H:%M:%S') if data['create_time'] else ''
            data['update_time'] = data['update_time'].strftime('%Y-%m-%d %H:%M:%S') if data['update_time'] else ''

        return data


class Heros(Basemodel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: int | None = None