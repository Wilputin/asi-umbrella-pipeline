from pydantic import BaseModel

from pipeline.dependencies.driver.query_builder import SQLQueryBuilder

attribute_list = ["select", "join", "where", "order_by", "limit"]


class ApiJoin(BaseModel):
    join_type: str
    table: str
    on_clause: str


class ApiQueryModel(BaseModel):
    main_table: str
    select: list[str] | None = None
    join: ApiJoin | None = None
    where: str | None = None
    params: tuple | None = None
    order_by: str | None = None
    limit: int | None = None

    def get_query(self) -> tuple:
        qb = SQLQueryBuilder(self.main_table)
        model_dict = self.model_dump()
        for at in attribute_list:
            value = model_dict[at]
            if value is None:
                continue
            if at == "select":
                qb.select(self.select)
            if at == "join":
                qb.join(self.join.join_type, self.join.table, self.join.on_clause)
            if at == "where":
                qb.where(self.where, (self.params))
            if at == "order_by":
                qb.order_by(self.order_by)
            if at == "limit":
                qb.limit(self.limit)

        results = qb.build_query()
        return results
