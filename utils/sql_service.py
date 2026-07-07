# -*- coding: utf-8 -*-
"""
@Time ： 2026/7/6 17:30
@Auth ： 章豹
@File ：sql_service.py
@IDE ：PyCharm
@LastEditTime ： 2026/7/6 17:30
"""
import os
import pymysql
from pathlib import Path
from typing import Dict, Any


class MySQLService:
    def __init__(self, config: Dict[str, Any], sql_dir: str = r"sql_queries", port=3306):
        self.conn = pymysql.connect(
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            port=port,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        file_path = os.path.dirname(__file__).split(sep='util')
        self.sql_dir = Path(file_path[0] + sql_dir)
        self._validate_sql_dir()

    def _validate_sql_dir(self):
        if not self.sql_dir.exists():
            raise FileNotFoundError(f"SQL directory not found: {self.sql_dir}")
        if not any(self.sql_dir.glob("*.sql")):
            raise ValueError(f"No SQL files found in {self.sql_dir}")

    def _load_sql(self, query_name: str) -> str:
        sql_file = self.sql_dir / f"{query_name}.sql"
        if not sql_file.exists():
            raise FileNotFoundError(f"SQL file not found: {sql_file}")
        return sql_file.read_text(encoding='utf-8')

    def execute_query(self, query_name: str, params: Dict[str, Any] = None) -> tuple[tuple[Any, ...], ...]:
        sql = self._load_sql(query_name)
        with self.conn.cursor() as cursor:
            cursor.execute(sql, params or {})
            return cursor.fetchall()

    def execute_update(self, query_name: str, params: Dict[str, Any] = None) -> int:
        sql = self._load_sql(query_name)
        with self.conn.cursor() as cursor:
            affected_rows = cursor.execute(sql, params or {})
            self.conn.commit()
            return affected_rows

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


# if __name__ == '__main__':
#     db_config = {
#         'host': '192.168.100.35',
#         'user': 'mgmt',
#         'password': 'mgmt',
#         'database': 'mgmt_data'
#     }

    # with MySQLService(db_config) as db:
    #     # 执行查询
    #     user = db.execute_query(
    #         "get_user_by_id",
    #         {'user_uid': '001140c28f9e4e6asdd7d54bcdvferver'}
    #     )
    #     print(user)
    #     role = db.execute_query("get_user_role",
    #                             {"user_uid": "c134a92d203940d499babf1c40fb29bd",
    #                              "role_id": "1",
    #                              "name": "ceshizb"})
    #     print(role[0]['user_uid'])

    # with MySQLService(db_config) as db:
    #     # 执行查询
    #     data = db.execute_query(
    #         "cargo_acceptance_item",
    #         {'settlement_batch_data': '20260113-CMJT-CFNSB001-T7P5JQ',
    #          'logic_contract_code':'20260113-CMJT-CFNSB001'}
    #     )
    #     # print(data)
    #     instruction_id = data[0]['instruction_no']
    #     create_time_str = data[0]['create_time'].strftime('%Y/%m/%d %H:%M:%S')
    #     print(f"{instruction_id} -- {create_time_str}")
  