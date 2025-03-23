from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from pipeline.pods.asi_api.api_query_model import ApiQueryModel
import datetime
router = APIRouter()

@router.get(path="/query_data")
async def query_data(request: Request, query: ApiQueryModel) -> JSONResponse:

    app_state = request.app
    app_state.state.db_driver.logger.info(f"received query model: {query.model_dump()}")
    result = query.get_query()
    query_statement = result[0]
    params = result[1]
    results = await app_state.state.db_driver.query_data(query=query_statement,params=params)
    serialized_results = [serialize_row(row) for row in results]
    response = {
        "result":serialized_results
    }
    return JSONResponse(content=response,status_code=200)

def serialize_row(row):
    return [
        item.isoformat() if isinstance(item, datetime.datetime) else item
        for item in row
    ]


