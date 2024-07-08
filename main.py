from datetime import datetime
from sqlmodels.model.model import Heros
from sqlmodels.model.curd.BaseCurd import HeroCurd
from sqlmodels.tool.tool import create_db_and_tables

from chemy.model import model
from chemy.model.model import Auth
from chemy.tool.tool import get_db
from chemy.model.curd.BaseCurd import Base_curd as chemy_curd
from chemy.config.config import engine


def sql_model_main():
    # 创建数据表
    # create_db_and_tables()

    # 初始化CURD类
    option = HeroCurd(Heros)

    que = option.query_({
        'curd': False,
        'export': ['secret_name'],
        'all_field': False,
        'reverse': True,
        'is_first': False,
        'pagination': {
            'current': 8,
            'page_size': 10,
        }
    })
    print(que)
    # print(que['code'])
    # for i in que['info']:
    #     print(i)
    print(que['pagination'])
    # print(datetime.now() - start_time)

    # add_list = [{'name': 'Jack'+str(i), 'secret_name': 'Thor'+str(i), 'age': i} for i in range(99)]
    # add = option.create_({'curd': add_list, 'is_commit': True})
    # print(add)

    # add = option.create_({'curd':{'name': '侯启胜7', 'secret_name': '陈刚7', 'age': 29},'is_commit': True})
    # print(add)

    # upd_first = option.update_({'query': {'id': 100},'curd': {'name': 'Jack'},'is_commit': True})
    # print(upd_first)

    # upd = option.update_({
    #     'query': [{'id': 1},{'id': 2},{'id': 3}],
    #     'curd': {'age': 55},'is_commit': True})
    # print(upd)

    # rem = option.remove_({'curd': {'id': 101},'is_commit': True})
    # print(rem)

    # rem_list = option.remove_({
    #     'curd': [{'id': 102},{'id': 103},{'id': 104},{'id': 105},],
    #     'is_commit': True,
    # })
    # print(rem_list)


def sqlalchemy_main():
    # 创建数据表
    # model.Base.metadata.create_all(bind=engine)

    start_time = datetime.now()

    # 初始化CURD类
    option = chemy_curd(Auth)

    query = option.query_({
        'curd': False,
        'is_first': False,
        'export': [],
        'all_field': True,
        'reverse': False,
        'group_by': 'id',
        'sort_by': 'id',
        'sort_order': 'asc',
        'pagination': {
            'current': 2,
            'page_size': 40
        }
    })
    print(query)
    print(query['pagination'])

    print(datetime.now() - start_time)
    # lists = [{'first_name': '侯启胜'+str(i), 'last_name': 'Jane'+str(i), 'age': i} for i in range(92)]
    # add = option.create_({
    #     'curd': lists,
    #     'is_commit': True,
    # })
    # print(add)

    # update = option.update_({
    #     'query': {'id': 1},
    #     'curd': [
    #         {'id': 2, 'first_name': '侯启胜'},
    #         {'id': 3, 'first_name': '侯启胜'},
    #         {'id': 4, 'first_name': '侯启胜'},
    #         {'id': 5, 'first_name': '侯启胜'},
    #         {'id': 6, 'first_name': '侯启胜'},
    #         {'id': 16, 'first_name': '侯启胜'},
    #     ],
    #     'is_commit': True,
    # })
    # print(update)

    # del_ = option.remove_({
    #     'curd': [
    #         {'id': 13},
    #         {'id': 14, 'first_name': 'Ella1'},
    #         {'id': 15},
    #     ],
    #     'is_commit': True
    # })
    # print(del_)


if __name__ == "__main__":
    # Sqlmodel
    sql_model_main()

    # Sqlalchemy
    # sqlalchemy_main()
