from fastapi import APIRouter

from .endpoints import query


def build_main_router() -> APIRouter:
    """
    router.include_router(
        router=, prefix="/employees", tags=["Employees"]
    )
    """
    router = APIRouter()
    router.include_router(router=query.router, prefix="", tags=["Query paramters"])
    return router
