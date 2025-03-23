from pipeline.dependencies.driver.query_builder import SQLQueryBuilder

from pydantic import BaseModel
class ApiQueryModel(BaseModel):
    main_table: str
    where: str
    params: tuple
    order_by: str
    limit: int

    def get_query(self) -> tuple:
        qb = SQLQueryBuilder(self.main_table)
        results = (
            qb.where(self.where, (self.params))
            .order_by(self.order_by)
            .limit(self.limit)
            .build_query()
        )
        return results
