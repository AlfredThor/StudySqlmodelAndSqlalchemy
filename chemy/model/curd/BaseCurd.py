from datetime import datetime
from sqlalchemy.orm import Session
from chemy.config.logger import logger
from chemy.config.config import SessionLocal
from chemy.tool.tool import get_db, Condition, pages
from sqlalchemy import func, and_, or_, desc, asc, distinct
from sqlalchemy.exc import IntegrityError, OperationalError


class Base_curd:

    def __init__(self, model):
        self.model = model
        self.db = SessionLocal()

    def query_(self, info):
        '''
            in:
                {
                    'curd':{具体搜索的字段},
                    'export': [不需要返回的字段],
                    'all_field': 是否返回所有字段,
                    'reverse': True 输出去除该列表里面的字段 / False 输出只有该列表里面的字段
                    'pagination': {
                            'current':current,  当前第几页
                            'page_size':page_size  每页多少数据
                        }
                    'is_first': True/False 单条数据或者多条分页数据,
                }
            out: {'code': '100200', 'msg': '👌', 'data':{'list':[{},{},,,],'pagination':{} } }
        '''
        conditions = []
        if 'start_time' in info and 'end_time' in info:
            start_time = datetime.strftime(info['start_time'], '%Y-%m-%d')
            end_time = datetime.strftime(info['end_time'], '%Y-%m-%d')
            conditions.append(self.model.ceeate_time.between(start_time, end_time))

        if info['curd']:
            for item in info['curd']:
                if isinstance(info['curd'][item], list):
                    conditions.append(getattr(self.model, item).in_(info['curd'][item]))
                else:
                    conditions.append(Condition(self.model).process_condition(item, info['curd'][item]))

        if not info['curd']:
            db_query = self.db.query(self.model)
        else:
            if info['query_type'] == 'or':
                db_query = self.db.query(self.model).filter(or_(*conditions))
            if info['query_type'] == 'and':
                db_query = self.db.query(self.model).filter(and_(*conditions))

        # 添加排序
        if 'group_by' in info:
            group_field = getattr(self.model, info['group_by'], None)
            if group_field:
                db_query = db_query.group_by(group_field)
                if 'sort_by' in info:
                    sort_field = getattr(self.model, info['sort_by'], None)
                    if sort_field:
                        if info.get('sort_order', 'asc') == 'desc':
                            order_direction = desc if info.get('sort_order', 'asc') == 'desc' else asc
                            db_query = db_query.order_by(order_direction(sort_field))

        # 所有的字段
        base_export = self.model.__table__.columns.keys()
        # 是否返回所有字段
        info['all_field'] = info['all_field'] if 'all_field' in info else True
        # True 输出去除该列表里面的字段 / False 输出只有该列表里面的字段
        info['reverse'] = info['reverse'] if 'reverse' in info else True

        if info['all_field']:
            info['export'] = base_export
        else:
            info['export'] = info['export'] if 'export' in info else base_export

        # 返回单条数据
        if info['is_first']:
            try:
                db_info = db_query.first() if db_query else None
                if db_info:
                    return {'code': 200, 'message': '搜索成功!',
                            'info': db_info.to_dict(exclude=info['export'], reverse=info['reverse'])}

                if db_info is None:
                    return {'code': 404, 'message': '搜索到数据为空!'}

            except OperationalError as error:

                return {'code': 404, 'message': '搜索出现未知错误!', 'info': str(error)}

        # 返回多条数据
        else:
            # 总数据量
            # 如果包含分组逻辑
            if 'group_by' in info and getattr(self.model, info['group_by'], None):
                # 计算分组后的总组数
                total_query = self.db.query(func.count(distinct(getattr(self.model, info['group_by']))))
            else:
                # 计算未分组的总数据量
                total_query = self.db.query(func.count(self.model.id))

            if conditions:
                total_query = total_query.filter(and_(*conditions))

            query_count = total_query.scalar()

            pagination = pages.iPagination({
                'current': info['pagination']['current'],
                'page_size': info['pagination']['page_size'],
                'total': query_count
            })

            db_info = db_query.offset(info['pagination']['page_size'] * (info['pagination']['current'] - 1)).limit(
                info['pagination']['page_size']).all()

            if db_info:
                return {
                    'code': 200,
                    'message': '搜索成功!',
                    'list': [i.to_dict(exclude=info['export'], reverse=info['reverse']) for i in db_info],
                    'pagination': pagination
                }
            else:
                return {'code': 404, 'message': '搜索到数据为空!', 'list': [], 'pagination': pagination}

    def create_(self, info):
        try:
            if isinstance(info['curd'], list):
                self.db.bulk_insert_mappings(self.model, info['curd'])
                count = len(info['curd'])

                if info['is_commit']:
                    self.db.commit()
                    self.db.flush()
                return {'code': 200, 'message': '新增成功!', 'info': f'新增了{count}条数据!'}

            if isinstance(info['curd'], dict):
                db_add = self.model()
                for key, value in info['curd'].items():
                    setattr(db_add, key, value)

                self.db.add(db_add)
                if info['is_commit']:
                    self.db.commit()
                    self.db.flush()
                    self.db.refresh(db_add)

                return {'code': 200, 'message': '新增成功!', 'info': db_add.to_dict()}

        except IntegrityError as error:
            self.db.rollback()
            logger.error(f'添加数据错误! 模型: {self.model} 数据: {info} 报错信息: {error}')
            return {'code': 400, 'message': '出现重复数据!', 'info': str(error)}

        except Exception as error:
            self.db.rollback()
            logger.error(f'添加数据错误! 模型: {self.model} 数据: {info} 报错信息: {error}')
            return {'code': 400, 'message': '出现未知错误! 请通知管理员!', 'info': str(error)}

    def update_(self, info):
        '''
                    in：{
                        'query:{查询的字段}
                        'curd':{里面为要增加或者更新的字段},
                        'is_commit':'是否提交'
                        }
                    out：一个增加或者更新数据后的对象
                '''
        try:
            if  isinstance(info['curd'], list):
                self.db.bulk_update_mappings(self.model, info['curd'])
                count = len(info['curd'])

                if info['is_commit']:
                    self.db.commit()
                    self.db.flush()

                return {'code': 200, 'message': '更新成功!', 'info': f'更新了{count}条数据!'}

            if isinstance(info['curd'], dict):
                query = self.db.query(self.model)
                for key, value in info['query'].items():
                    query = query.filter(getattr(self.model, key)==value)

                db_obj = query.first()
                if db_obj:
                    for key, value in info['curd'].items():
                        setattr(db_obj, key, value)

                    if info['is_commit']:
                        self.db.commit()
                        self.db.flush()
                        self.db.refresh(db_obj)
                    return {'code': 200, 'message': '更新成功!', 'info': db_obj.to_dict()}

                else:
                    return {'code': 404, 'message': '查询参数有错,查询不到数据!'}

        except Exception as error:
            self.db.rollback()
            logger.info(f'更新数据错误! 模型: {self.model} 数据: {info} 报错信息: {error}')
            return {'code': 400, 'message': '出现错误,请联系管理员!', 'info': str(error)}


    def remove_(self, info):
        '''
            删除操作
            in: {
                'curd':{}
                'is_commit': '是否提交'
                }
            out: 一个删除后的数据对象
        '''
        try:
            if isinstance(info['curd'], list):
                conditions = []
                for condition in info['curd']:
                    filters = [getattr(self.model, key) == value for key, value in condition.items()]
                    conditions.append(and_(*filters))

                delete_criteria = self.db.query(self.model).filter(or_(*conditions))
                delete_count = delete_criteria.delete(synchronize_session=False)
                if info['is_commit']:
                    self.db.commit()
                    return {'code': 200, 'message': '删除成功!', 'info': f'删除了{delete_count}条数据!'}

                return {'code': 404, 'message': '参数有误!'}

            if isinstance(info['curd'], dict):
                query = self.db.query(self.model)
                for key, value in info['curd'].items():
                    query = query.filter(getattr(self.model, key) == value)

                db_del = query.first()
                if db_del:
                    info['is_commit '] = info['is_commit'] if 'is_commit' in info else False
                    if info['is_commit']:
                        self.db.delete(db_del)
                        self.db.commit()
                        self.db.flush()
                    return {'code': 200, 'message': '删除成功!'}
                else:
                    return {'code': 404, 'message': '查询不到要删除的数据!'}

        except Exception as error:
            self.db.rollback()
            logger.info(f'删除数据错误! 模型: {self.model} 数据: {info} 报错信息: {error}')
            return {'code': 400, 'message': '出现错误,请联系管理员!', 'info': str(error)}
