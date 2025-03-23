from pydantic import BaseModel


class DBConfig(BaseModel):
    """
    handles secrets retrieval from enviroment variables
    DBConfig should be passed to the database driver on construction
    Values are hardcoded now but they should be passed as environment variables to the pod
    """

    database: str = "myDB"
    username: str = "myUser"
    password: str = "myPassword"
    localhost: str = (
        "localhost"  # when ran in docker this refers to postgres service name
    )
    compose_address: str = (
        "db"  # when ran in docker this refers to postgres service name
    )
    local_port: str = "3500"  # postgres default port exposed on localhost
    compose_port: str = "5432"  # postgres default port exposed on compose network
    use_secrets: bool = False

    def get_compose_connection_pool_address(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.compose_address}:{self.compose_port}/{self.database}"

    def get_localhost_connection_pool_address(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.localhost}:{self.local_port}/{self.database}"
