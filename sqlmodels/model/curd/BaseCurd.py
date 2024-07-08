from sqlmodels.tool.tool import pages
from sqlmodels.model.model import Heros
from sqlmodels.tool.tool import get_db
from sqlmodels.config.config import engine
from datetime import datetime
from sqlmodel import SQLModel, select, desc, func, and_, or_
from sqlalchemy import insert, update, delete


class HeroCurd:
    def __init__(self, model):
        self.db = get_db()
        self.model = model

    def query_(self, info):
        # 所有字段
        base_export = self.model.__fields__.keys()
        # 是否返回所有字段
        info['all_field'] = info['all_field'] if 'all_field' in info else True
        # True 输出去除该列表里面的字段 / False 输出只有该列表里面的字段
        info['reverse'] = info['reverse'] if 'reverse' in info else True

        if info['all_field']:
            info['export'] = base_export
        else:
            info['export'] = info['export'] if 'export' in info else base_export

        query = select(self.model)
        conditions = []

        # 构建查询条件
        if info.get('curd'):
            for key, value in info['curd'].items():
                conditions.append(getattr(self.model, key).like(f'%{value}%'))  # 模糊查询

        if 'start_time' in info and 'end_time' in info:
            start_time = datetime.strftime(info['start_time'], '%Y-%m-%d H:i:s')
            end_time = datetime.strftime(info['end_time'], '%Y-%m-%d H:i:s')
            conditions.append(self.model.created_at.between(start_time, end_time))

        # 应用条件
        if conditions:
            query = query.where(and_(*conditions))

        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total_count = self.db.exec(count_query).one()

        # 如果没有数据，直接返回
        if total_count == 0:
            return {'code': 404,'message': '查询成功，但没有找到匹配的数据','info': [],'pagination': {'current': info['pagination']['current'],'page_size': info['pagination']['page_size'],'total': 0}}

        # 分页
        pagination = pages.Ipagination({
            'current': info['pagination']['current'],
            'page_size': info['pagination']['page_size'],
            'total': total_count
        })

        # 应用分页和排序
        query = (query.offset((pagination['current'] - 1) * pagination['page_size']).limit(pagination['page_size']).order_by('id'))

        # 执行查询
        result = self.db.exec(query)
        db_info = result.first() if info.get('is_first') else result.all()

        # 处理查询结果为空的情况
        if db_info is None or (isinstance(db_info, list) and len(db_info) == 0):
            return {'code': 404,'message': '查询成功，但没有找到匹配的数据','info': [],'pagination': pagination}

        # 格式化结果
        if info.get('is_first'):
            formatted_info = db_info.to_dict(exclude=info['export'], reverse=info['reverse']) if db_info else {}
        else:
            formatted_info = [x.to_dict(exclude=info['export'], reverse=info['reverse']) for x in db_info]

        return {'code': 200,'message': '查询成功!','info': formatted_info,'pagination': pagination}

    def create_(self, info):
        try:
            if isinstance(info['curd'], list):
                data = []
                for item in info['curd']:
                    model_fields = {k: v for k, v in item.items() if k in self.model.__fields__.keys()}
                    data.append(model_fields)
                stmt = insert(self.model).values(data)
                result = self.db.execute(stmt)

                if info['is_commit']:
                    self.db.commit()

                    create_count = result.rowcount
                    if create_count != 0:
                        return {'code': 200, 'message': '批量添加数据成功!', 'info': f'成功新增{result.rowcount}条数据!'}

                    return {'code': 400, 'message': '批量新增有误!'}

                return {'code': 400, 'message': '参数有误!'}

            if isinstance(info['curd'], dict):
                model_fields = {k: v for k, v in info['curd'].items() if k in self.model.__fields__.keys()}
                models = self.model(**model_fields)
                self.db.add(models)
                if info['is_commit']:
                    self.db.commit()
                    self.db.refresh(models)
                    return {'code': 200, 'message': '添加数据成功!', 'info': models.to_dict()}

                return {'code': 400, 'message': '参数有误!'}

        except Exception as error:
            self.db.rollback()
            return {'code': 400, 'message': '添加数据失败!', 'info': str(error)}

    def update_(self, info):
        try:
            if isinstance(info['query'], list):
                conditions = []
                for item in info['query']:
                    for key, value in item.items():
                        if hasattr(self.model, key):
                            conditions.append(getattr(self.model, key)==value)

                # 使用 or_ 组合所有条件
                where_clause = or_(*conditions)
                update_data = {k: v for k, v in info['curd'].items() if hasattr(self.model, k)}

                # 构建更新语句
                stmt = update(self.model).where(where_clause).values(**update_data)
                result = self.db.exec(stmt)

                upd_count = result.rowcount

                if info['is_commit']:
                    self.db.commit()
                    if upd_count != 0:
                        return {'code': 200, 'message': '批量更新成功!', 'info': f'成功新增{result.rowcount}条数据!'}

                    return {'code': 400, 'message': '更新失败!'}

                return {'code': 400, 'message': '参数有有误!'}

            if isinstance(info['query'], dict):
                query_ = select(self.model)
                conditions = []
                for key, value in info['query'].items():
                    conditions.append(getattr(self.model, key)==value)  # 精确查询
                statement = query_.where(*conditions)
                result = self.db.exec(statement)
                db_info = result.first()
                if not db_info:
                    return {'code': 400, 'message': '查询不到数据!'}

                for key, value in info['curd'].items():
                    if hasattr(db_info, key):
                        setattr(db_info, key, value)

                if info['is_commit']:
                    self.db.add(db_info)
                    self.db.commit()
                    self.db.refresh(db_info)
                    return {'code': 200, 'message': '修改成功!', 'info': db_info.to_dict()}

                return {'code': 200, 'message': '参数有误!'}

        except Exception as error:
            self.db.rollback()
            return {'code': 400, 'message': '出现未知性错误!', 'info': str(error)}

    def remove_(self, info):
        try:
            if isinstance(info['curd'], list):
                conditions = []
                for item in info['curd']:
                    for key, value in item.items():
                        if hasattr(self.model, key):
                            conditions.append(getattr(self.model, key) == value)

                where_clause = or_(*conditions)
                stmt = delete(self.model).where(where_clause)
                result = self.db.execute(stmt)

                db_count = result.rowcount

                if db_count == 0:
                    return {'code': 200, 'message': '删除失败!搜索不到数据!'}
                if db_count != 0:

                    if info['is_commit']:
                        self.db.commit()
                        return {'code': 200, 'message': '删除成功!', 'info': f'成功删除了{db_count}条数据!'}

                    return {'code': 400, 'message': '参数有有误!'}

            if isinstance(info['curd'], dict):
                query_ = select(self.model)
                conditions = []
                for key, value in info['curd'].items():
                    conditions.append(getattr(self.model, key)==value)  # 精确查询
                statement = query_.where(*conditions)
                result = self.db.exec(statement)
                db_info = result.first()
                if not db_info:
                    return {'code': 400, 'message': '查询不到数据!'}

                if info['is_commit']:
                    self.db.delete(db_info)
                    self.db.commit()
                    return {'code': 200, 'message': '删除成功!'}
                else:
                    return {'code': 200, 'message': '参数有误!'}

        except Exception as error:
            self.db.rollback()
            return {'code': 400, 'message': '出现未知性错误!', 'info': str(error)}