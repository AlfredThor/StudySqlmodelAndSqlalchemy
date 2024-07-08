from datetime import datetime
from chemy.config.config import Base
from sqlalchemy import Column, Integer, String, DateTime


class BaseModel(object):
    create_time = Column(DateTime, default=datetime.now())
    update_time = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

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



class Auth(BaseModel, Base):
    __tablename__ = 'auths'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(15), nullable=False)
    last_name = Column(String(15), nullable=True)
    age = Column(Integer, nullable=True)