from typing import Any, List, Optional, Tuple

from pipeline.dependencies.driver.table_info import table_meta_info


class SQLQueryBuilder:
    def __init__(self, table_key: str):
        if table_key not in table_meta_info:
            raise ValueError(f"Table '{table_key}' not defined.")
        self.main_table = table_meta_info[table_key]["name"]
        self.main_columns = table_meta_info[table_key]["columns"]
        self.select_cols = [f"{self.main_table}.{col}" for col in self.main_columns]
        self.joins: list = []  # list of (join_type, table_name, on_clause)
        self.filters: list = []
        self.order_clause = ""
        self.limit_clause = ""

    def select(self, columns: List[str]):
        self.select_cols = columns
        return self

    def join(self, join_type: str, table_key: str, on_clause: str):
        """
        example
        An INNER JOIN combines rows
        from two or more tables only when they have matching values in
        the columns specified in the ON clause.
        """
        if table_key not in table_meta_info:
            raise ValueError(f"Join table '{table_key}' not defined.")
        table_name = table_meta_info[table_key]["name"]

        self.joins.append((join_type.upper(), table_name, on_clause))
        return self

    def where(self, condition: str, params: Optional[Tuple] = None):
        self.filters.append((condition, params))
        return self

    def order_by(self, clause: str):
        self.order_clause = f"ORDER BY {clause}"
        return self

    def limit(self, count: int):
        self.limit_clause = f"LIMIT {count}"
        return self

    def build_query(self) -> Tuple[str, List[Any]]:
        sql = f"SELECT {', '.join(self.select_cols)} FROM {self.main_table}"
        params: list = []

        for join_type, table_name, on_clause in self.joins:
            sql += f" {join_type} JOIN {table_name} ON {on_clause}"

        if self.filters:
            conditions = []
            for cond, param in self.filters:
                conditions.append(cond)
                if param:
                    if isinstance(param, tuple):
                        params.extend(param)
                    else:
                        params.append(param)
            sql += " WHERE " + " AND ".join(conditions)

        if self.order_clause:
            sql += f" {self.order_clause}"
        if self.limit_clause:
            sql += f" {self.limit_clause}"
        return sql, params
