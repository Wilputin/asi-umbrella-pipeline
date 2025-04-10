from fastapi import FastAPI
from starlette.datastructures import State
from uvicorn import Config, Server

from pipeline.dependencies.base_app.base_app import BaseApp
from pipeline.dependencies.driver.db_driver import DbDriver
from pipeline.pods.asi_api.router.router import build_main_router

fast_api_config = dict(port=5000, host="0.0.0.0")


class AppState(State):
    db_driver: DbDriver


class ApiApp(BaseApp):
    app: FastAPI
    app_state: AppState
    fast_api_config: dict

    async def on_init(self) -> None:
        db_driver = DbDriver(
            logger=self.logger, connection_config=self.connection_config
        )
        app_state = AppState()
        app_state.db_driver = db_driver
        self.fast_api_config = fast_api_config
        self.app = FastAPI()
        self.app.state = app_state
        router = build_main_router()
        self.app.include_router(router)
        config = Config(app=self.app, **self.fast_api_config)
        server = Server(config)
        self.logger.info("starting server to serve")
        await server.serve()
        self.running = True

    async def run(self):
        while self.running:
            pass
